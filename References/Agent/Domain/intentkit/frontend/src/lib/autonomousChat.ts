export const getAutonomousChatId = (taskId: string) => `autonomous-${taskId}`;

export const buildTaskLogsPath = (agentId: string, taskId: string) =>
  `/agent/${agentId}/tasks/${taskId}/logs`;

export const buildChatThreadPath = (
  agentId: string,
  threadId?: string | null,
) => {
  if (!threadId) return `/agent/${agentId}`;
  const params = new URLSearchParams({ thread: threadId });
  return `/agent/${agentId}?${params.toString()}`;
};
