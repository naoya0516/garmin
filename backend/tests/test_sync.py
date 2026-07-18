from app.models import Activity
from app.sync import _to_activity_fields, upsert_activities


def _raw_activity(activity_id, type_key="running", start="2026-07-16 06:30:00"):
    return {
        "activityId": activity_id,
        "activityName": "Morning Run",
        "activityType": {"typeKey": type_key},
        "startTimeLocal": start,
        "distance": 5200.0,
        "duration": 1710.0,
        "averageHR": 152.0,
        "calories": 320.0,
    }


def test_to_activity_fields_normal():
    fields = _to_activity_fields(_raw_activity(1))

    assert fields["activity_id"] == 1
    assert fields["activity_type"] == "running"
    assert fields["distance_m"] == 5200.0
    assert round(fields["average_pace_min_per_km"], 2) == 5.48


def test_to_activity_fields_missing_type_key_falls_back_to_unknown():
    # activityType自体が欠けているケース
    raw = _raw_activity(2)
    del raw["activityType"]
    fields = _to_activity_fields(raw)
    assert fields["activity_type"] == "unknown"


def test_upsert_activities_dedupes_same_activity_id_in_one_batch(db_session):
    # 同一activity_idがバッチ内で重複した場合、後の要素で上書きされ、
    # on_conflict_do_updateが同一トランザクション内で同じ行を2回対象にする
    # エラーを起こさないことを確認する。
    rows = [
        _to_activity_fields(_raw_activity(100, start="2026-07-16 06:30:00")),
        _to_activity_fields(_raw_activity(100, start="2026-07-16 07:00:00")),
    ]

    upserted = upsert_activities(db_session, rows)

    assert upserted == 1
    saved = db_session.query(Activity).filter_by(activity_id=100).one()
    assert saved.start_time_local.strftime("%H:%M:%S") == "07:00:00"


def test_upsert_activities_empty_rows_returns_zero(db_session):
    assert upsert_activities(db_session, []) == 0
