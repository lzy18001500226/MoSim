import { NextRequest, NextResponse } from "next/server";

const CREATIVE_PROMPTS = {
  start: [
    "What kind of world do you want to build today? 🌍",
    "Close your eyes and imagine a place... What do you see?",
    "If you could visit any world, what would it look like?",
    "Let's build something amazing! What's the first thing you'd put in your world?",
  ],
  explore: [
    "Who lives in this world? Can you add them?",
    "What sounds would you hear in this place?",
    "What happens when night falls here?",
    "Is there something hidden in your world?",
    "What would happen if everything became giant-sized?",
  ],
  extend: [
    "What if it started raining colors here?",
    "Can you make your world stranger?",
    "What's missing from this place?",
    "What would happen if gravity changed?",
    "Can your world tell a feeling?",
    "What if a new character arrived?",
  ],
  reflect: [
    "Why did you build it this way?",
    "What feeling does your world show?",
    "What changed from your first idea?",
    "What would you build next?",
    "If a friend visited your world, what would surprise them?",
  ],
  challenge: [
    "Can you add something that moves?",
    "Try making a secret spot in your world!",
    "What if you could only use 3 colors?",
    "Build the tallest thing you can imagine!",
    "Create a path someone could follow through your world.",
  ],
};

function getContextualPrompts(objectCount: number): string[] {
  if (objectCount === 0) return CREATIVE_PROMPTS.start;
  if (objectCount < 3) return CREATIVE_PROMPTS.explore;
  if (objectCount < 8) return CREATIVE_PROMPTS.extend;
  return CREATIVE_PROMPTS.reflect;
}

function generateResponse(objectCount: number, environment: string, message?: string): {
  response: string;
  suggestions: string[];
} {
  const prompts = getContextualPrompts(objectCount);
  const randomPrompt = prompts[Math.floor(Math.random() * prompts.length)];

  const suggestions = [];
  const allPrompts = [...CREATIVE_PROMPTS.challenge, ...CREATIVE_PROMPTS.extend];
  for (let i = 0; i < 3; i++) {
    const idx = Math.floor(Math.random() * allPrompts.length);
    suggestions.push(allPrompts[idx]);
  }

  if (message) {
    const responses = [
      `That's a wonderful idea! ${randomPrompt}`,
      `I love that! Here's another thought: ${randomPrompt}`,
      `Great thinking! Now, ${randomPrompt}`,
      `Ooh, interesting! ${randomPrompt}`,
    ];
    return {
      response: responses[Math.floor(Math.random() * responses.length)],
      suggestions,
    };
  }

  return { response: randomPrompt, suggestions };
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const { message, objectCount = 0, environment = "meadow" } = body;

  // If OPENAI_API_KEY is configured, use it for richer responses
  if (process.env.OPENAI_API_KEY) {
    try {
      const res = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
        },
        body: JSON.stringify({
          model: "gpt-4o-mini",
          messages: [
            {
              role: "system",
              content: `You are a warm, encouraging creative companion for a child (under grade 6) building a 3D world. The world currently has ${objectCount} objects and uses a "${environment}" theme. Keep responses to 1-2 short sentences. Ask imagination-sparking questions. Never give commands or correct answers. Suggest creative ideas as options. Use simple language. Be playful and supportive. End with a question or gentle suggestion.`,
            },
            { role: "user", content: message || "I just started building!" },
          ],
          max_tokens: 100,
          temperature: 0.9,
        }),
      });
      const data = await res.json();
      const aiResponse = data.choices?.[0]?.message?.content || "";
      const suggestions = CREATIVE_PROMPTS.challenge.slice(0, 3);
      return NextResponse.json({ response: aiResponse, suggestions });
    } catch {
      // Fall through to built-in responses
    }
  }

  const result = generateResponse(objectCount, environment, message);
  return NextResponse.json(result);
}
