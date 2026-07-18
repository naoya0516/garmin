// 同期ボタンの押下・ローディング状態の表示のみ。同期成功後の再フェッチは親
// （App.tsx）に委譲する。docs/08_詳細設計.md `components/SyncButton.tsx` 節。

import { useState } from "react";
import { syncActivities } from "../api/client";

interface SyncButtonProps {
  onSynced: () => void; // 同期成功後に親へ再フェッチを促すコールバック
  onError: (message: string) => void; // 失敗時、エラー表示を親(App.tsx)に一元化する
}

export function SyncButton({ onSynced, onError }: SyncButtonProps) {
  const [isSyncing, setIsSyncing] = useState(false);

  async function handleClick() {
    setIsSyncing(true);
    try {
      await syncActivities();
      onSynced();
    } catch {
      // Garmin側のエラー詳細はそのまま表示せず、固定の簡易メッセージとする
      // （07_非機能要件のセキュリティ方針との整合、および実装の単純化のため）。
      onError("同期に失敗しました");
    } finally {
      setIsSyncing(false);
    }
  }

  return (
    <button type="button" onClick={handleClick} disabled={isSyncing}>
      {isSyncing ? "同期中..." : "同期"}
    </button>
  );
}
