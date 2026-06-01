import { NextRequest, NextResponse } from "next/server";

const CREATIVE_PROMPTS = [
  "What if your world had a secret underground cave? What would be inside?",
  "Imagine a character who lives here. What do they look like? What do they do?",
  "What sounds would you hear in this world? Birds? Music? Something weird?",
  "Can you add something that doesn't belong? Something surprising?",
  "What would happen if everything in your world was upside down?",
  "Try adding something really tiny next to something really big!",
  "What if the sky changed color? What mood would that create?",
  "Every world needs a mystery. What's the mystery in yours?",
  "What story is happening in your world right now?",
  "What would a visitor notice first when they arrive here?",
  "Can you make something that shows how you're feeling today?",
  "What if you could only use round shapes? Or only pointy ones?",
  "Add something that moves. What is it and where does it go?",
  "What would this world look like from really far away? Like from space?",
  "Try making a path. Where does it lead?",
];

export async function POST(request: NextRequest) {
  const body = await request.json();
  const { message, context } = body;

  const apiKey = process.env.OPENAI_API_KEY;

  if (apiKey) {
    try {
      const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          model: "gpt-4o-mini",
          messages: [
            {
              role: "system",
              content: `You are a warm, encouraging creative companion for children under 12 who are building 3D worlds. Keep responses SHORT (1-2 sentences max). Be playful, use simple words. Never be critical. Always encourage experimentation. Ask imagination-sparking questions. The child's world has ${context.objectCount} objects (${context.objectNames.join(", ")}) and uses a "${context.theme}" theme.`,
            },
            { role: "user", content: message },
          ],
          max_tokens: 100,
          temperature: 0.9,
        }),
      });

      const data = await response.json();
      const reply = data.choices?.[0]?.message?.content ?? getRandomPrompt();
      return NextResponse.json({ reply });
    } catch {
      return NextResponse.json({ reply: getRandomPrompt() });
    }
  }

  return NextResponse.json({ reply: getContextualPrompt(message, context) });
}

function getRandomPrompt(): string {
  return CREATIVE_PROMPTS[Math.floor(Math.random() * CREATIVE_PROMPTS.length)];
}

function getContextualPrompt(
  message: string,
  context: { objectCount: number; objectNames: string[]; theme: string }
): string {
  if (context.objectCount === 0) {
    return "Your world is empty — like a blank page! What's the first thing you want to place? Something big or something tiny?";
  }

  if (context.objectCount < 3) {
    return `Nice start! You have ${context.objectCount} thing${context.objectCount > 1 ? "s" : ""} in your world. What else would make this place feel alive?`;
  }

  if (message.toLowerCase().includes("story")) {
    return `Ooh, a story! Look at your world with ${context.objectNames.join(" and ")}. What just happened? What happens next?`;
  }

  if (message.toLowerCase().includes("weird") || message.toLowerCase().includes("strange")) {
    return "I love weird! What if you put something in your world that really doesn't belong there? Like a giant donut in the ocean? Go wild!";
  }

  return CREATIVE_PROMPTS[Math.floor(Math.random() * CREATIVE_PROMPTS.length)];
}
