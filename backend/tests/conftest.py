"""テスト用の共有fixture。

各テストで使い捨てのインメモリSQLite DBを用意する。app.database の
グローバルengine（ファイルDB）とは分離し、実データ(data/garmin.db)を汚さない。
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Activity  # noqa: F401  (テーブル定義をBase.metadataに登録するため)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
