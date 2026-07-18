from datetime import datetime, timedelta

from app.models import Activity
from app.summary import calc_running_summary

NOW = datetime(2026, 7, 17, 12, 0, 0)


def _add_activity(db_session, activity_id, activity_type, days_ago, distance_m, duration_s):
    db_session.add(
        Activity(
            activity_id=activity_id,
            activity_name="test",
            activity_type=activity_type,
            start_time_local=NOW - timedelta(days=days_ago),
            distance_m=distance_m,
            duration_s=duration_s,
            average_hr=None,
            calories=None,
            average_pace_min_per_km=None,
            raw_json={},
        )
    )
    db_session.commit()


def test_calc_running_summary_normal(db_session):
    # 直近7日以内: running 1件
    _add_activity(db_session, 1, "running", 2, 5000.0, 1500.0)
    # 8〜28日以内: running 1件（7日サマリーには含まれず28日サマリーのみ含む）
    _add_activity(db_session, 2, "running", 10, 3000.0, 900.0)
    # ランニング以外は集計対象外
    _add_activity(db_session, 3, "walking", 1, 2000.0, 1200.0)

    result = calc_running_summary(db_session, now=NOW)

    assert result.last_7_days.distance_m == 5000.0
    assert result.last_7_days.duration_s == 1500.0
    assert result.last_28_days.distance_m == 8000.0
    assert result.last_28_days.duration_s == 2400.0


def test_calc_running_summary_no_data_returns_zero(db_session):
    # 該当レコードが0件の場合はCOALESCEにより0.0/0.0（0埋め表示に対応）
    result = calc_running_summary(db_session, now=NOW)

    assert result.last_7_days.distance_m == 0.0
    assert result.last_7_days.duration_s == 0.0
    assert result.last_28_days.distance_m == 0.0
    assert result.last_28_days.duration_s == 0.0


def test_calc_running_summary_excludes_unknown_type(db_session):
    # activityType.typeKeyが取得できず"unknown"にフォールバックしたレコードは
    # "running"の完全一致から外れ、サマリー集計対象にならない（意図した挙動）。
    _add_activity(db_session, 4, "unknown", 1, 5000.0, 1500.0)

    result = calc_running_summary(db_session, now=NOW)

    assert result.last_7_days.distance_m == 0.0
    assert result.last_28_days.distance_m == 0.0
