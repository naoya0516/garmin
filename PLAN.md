# Garmin活動データ取得・表示アプリ（MVP）

> 詳細設計は基本設計書（[docs/00_目次.md](docs/00_目次.md)）を参照。本ファイルは実装時のセットアップ手順書として残す。

## Context

Garminで記録した走行データ（ランニング等）を管理し、将来的にはカレンダー表示や分析機能を持つアプリを作りたい。今回のスコープはその第一歩として、Garmin Connectからアクティビティデータを取得し、DBに保存し、Web画面に一覧表示するところまで。カレンダーや分析機能は将来の拡張とし、今回は設計時にそれを阻害しないデータ構造にする程度に留める。

`c:\Users\highj\ClaudeCode\garmin` は現状空のディレクトリ。兄弟プロジェクト `catan-game`（Vite + React + TypeScript構成）の設定パターンを踏襲する。

## 合意済み要件

- 技術スタック: バックエンド Python (FastAPI) / フロントエンド React + TypeScript (Vite)
- Garmin連携: `garminconnect` (PyPI, cyberjunky/python-garminconnect) による非公式ログイン。認証情報は `.env` の `GARMIN_EMAIL`/`GARMIN_PASSWORD`
- 永続化: SQLite。同期時にupsertし、画面表示はDBから読む（毎回Garminを叩かない）
- 初回取得範囲: 直近30日、全アクティビティ種別（ランニング以外も取得・保存）
- 表示項目: 日付・種別・距離・時間・ペース・平均心拍・消費カロリー
- UX: 「同期」ボタンで手動同期→一覧再取得のシンプルな1画面

## ディレクトリ構成

```
garmin/
├── .gitignore
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── scripts/init_login.py     # 初回ログイン専用（MFA対応、ターミナルで手動実行）
│   └── app/
│       ├── main.py               # FastAPIアプリ、CORS、create_all、ルーター登録
│       ├── config.py             # .env読み込み
│       ├── database.py           # engine, SessionLocal, Base, get_db
│       ├── models.py             # Activity ORMモデル
│       ├── schemas.py            # ActivityOut (Pydantic)
│       ├── garmin_client.py      # ログイン・直近N日取得ラッパー
│       ├── sync.py               # upsertロジック
│       ├── pace.py               # ペース計算 (distance/duration → min/km)
│       └── routers/activities.py # GET /api/activities, POST /api/sync
└── frontend/                     # catan-gameのvite.config/tsconfig/oxlint設定を踏襲、zustandは不要なので除外
    └── src/
        ├── App.tsx                # マウント時fetch＋同期ボタン押下で再fetchのオーケストレーション
        ├── types.ts                # Activity型（ActivityOutと1:1対応）
        ├── api/client.ts           # fetchActivities(), syncActivities()
        ├── components/ActivityTable.tsx
        ├── components/SyncButton.tsx
        └── utils/format.ts         # ペース/時間/日付の整形
```

## バックエンド設計

**MFAの扱い**: `Garmin(email, password, prompt_mfa=...)` の `prompt_mfa` はブロッキング入力になるため、FastAPIのリクエストハンドラ内では使わない。初回のみ `scripts/init_login.py` を手動実行してトークンキャッシュ（`client.login(tokenstore_path)` → `garth`が自動保存）を作成し、以降 `POST /api/sync` はキャッシュ済みトークンを再利用するだけにする。

**`models.py` の `Activity` テーブル**（GarminのactivityIdを主キーにしてupsertで重複防止。将来の分析拡張に備え生レスポンスも保持）:
- `activity_id` (BigInteger, PK) — GarminのactivityId
- `activity_name` (String, nullable)
- `activity_type` (String, index) — typeKey（running/cycling/walking等）
- `start_time_local` (DateTime, index)
- `distance_m`, `duration_s`, `average_hr`, `calories` (Float, nullable)
- `average_pace_min_per_km` (Float, nullable) — sync時に`pace.py`で計算して保存
- `raw_json` (JSON) — Garminの生レスポンス（将来の分析用に未使用フィールドも保持）
- `synced_at` (DateTime, server_default=now, onupdate=now)

**`garmin_client.py`**: `fetch_recent_activities(days: int) -> list[dict]` で `client.get_activities_by_date(start_iso, end_iso)`（activitytype省略で全種別）を呼ぶ。実装時に `garminconnect` パッケージの実際のdocstring/型定義（`pip show`後にインストール先を確認、または `help(client.get_activities_by_date)`）で正確なシグネチャを再確認すること（README調査では引数の詳細までは確定できなかった）。

**`sync.py`**: SQLiteの `INSERT ... ON CONFLICT(activity_id) DO UPDATE`（`sqlalchemy.dialects.sqlite.insert`）でupsert。

**APIエンドポイント**（`routers/activities.py`、prefix `/api`）:
| Method | Path | 説明 |
|---|---|---|
| GET | `/activities` | DBから`start_time_local desc`で一覧取得（`limit`クエリ、既定50） |
| POST | `/sync` | Garminから直近30日・全種別を取得しupsert。`{"fetched": int, "upserted": int}`を返す |

**`main.py`**: `CORSMiddleware`で`http://localhost:5173`を許可。`Base.metadata.create_all(bind=engine)`でテーブル作成（Alembic等のマイグレーションツールは今回不要）。

**依存 (`requirements.txt`)**: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `garminconnect`, `python-dotenv`

## フロントエンド設計

catan-gameの `package.json`/`vite.config.ts`/`tsconfig*.json`/`.oxlintrc.json` を流用し、`zustand`依存は除外（状態が単純なため`useState`/`useEffect`で十分。将来カレンダー機能等で複雑化したら追加）。

- `api/client.ts`: `fetchActivities()` (GET /api/activities), `syncActivities()` (POST /api/sync)。`VITE_API_BASE_URL`環境変数、既定`http://localhost:8000`
- `ActivityTable.tsx`: Propsでデータを受け取るだけの純粋表示コンポーネント。列は日付・種別・距離・時間・ペース・平均心拍・カロリー
- `SyncButton.tsx`: 押下中ローディング表示、完了後`onSynced`コールバックで親に再fetchを促す
- `App.tsx`: マウント時に一覧取得、同期ボタン押下後に再取得。エラーは簡易メッセージ表示のみ

## セットアップ手順

```
# backend
cd garmin/backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env    # GARMIN_EMAIL / GARMIN_PASSWORD を編集
python scripts\init_login.py   # 初回ログイン（MFAがあればここでコード入力）
uvicorn app.main:app --reload --port 8000

# frontend
cd garmin/frontend
npm install
npm run dev    # http://localhost:5173
```

`.gitignore`に追加: `backend/venv/`, `backend/.env`, `backend/data/`, `backend/.garmin_tokens/`（または`~/.garminconnect`側キャッシュ）, `frontend/node_modules/`, `frontend/dist/`

## 検証方法

1. バックエンド単体: `uvicorn`起動後 `http://localhost:8000/docs` (Swagger UI) で `POST /api/sync` を実行し `{"fetched": N, "upserted": N}` を確認、続けて `GET /api/activities` で一覧が返ることを確認
2. フロントエンド: `npm run dev` で `http://localhost:5173` を開き、「同期」ボタン押下でテーブルに直近30日分のアクティビティ（日付・種別・距離・時間・ペース・平均心拍・カロリー）が表示され、CORSエラーが出ないことを確認

※ 実際のGarminアカウントでのログイン確認はユーザーの実認証情報が必要なため、動作確認はユーザー自身による最終確認が必要（`scripts/init_login.py`実行とSwagger UIでの`/api/sync`確認をユーザーに依頼する）。

## ステータス

2026-07-17時点: 要件定義・設計完了。実装はまだ着手していない。
