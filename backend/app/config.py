"""アプリ全体の設定値を一元管理するモジュール。

他モジュールは環境変数を直接読まず、必ずこのモジュール経由で値を参照する
（docs/08_詳細設計.md `config.py` 節）。
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv
import os

# アプリ起動時（モジュールロード時）に一度だけ.envを読み込む。
load_dotenv()


@dataclass(frozen=True)
class Settings:
    garmin_email: str | None
    garmin_password: str | None
    # SYNC_LOOKBACK_DAYS: 同期時にGarminから取得する直近日数。既定30日。
    #
    # 【暗黙の前提】summary.py は直近7日間・直近28日間のランニング合計を集計するが、
    # その集計はあくまで「DBに既に同期済みのデータ」に対して行われる（Garmin通信は
    # 行わない）。したがって、この sync_lookback_days が28日未満に設定されている場合、
    # 「直近28日間サマリー」は実際には過去 sync_lookback_days 日分しか同期されていない
    # データを対象に集計されることになり、28日間全体を正しく反映しない（＝未同期期間を
    # 含んだ不完全な集計になる）。運用上は30日以上を維持すること。
    sync_lookback_days: int
    database_url: str
    # garminconnectのトークンキャッシュ保存先。scripts/init_login.py で生成され、
    # garmin_client.get_client() が読み込む。
    tokenstore_path: str
    cors_allow_origin: str


@lru_cache
def get_settings() -> Settings:
    """プロセス内シングルトンとしてSettingsを返す。

    garmin_email/garmin_password が未設定でも例外は送出しない
    （GET /api/activities のようなDBのみで完結する経路を、Garmin認証情報の
    有無で壊さないため。実際にGarmin通信が必要になるのは garmin_client.py の
    呼び出し時のみ）。
    """
    return Settings(
        garmin_email=os.getenv("GARMIN_EMAIL") or None,
        garmin_password=os.getenv("GARMIN_PASSWORD") or None,
        sync_lookback_days=int(os.getenv("SYNC_LOOKBACK_DAYS", "30")),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./data/garmin.db"),
        tokenstore_path=os.getenv("TOKENSTORE_PATH", "~/.garminconnect"),
        cors_allow_origin=os.getenv("CORS_ALLOW_ORIGIN", "http://localhost:5173"),
    )
