"use client";

import { useEffect } from "react";
import { useParams } from "next/navigation";
import { useCurrentUser } from "@/stores/auth";
import { RealtimeProvider } from "@/providers/RealtimeProvider";
import { TerminalPane } from "@/components/workspace/TerminalPane";
import { getShortPodKey } from "@/lib/pod-display-name";

export default function PopoutTerminalPage() {
  const { podKey } = useParams<{ podKey: string }>();
  const user = useCurrentUser();

  useEffect(() => {
    if (podKey) {
      document.title = `Terminal - ${getShortPodKey(podKey)}`;
    }
  }, [podKey]);

  if (!user || !podKey) return null;

  return (
    <RealtimeProvider>
      <div className="h-screen w-screen bg-terminal-bg">
        <TerminalPane
          paneId={`popout-${podKey}`}
          podKey={podKey}
          isActive={true}
          showHeader={true}
          allowSplit={false}
        />
      </div>
    </RealtimeProvider>
  );
}
