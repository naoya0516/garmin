"""Activity ORMモデルの定義のみ。ビジネスロジックは持たない。

docs/08_詳細設計.md `models.py` 節 / docs/04_DB設計.md テーブル定義書と1:1対応。
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Activity(Base):
    __tablename__ = "activities"

    activity_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    activity_name: Mapped[str | None] = mapped_column(String, nullable=True)
    activity_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    start_time_local: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    distance_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    average_hr: Mapped[float | None] = mapped_column(Float, nullable=True)
    calories: Mapped[float | None] = mapped_column(Float, nullable=True)
    average_pace_min_per_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    # raw_json はレコードが必ず持つ値だが、Garminの生レスポンス自体がNoneになり得る
    # 経路（マッピング処理で未取得時）を許容するため nullable=True・型ヒントも
    # `dict | None` にする（ISSUE_LOG.md 2026-07-17付「実装着手前の懸念点洗い出し」で
    # 合意済み）。
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
