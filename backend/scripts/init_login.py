"""初回ログイン専用スクリプト（MFA対応、ターミナルで手動実行）。

python scripts/init_login.py で実行する。GARMIN_EMAIL/GARMIN_PASSWORDで
ログインし、MFAが必要な場合はターミナルからのinput()でコードを入力させる。
成功するとtokenstore_path（既定 ~/.garminconnect）にトークンキャッシュが保存され、
以降 POST /api/sync はこのキャッシュを再利用するだけになる（06_外部インターフェース
設計・08_詳細設計 参照）。
"""

from __future__ import annotations

import sys
from pathlib import Path

# backend/ をパスに追加してこのスクリプトを単独実行できるようにする。
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from garminconnect import Garmin  # noqa: E402

from app.config import get_settings  # noqa: E402


def prompt_mfa() -> str:
    return input("Garmin MFAコードを入力してください: ").strip()


def main() -> None:
    settings = get_settings()

    if not settings.garmin_email or not settings.garmin_password:
        print(
            "GARMIN_EMAIL / GARMIN_PASSWORD が.envに設定されていません。"
            ".env.exampleをコピーして編集してください。",
            file=sys.stderr,
        )
        sys.exit(1)

    client = Garmin(
        email=settings.garmin_email,
        password=settings.garmin_password,
        prompt_mfa=prompt_mfa,
    )
    client.login(settings.tokenstore_path)

    print(f"ログインに成功しました。トークンを保存しました: {settings.tokenstore_path}")
    print("以降は `uvicorn app.main:app --reload --port 8000` でアプリを起動し、"
          "同期ボタン(POST /api/sync)からキャッシュ済みトークンを再利用できます。")


if __name__ == "__main__":
    main()
