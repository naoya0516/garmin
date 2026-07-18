// F-03のサマリーブロック（直近7日間・直近28日間の合計距離・合計時間）の表示のみを
// 行う純粋表示コンポーネント。docs/08_詳細設計.md `components/SummaryPanel.tsx` 節。

import type { ActivitySummary, RunningSummary } from "../types";
import { formatDistanceKm, formatDurationHoursMinutes } from "../utils/format";

interface SummaryPanelProps {
  summary: ActivitySummary | null; // 未取得時はnull
}

// 03_画面設計: 対象期間にランニング記録が無い場合は「0.0km / 0時間0分」の0埋め
// 表示とし、サマリー側には特別な空状態文言は設けない。summaryがnull（初回fetch
// 未完了時）でも真っ白にはせず、同じ0埋めのプレースホルダを表示する。
const ZERO_SUMMARY: RunningSummary = { distance_m: 0, duration_s: 0 };

export function SummaryPanel({ summary }: SummaryPanelProps) {
  const last7 = summary?.last_7_days ?? ZERO_SUMMARY;
  const last28 = summary?.last_28_days ?? ZERO_SUMMARY;

  return (
    <section className="summary-panel">
      <p>
        直近7日間 合計距離 {formatDistanceKm(last7.distance_m)} / 合計時間{" "}
        {formatDurationHoursMinutes(last7.duration_s)}
      </p>
      <p>
        直近28日間 合計距離 {formatDistanceKm(last28.distance_m)} / 合計時間{" "}
        {formatDurationHoursMinutes(last28.duration_s)}
      </p>
      <p className="summary-note">※ランニングのみ集計</p>
    </section>
  );
}
