# 05. API設計

バックエンド（FastAPI, `localhost:8000`）が提供する内部REST APIの仕様。フロントエンド（`localhost:5173`）専用であり、外部公開は想定しない（[07_非機能要件](07_非機能要件.md) 参照）。

## エンドポイント一覧

| Method | Path | 概要 | 対応機能 |
|---|---|---|---|
| GET | `/api/activities` | DBに保存済みのアクティビティ一覧を取得 | F-02 |
| POST | `/api/sync` | Garmin Connectから直近30日・全種別を取得しDBにupsert | F-01 |
| GET | `/api/activities/summary` | 直近7日間・直近28日間の合計距離・合計時間サマリーを取得（ランニングのみ集計） | F-03 |

## GET /api/activities

### リクエスト

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|
| `limit` | int (query) | 任意 | 50 | 取得件数の上限 |

### レスポンス（200 OK）

`start_time_local` の降順で返す。

```json
[
  {
    "activity_id": 123456789,
    "activity_name": "Morning Run",
    "activity_type": "running",
    "start_time_local": "2026-07-16T06:30:00",
    "distance_m": 5200.0,
    "duration_s": 1710.0,
    "average_hr": 152.0,
    "calories": 320.0,
    "average_pace_min_per_km": 5.48
  }
]
```

`raw_json`はレスポンスに含めない（フロントエンドでは不要なため。[04_DB設計](04_DB設計.md) 参照）。

## POST /api/sync

### リクエスト

パラメータなし（対象期間は[06_外部インターフェース設計](06_外部インターフェース設計.md)で定める既定値=直近30日を使用）。

### レスポンス（200 OK）

```json
{
  "fetched": 12,
  "upserted": 12
}
```

| フィールド | 説明 |
|---|---|
| `fetched` | Garmin Connectから取得したアクティビティ件数 |
| `upserted` | DBにupsertした件数（通常`fetched`と一致） |

## GET /api/activities/summary

### リクエスト

パラメータなし。

### レスポンス（200 OK）

`activity_type == "running"`のレコードのみを対象に、直近7日間・直近28日間それぞれの合計距離・合計時間を返す。

```json
{
  "last_7_days": {
    "distance_m": 21400.0,
    "duration_s": 7800.0
  },
  "last_28_days": {
    "distance_m": 98600.0,
    "duration_s": 35100.0
  }
}
```

対象期間内にランニングの記録が無い場合、`distance_m`・`duration_s`はともに`0.0`（0埋め）で返す。

## エラーレスポンスの方針

MVPでは詳細なエラーハンドリングは行わない。Garmin Connectへのログイン失敗やネットワークエラーはFastAPIの標準的な500エラーとして返し、詳細なリトライ・エラーメッセージ設計は将来課題とする。フロントエンド側も簡易的なエラーメッセージ表示に留める（[03_画面設計](03_画面設計.md) 参照）。

`GET /api/activities/summary`もDB読み取りのみのエンドポイントであり、上記と同じ方針（明示的なtry/exceptを置かず、FastAPIの標準例外処理に委ねる）がそのまま適用される。
