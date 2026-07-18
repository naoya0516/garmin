// バックエンドAPIへのHTTP呼び出しのみを担う。UIロジック・状態管理は持たない。
// docs/08_詳細設計.md `api/client.ts` 節。

import type { Activity, ActivitySummary, SyncResult } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function fetchActivities(limit = 50): Promise<Activity[]> {
  const res = await fetch(`${API_BASE_URL}/api/activities?limit=${limit}`);
  if (!res.ok) throw new Error(`GET /api/activities failed: ${res.status}`);
  return res.json();
}

export async function syncActivities(): Promise<SyncResult> {
  const res = await fetch(`${API_BASE_URL}/api/sync`, { method: "POST" });
  if (!res.ok) throw new Error(`POST /api/sync failed: ${res.status}`);
  return res.json();
}

export async function fetchSummary(): Promise<ActivitySummary> {
  const res = await fetch(`${API_BASE_URL}/api/activities/summary`);
  if (!res.ok) throw new Error(`GET /api/activities/summary failed: ${res.status}`);
  return res.json();
}
