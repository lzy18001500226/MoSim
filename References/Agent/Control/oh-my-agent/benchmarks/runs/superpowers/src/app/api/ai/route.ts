import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const { type, userMessage, worldContext, systemPrompt } = await request.json();

  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    return NextResponse.json({ error: "API key not configured" }, { status: 500 });
  }

  let prompt = worldContext;
  if (type === "whatif") {
    prompt += " Generate a fun 'what if' question for the child about their world.";
  } else if (type === "reflect") {
    prompt += " Ask a gentle reflection question about why they made their creative choices.";
  } else if (type === "chat" && userMessage) {
    prompt += ` The child said: "${userMessage}". Respond warmly and helpfully.`;
  } else if (type === "greet") {
    prompt += " Give a short, excited greeting to the child who just started building.";
  } else {
    prompt += " Give a short creative suggestion or encouragement.";
  }

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
          { role: "system", content: systemPrompt },
          { role: "user", content: prompt },
        ],
        max_tokens: 80,
        temperature: 0.8,
      }),
    });

    if (!response.ok) {
      return NextResponse.json({ error: "AI request failed" }, { status: 502 });
    }

    const data = await response.json();
    const message = data.choices?.[0]?.message?.content ?? "Let's keep building!";

    return NextResponse.json({ message });
  } catch {
    return NextResponse.json({ error: "AI request failed" }, { status: 500 });
  }
}
