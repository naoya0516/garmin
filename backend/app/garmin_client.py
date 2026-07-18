"""Garmin Connectとの通信をラップするモジュール。

他モジュール（sync.py等）に対してGarmin固有のAPI形状を意識させない
（docs/08_詳細設計.md `garmin_client.py` 節）。
"""

from __future__ import annotations

from datetime import date, timedelta

from garminconnect import Garmin

from app.config import get_settings


def get_client() -> Garmin:
    """garminconnect.Garmin インスタンスを生成し、tokenstore_path からトークン
    キャッシュをロードしてログイン済み状態で返す。

    - prompt_mfa は渡さない（FastAPIのリクエストハンドラ内でブロッキング入力を
      発生させないため）。
    - トークンキャッシュが存在しない/失効している場合、garminconnectは
      GARMIN_EMAIL/GARMIN_PASSWORD を使った素の資格情報ログインにフォール
      バックする。その際MFAが必要でprompt_mfaが未指定だと
      GarminConnectAuthenticationError が送出される（scripts/init_login.py の
      未実行、またはキャッシュ失効を示すエラーとしてそのまま呼び出し元に伝播させる）。
    - プロセス内でクライアントを使い回すためのキャッシュは行わない（MVPでは
      呼び出し頻度が低く、同期ボタン押下のたびに生成しても性能上の問題はない
      ため。07_非機能要件 参照）。
    """
    settings = get_settings()
    client = Garmin(email=settings.garmin_email, password=settings.garmin_password)
    client.login(settings.tokenstore_path)
    return client


def fetch_recent_activities(days: int) -> list[dict]:
    """直近 `days` 日分・全種別のアクティビティをGarmin Connectから取得して返す。

    戻り値（Garminの生JSON配列。各要素はdict）はそのまま返す。このレイヤーでは
    加工・フィールド抽出を行わない（マッピングは sync.py の責務）。
    """
    client = get_client()
    end = date.today()
    start = end - timedelta(days=days)
    # activitytype引数は省略し全種別取得（06_外部インターフェース設計 参照）。
    return client.get_activities_by_date(start.isoformat(), end.isoformat())
