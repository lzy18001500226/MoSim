import { openai } from "@/lib/openai";
import { COMPANION_SYSTEM_PROMPT, buildUserMessage } from "@/features/companion/utils/prompts";
import { z } from "zod";

const requestSchema = z.object({
  objectCount: z.number(),
  objectTypes: z.array(z.string()),
  environment: z.string(),
  userMessage: z.string().optional(),
  history: z
    .array(
      z.object({
        role: z.enum(["user", "assistant"]),
        content: z.string(),
      })
    )
    .optional(),
});

export async function POST(request: Request) {
  const body = await request.json();
  const parsed = requestSchema.safeParse(body);

  if (!parsed.success) {
    return Response.json({ error: "Invalid input" }, { status: 400 });
  }

  const { objectCount, objectTypes, environment, userMessage, history } = parsed.data;

  const messages: Array<{ role: "system" | "user" | "assistant"; content: string }> = [
    { role: "system", content: COMPANION_SYSTEM_PROMPT },
  ];

  if (history) {
    for (const msg of history.slice(-6)) {
      messages.push({ role: msg.role, content: msg.content });
    }
  }

  messages.push({
    role: "user",
    content: buildUserMessage({ objectCount, objectTypes, environment, userMessage }),
  });

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages,
    max_tokens: 100,
    temperature: 0.8,
  });

  const content =
    response.choices[0]?.message?.content || "What would you like to build today?";

  return Response.json({ message: content });
}
