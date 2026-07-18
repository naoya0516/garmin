"""SQLAlchemyのエンジン・セッション・Base・DIヘルパーの定義。

docs/08_詳細設計.md `database.py` 節。
"""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# database_url が指す data/ ディレクトリが存在しない場合、engine生成前に作成しておく
# （初回起動時にディレクトリが無くて失敗するのを防ぐ）。
if settings.database_url.startswith("sqlite:///./"):
    db_path = Path(settings.database_url.removeprefix("sqlite:///./"))
    db_path.parent.mkdir(parents=True, exist_ok=True)

# SQLiteはデフォルトでは同一スレッドからのみ接続可能なため、
# check_same_thread=False を付与する（FastAPIのDepends注入がリクエストごとに
# 異なるスレッドを使い得るため）。
engine = create_engine(
    settings.database_url, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
