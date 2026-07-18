"""Garminから取得した生データをDBにupsertする一連の処理をオーケストレーションする。

docs/08_詳細設計.md `sync.py` 節。
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from app import garmin_client
from app.models import Activity
from app.pace import calc_pace_min_per_km
from app.schemas import SyncResult


def sync_recent_activities(db: Session, days: int) -> SyncResult:
    """直近 `days` 日分のアクティビティをGarminから取得し、DBにupsertする。"""
    raw_list = garmin_client.fetch_recent_activities(days)
    fetched = len(raw_list)
    rows = [_to_activity_fields(raw) for raw in raw_list]
    upserted = upsert_activities(db, rows)
    return SyncResult(fetched=fetched, upserted=upserted)


def _parse_start_time_local(value: str) -> datetime:
    """Garminの `startTimeLocal` をパースする。

    スペース区切り（"2026-07-16 06:30:00"）とT区切り（ISO8601形式）の両方を
    ハンドリングできるようにしておく（docs/08_詳細設計.md マッピング仕様表 参照）。
    """
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def _to_activity_fields(raw: dict) -> dict:
    """Garmin生レスポンス1件をActivityのカラム名に対応するdictに変換する。

    docs/08_詳細設計.md のマッピング仕様表に基づく。キーが存在しない/Noneの場合は
    該当カラムをNoneのまま保存する（欠損値のフォールバック補完は行わない。
    07_非機能要件の「詳細なエラーハンドリングは行わない」方針に沿う）。
    """
    distance_m = raw.get("distance")
    duration_s = raw.get("duration")

    # activityType.typeKey が取得できない場合は "unknown" にフォールバックする。
    # これは意図した挙動であり、summary.py が activity_type == "running" の完全一致
    # のみを対象にすることと合わせて、"unknown" のレコードはランニングサマリーの
    # 集計対象から自動的に除外される（＝取得できない種別を誤ってrunning扱いしない
    # ための安全側フォールバック）。
    activity_type = (raw.get("activityType") or {}).get("typeKey") or "unknown"

    start_time_local_raw = raw.get("startTimeLocal")

    return {
        "activity_id": raw.get("activityId"),
        "activity_name": raw.get("activityName"),
        "activity_type": activity_type,
        "start_time_local": _parse_start_time_local(start_time_local_raw),
        "distance_m": distance_m,
        "duration_s": duration_s,
        "average_hr": raw.get("averageHR"),
        "calories": raw.get("calories"),
        "average_pace_min_per_km": calc_pace_min_per_km(distance_m, duration_s),
        "raw_json": raw,
    }


def upsert_activities(db: Session, rows: list[dict]) -> int:
    """SQLiteのUPSERTを使い、activity_idの重複を排除しながら一括登録・更新する。"""
    if not rows:
        return 0

    # 同一activity_idがバッチ内で重複した場合、insert().values(rows)が同一
    # トランザクション内で同じ行を2回対象にしエラーになりうるため、先に
    # activity_id単位で重複除去する（後勝ち＝リストの後の要素を採用）。
    deduped: dict[int, dict] = {}
    for row in rows:
        deduped[row["activity_id"]] = row
    unique_rows = list(deduped.values())

    stmt = insert(Activity).values(unique_rows)
    update_cols = {
        c.name: stmt.excluded[c.name]
        for c in Activity.__table__.columns
        if c.name != "activity_id"
    }
    # synced_at は on_conflict_do_update の set_ に明示的に含める。
    # models.py の onupdate=func.now() はORM経由のUPDATE（session.add等）にのみ
    # 効き、ここで使っているCore APIの insert().on_conflict_do_update() には
    # 適用されないため、明示的にfunc.now()をセットしないと最終同期日時が更新
    # されないままになる（ISSUE_LOG.md 2026-07-17付エントリで合意済み）。
    update_cols["synced_at"] = func.now()
    stmt = stmt.on_conflict_do_update(index_elements=["activity_id"], set_=update_cols)

    db.execute(stmt)
    db.commit()

    # SQLiteのon_conflict_do_updateは「INSERTされた行数」を返さないため、
    # 重複除去後の件数をそのままupsertedとして扱う（05_API設計 の
    # 「通常fetchedと一致する」という記述と整合させる）。
    return len(unique_rows)
