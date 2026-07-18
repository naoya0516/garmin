"""APIレスポンス用Pydanticモデルの定義。

ORMモデルとは分離し、raw_jsonのような内部専用フィールドを外部に漏らさないための境界。
docs/08_詳細設計.md `schemas.py` 節 / docs/05_API設計.md のレスポンス例と1:1対応。
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActivityOut(BaseModel):
    activity_id: int
    activity_name: str | None
    activity_type: str
    start_time_local: datetime
    distance_m: float | None
    duration_s: float | None
    average_hr: float | None
    calories: float | None
    average_pace_min_per_km: float | None

    model_config = ConfigDict(from_attributes=True)


class SyncResult(BaseModel):
    fetched: int
    upserted: int


class RunningSummary(BaseModel):
    distance_m: float  # 対象期間内・running種別のみの合計距離(m)。該当なしは0.0
    duration_s: float  # 同上、合計時間(秒)。該当なしは0.0


class ActivitySummaryOut(BaseModel):
    last_7_days: RunningSummary
    last_28_days: RunningSummary
