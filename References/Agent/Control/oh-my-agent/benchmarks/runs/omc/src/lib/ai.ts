import type { AIMessage } from "@/types/world";

export async function getAIResponse(
  message: string | undefined,
  objectCount: number,
  environment: string
): Promise<{ response: string; suggestions: string[] }> {
  const res = await fetch("/api/ai", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, objectCount, environment }),
  });
  return res.json();
}

export function createAIMessage(content: string, suggestions?: string[]): AIMessage {
  return {
    id: crypto.randomUUID(),
    role: "ai",
    content,
    timestamp: new Date().toISOString(),
    suggestions,
  };
}

export function createChildMessage(content: string): AIMessage {
  return {
    id: crypto.randomUUID(),
    role: "child",
    content,
    timestamp: new Date().toISOString(),
  };
}
