export interface Metrics {
  sessions: number;
  skillsUsed: Record<string, number>;
  tasksCompleted: number;
  totalSessionTime: number;
  filesChanged: number;
  linesAdded: number;
  linesRemoved: number;
  lastUpdated: string;
  startDate: string;
  lastSessionId?: string;
  lastSessionStatus?: string;
  lastSessionStarted?: string;
  lastSessionDuration?: number;
}

export interface Retrospective {
  id: string;
  date: string;
  summary: string;
  keyLearnings: string[];
  filesChanged: string[];
  nextSteps: string[];
}

export interface CleanupResult {
  cleaned: number;
  skipped: number;
  details: string[];
}
