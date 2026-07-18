// 表示用のフォーマット変換のみを行う純粋関数群。DOM操作・状態は持たない。
// ActivityTable.tsx・SummaryPanel.tsxの両方から利用する共通関数。
// docs/08_詳細設計.md `utils/format.ts` 節。
//
// 【重要】null と 0 は明示的に `=== null` で区別する（`if (!value)` のような
// falsy判定を使わない）。SummaryPanelでは「対象期間にランニング記録が0件」の
// 場合に正当に0が渡され、その場合は「0.0km」のような0埋め表示が正しい仕様
// （03_画面設計 参照）。`if (!value)` 等のfalsy判定を使うと 0 が null と
// 同じ「-」表示になってしまい、この0埋め要件を壊す（ISSUE_LOG.md 2026-07-17付
// エントリで合意済み）。

export function formatDate(iso: string): string {
  // "2026-07-16T06:30:00" -> "2026-07-16"（先頭10文字を切り出す）
  return iso.slice(0, 10);
}

export function formatDistanceKm(meters: number | null): string {
  if (meters === null) return "-";
  return `${(meters / 1000).toFixed(1)}km`;
}

export function formatDuration(seconds: number | null): string {
  if (seconds === null) return "-";
  const totalSeconds = Math.round(seconds);
  const minutes = Math.floor(totalSeconds / 60);
  const secs = totalSeconds % 60;
  return `${minutes}:${String(secs).padStart(2, "0")}`;
}

export function formatPace(minPerKm: number | null): string {
  if (minPerKm === null) return "-";
  const minutes = Math.floor(minPerKm);
  const seconds = Math.round((minPerKm - minutes) * 60);
  return `${minutes}:${String(seconds).padStart(2, "0")}/km`;
}

export function formatHr(bpm: number | null): string {
  if (bpm === null) return "-";
  return `${Math.round(bpm)}bpm`;
}

export function formatCalories(kcal: number | null): string {
  if (kcal === null) return "-";
  return `${Math.round(kcal)}kcal`;
}

// SummaryPanel専用: 秒数を「N時間M分」形式で表示する
// （03_画面設計 のサマリーブロック表記「2時間10分」「0時間0分」に対応）。
export function formatDurationHoursMinutes(seconds: number): string {
  const totalMinutes = Math.round(seconds / 60);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return `${hours}時間${minutes}分`;
}
