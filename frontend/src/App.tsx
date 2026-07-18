// 画面全体のstate管理とデータフローのオーケストレーション。API呼び出しの結果を
// 子コンポーネントにpropsとして渡すだけで、表示ロジック自体は持たない。
// docs/08_詳細設計.md `App.tsx` 節。

import { useEffect, useState } from "react";
import "./App.css";
import { fetchActivities, fetchSummary } from "./api/client";
import { ActivityTable } from "./components/ActivityTable";
import { SummaryPanel } from "./components/SummaryPanel";
import { SyncButton } from "./components/SyncButton";
import type { Activity, ActivitySummary } from "./types";

function App() {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [summary, setSummary] = useState<ActivitySummary | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function loadAll(): Promise<void> {
    // 03_画面設計の初回ロード/同期後シーケンス図に対応:
    // GET /api/activities → GET /api/activities/summary の順に呼び出し、
    // それぞれ結果をstateにセットする。個別にtry/catchし、片方が失敗しても
    // もう片方の表示は継続できるようにする（エラーメッセージのみ蓄積して表示）。
    // 失敗時もstateはクリアせず直前の表示内容を保持し、真っ白な画面にはしない。
    try {
      const data = await fetchActivities();
      setActivities(data);
    } catch {
      setErrorMessage("一覧の取得に失敗しました");
    }

    try {
      const data = await fetchSummary();
      setSummary(data);
    } catch {
      setErrorMessage("サマリーの取得に失敗しました");
    }
  }

  useEffect(() => {
    loadAll(); // マウント時に初回ロード
  }, []);

  function handleSynced() {
    setErrorMessage(null);
    loadAll();
  }

  function handleSyncError(message: string) {
    setErrorMessage(message);
  }

  return (
    <>
      <header className="app-header">
        <h1>Garmin Activity Tracker</h1>
        <SyncButton onSynced={handleSynced} onError={handleSyncError} />
      </header>
      {errorMessage && <div className="error-message">{errorMessage}</div>}
      <SummaryPanel summary={summary} />
      <ActivityTable activities={activities} />
    </>
  );
}

export default App;
