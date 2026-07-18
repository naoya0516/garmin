"""FastAPIアプリケーションの組み立て（アプリ生成・CORS設定・DB初期化・ルーター登録）のみ。

ビジネスロジックは持たない（docs/08_詳細設計.md `main.py` 節）。
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import activities

app = FastAPI(title="Garmin Activity Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().cors_allow_origin],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# create_allは冪等（既存テーブルがあれば何もしない）なので、--reloadによる
# リロード時にも安全。Alembic等のマイグレーションツールは今回不要
# （07_非機能要件 参照）。
Base.metadata.create_all(bind=engine)

app.include_router(activities.router)
