"""DBに保存済みのアクティビティから、直近7日間・直近28日間のランニングのみの
合計距離・合計時間を集計する（F-03）。Garmin通信は行わない。

docs/08_詳細設計.md `summary.py` 節。
"""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Activity
from app.schemas import ActivitySummaryOut, RunningSummary

# 【暗黙の前提】この集計は「DBに既に同期済みのデータ」のみを対象とする（Garmin通信は
# 行わない）。config.pyのsync_lookback_daysが28日未満に設定されている場合、
# 直近28日間サマリーは実際には過去sync_lookback_days日分しか同期されていない
# データを対象に集計されるため、28日間全体を正しく反映しない
# （＝未同期期間を含んだ不完全な集計になりうる）。config.py側のコメントと合わせて参照。


def _sum_running(db: Session, start: datetime, end: datetime) -> RunningSummary:
    stmt = select(
        func.coalesce(func.sum(Activity.distance_m), 0.0),
        func.coalesce(func.sum(Activity.duration_s), 0.0),
    ).where(
        # "running" の完全一致のみを対象にする。typeKeyの表記揺れ（トレッドミルラン等の
        # 派生種別）が存在する場合の扱いはMVPスコープ外として考慮しない
        # （docs/08_詳細設計.md 基本設計書との整合性メモ 参照。意図した挙動）。
        Activity.activity_type == "running",
        Activity.start_time_local >= start,
        Activity.start_time_local <= end,
    )
    distance_m, duration_s = db.execute(stmt).one()
    return RunningSummary(distance_m=float(distance_m), duration_s=float(duration_s))


def calc_running_summary(
    db: Session, now: datetime | None = None
) -> ActivitySummaryOut:
    """直近7日間・直近28日間のランニング合計距離・合計時間を集計する。

    now を省略した場合は datetime.now() を使う（テスト時に固定日時を注入できる
    ように引数化してある）。該当レコードが0件の場合はCOALESCEにより0.0/0.0になる
    （03_画面設計 の「0.0 km / 0時間0分」の0埋め表示に対応）。
    """
    if now is None:
        now = datetime.now()

    last_7_days = _sum_running(db, now - timedelta(days=7), now)
    last_28_days = _sum_running(db, now - timedelta(days=28), now)

    return ActivitySummaryOut(last_7_days=last_7_days, last_28_days=last_28_days)
