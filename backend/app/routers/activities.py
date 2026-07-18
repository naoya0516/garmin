"""HTTPリクエスト/レスポンスの境界。

ビジネスロジックはsync.py/summary.pyに委譲し、ルーター自体は薄く保つ
（docs/08_詳細設計.md `routers/activities.py` 節）。
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.models import Activity
from app.schemas import ActivityOut, ActivitySummaryOut, SyncResult
from app.summary import calc_running_summary
from app.sync import sync_recent_activities

router = APIRouter(prefix="/api")


@router.get("/activities", response_model=list[ActivityOut])
def list_activities(
    limit: int = 50, db: Session = Depends(get_db)
) -> list[ActivityOut]:
    # DB読み取り系: try/exceptを置かず、FastAPIの標準例外処理に委ねる
    # （07_非機能要件「詳細なエラーハンドリングは行わない」方針）。
    activities = (
        db.query(Activity)
        .order_by(Activity.start_time_local.desc())
        .limit(limit)
        .all()
    )
    return activities


@router.post("/sync", response_model=SyncResult)
def sync(
    settings: Settings = Depends(get_settings), db: Session = Depends(get_db)
) -> SyncResult:
    # Garmin通信を伴う唯一のエンドポイント。例外を捕捉し、500 + 簡潔なdetail
    # メッセージに変換する最低限のtry/exceptのみを置く（個別の例外種別ごとの
    # ハンドリング・リトライは行わない）。
    try:
        return sync_recent_activities(db, settings.sync_lookback_days)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/activities/summary", response_model=ActivitySummaryOut)
def get_summary(db: Session = Depends(get_db)) -> ActivitySummaryOut:
    # list_activitiesと同様、明示的なtry/exceptは配置しない。
    return calc_running_summary(db)
