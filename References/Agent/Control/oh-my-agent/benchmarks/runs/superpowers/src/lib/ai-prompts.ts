import type { World, EnvironmentTheme } from "@/types/world";

const THEME_DESCRIPTIONS: Record<EnvironmentTheme, string> = {
  meadow: "a sunny green meadow with soft grass",
  desert: "a warm sandy desert with dunes",
  ocean: "a deep blue ocean world with waves",
  space: "a sparkly outer space with stars",
  forest: "a magical forest with tall trees",
  snow: "a snowy winter wonderland",
  candy: "a sweet candy land with treats everywhere",
  volcano: "a dramatic volcanic landscape",
};

export function getSystemPrompt(): string {
  return `You are a friendly, warm, and encouraging creative companion for children in elementary school (under Grade 6). Your name is Sparky.

Your role:
- Guide children's creativity through short, playful prompts
- Ask "what if" questions to spark imagination
- Never give long answers — keep responses to 1-2 short sentences
- Use simple, age-appropriate language
- Encourage experimentation and divergent thinking
- Never judge or correct creative choices
- Suggest ideas as options, never as commands
- Be warm, enthusiastic, and supportive
- Use occasional fun expressions but don't overdo it

You must NEVER:
- Give complex or technical instructions
- Use scary, violent, or inappropriate content
- Dominate the creative process
- Give single "correct" answers
- Use words children wouldn't understand

Response format:
- Keep responses under 30 words
- Ask one question or give one suggestion at a time
- Use simple punctuation`;
}

export function getCreativePrompt(world: World): string {
  const objectCount = world.objects.length;
  const themeDesc = THEME_DESCRIPTIONS[world.theme];

  if (objectCount === 0) {
    return `The child just started building a new world called "${world.name}" set in ${themeDesc}. The world is empty. Give a short, excited welcome and ask what they want to place first.`;
  }

  const objectNames = world.objects.map((o) => o.name).join(", ");

  if (objectCount < 3) {
    return `The child is building "${world.name}" in ${themeDesc}. They have placed: ${objectNames}. Ask a fun "what if" question or suggest what might go well with what they've built.`;
  }

  if (objectCount < 6) {
    return `The child's world "${world.name}" in ${themeDesc} now has: ${objectNames}. Their world is growing! Ask an imagination question about what happens in this place or who lives here.`;
  }

  return `The child has built a rich world "${world.name}" in ${themeDesc} with: ${objectNames}. Encourage them with a reflection question about their world or suggest a creative twist like changing the time of day or adding a story element.`;
}

export function getWhatIfPrompts(): string[] {
  return [
    "What if everything was upside down?",
    "What if it suddenly became nighttime?",
    "What if a friendly dragon visited?",
    "What if everything could talk?",
    "What if it started raining colors?",
    "What if your world was underwater?",
    "What if everything was giant-sized?",
    "What if everything was tiny?",
    "What if a magical door appeared?",
    "What if gravity stopped working?",
  ];
}

export function getReflectionPrompts(): string[] {
  return [
    "Why did you build it this way?",
    "What feeling does your world show?",
    "What would you change if you started over?",
    "What story is hiding in your world?",
    "If you could live here, what would you do first?",
    "What sounds would you hear in this place?",
    "What is your favorite part?",
    "What would you build next?",
  ];
}

export function getStarterPrompts(): string[] {
  return [
    "What kind of world do you want to build?",
    "Who lives in your world?",
    "What happens in this place?",
    "Is your world happy, mysterious, or exciting?",
    "What colors do you see in your imagination?",
  ];
}
