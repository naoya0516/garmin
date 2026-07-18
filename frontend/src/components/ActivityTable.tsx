// Propsで受け取ったアクティビティ配列を表として描画するだけの純粋表示コンポーネント。
// フェッチ・状態管理は行わない。docs/08_詳細設計.md `components/ActivityTable.tsx` 節。

import type { Activity } from "../types";
import {
  formatCalories,
  formatDate,
  formatDistanceKm,
  formatDuration,
  formatHr,
  formatPace,
} from "../utils/format";

interface ActivityTableProps {
  activities: Activity[];
}

export function ActivityTable({ activities }: ActivityTableProps) {
  if (activities.length === 0) {
    // 03_画面設計: 一覧が0件の場合は空状態メッセージを表示する。
    return <p className="empty-message">アクティビティがありません。同期してください。</p>;
  }

  return (
    <table className="activity-table">
      <thead>
        <tr>
          <th>日付</th>
          <th>種別</th>
          <th>距離</th>
          <th>時間</th>
          <th>ペース</th>
          <th>平均心拍</th>
          <th>カロリー</th>
        </tr>
      </thead>
      <tbody>
        {activities.map((activity) => (
          <tr key={activity.activity_id}>
            <td>{formatDate(activity.start_time_local)}</td>
            <td>{activity.activity_type}</td>
            <td>{formatDistanceKm(activity.distance_m)}</td>
            <td>{formatDuration(activity.duration_s)}</td>
            <td>{formatPace(activity.average_pace_min_per_km)}</td>
            <td>{formatHr(activity.average_hr)}</td>
            <td>{formatCalories(activity.calories)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
