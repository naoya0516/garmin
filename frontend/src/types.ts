// バックエンド app/schemas.py の ActivityOut/SyncResult/ActivitySummaryOut と1:1対応させる。
// docs/08_詳細設計.md `types.ts` 節。

export interface Activity {
  activity_id: number;
  activity_name: string | null;
  activity_type: string;
  start_time_local: string; // ISO8601文字列。パースはutils/format.ts側で行う
  distance_m: number | null;
  duration_s: number | null;
  average_hr: number | null;
  calories: number | null;
  average_pace_min_per_km: number | null;
}

export interface SyncResult {
  fetched: number;
  upserted: number;
}

export interface RunningSummary {
  distance_m: number;
  duration_s: number;
}

export interface ActivitySummary {
  last_7_days: RunningSummary;
  last_28_days: RunningSummary;
}
