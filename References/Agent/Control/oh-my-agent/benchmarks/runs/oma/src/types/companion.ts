export type MessageRole = "assistant" | "user";

export interface CompanionMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: number;
}

export interface Suggestion {
  id: string;
  text: string;
}
