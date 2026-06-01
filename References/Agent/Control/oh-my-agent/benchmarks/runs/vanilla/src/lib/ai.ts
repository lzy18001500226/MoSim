import { AIMessage, WorldObject, EnvironmentTheme } from '@/types';
import { v4 as uuid } from 'uuid';

const GREETING_PROMPTS = [
  "Hi there, creative builder! What kind of world do you want to make today?",
  "Welcome back, imagination explorer! Ready to build something amazing?",
  "Hello, world creator! I'm your creative buddy. What shall we build?",
];

const EMPTY_WORLD_PROMPTS = [
  "Your world is a blank canvas! Try placing some objects to get started. What do you see in your imagination?",
  "Every great world starts with one thing. What's the first thing you'd place in your world?",
  "Close your eyes and imagine a place. What's the very first thing you notice there?",
];

const FEW_OBJECTS_PROMPTS = [
  "Nice start! Who lives in this world? Maybe add a character or animal!",
  "Looking good! What sounds would you hear in this place?",
  "Great beginning! What would make this place feel more alive?",
  "I like what you've made! What's the story of this world?",
];

const MANY_OBJECTS_PROMPTS = [
  "Wow, your world is growing! What happens here when the sun goes down?",
  "This is amazing! If I were tiny and walked through your world, what would I discover?",
  "Your world has so much in it! What's the most important part?",
  "Beautiful world! What if something magical happened here right now?",
];

const WHAT_IF_PROMPTS = [
  "What if everything in your world could float?",
  "What if your world was the size of a teacup?",
  "What if a friendly giant visited your world?",
  "What if it rained colors in your world?",
  "What if time moved backwards here?",
  "What if everything could talk - what would they say?",
  "What if your world was made of candy?",
  "What if this world existed on a cloud?",
];

const REFLECTION_PROMPTS = [
  "Why did you choose these colors for your world?",
  "What feeling does your world give you?",
  "If you could step into your world, what would you do first?",
  "What's the story behind your world?",
  "What would you change if you started over?",
  "What's your favorite part of what you've built?",
];

const THEME_PROMPTS: Record<EnvironmentTheme, string[]> = {
  meadow: [
    "What creatures live in this meadow?",
    "Is there a secret path hidden in the grass?",
  ],
  night: [
    "What glows in the darkness of your night world?",
    "Who is awake when everyone else is sleeping?",
  ],
  underwater: [
    "What's at the very bottom of your ocean?",
    "Do the fish have names? What are they?",
  ],
  space: [
    "What planet are we orbiting?",
    "Have any aliens visited your space station?",
  ],
  desert: [
    "What's hiding under the sand?",
    "Is there an oasis somewhere in your desert?",
  ],
  snow: [
    "What's the warmest thing in your snow world?",
    "Do snowflakes look different here?",
  ],
  sunset: [
    "What happens when the sun finally sets?",
    "Who is watching this sunset with you?",
  ],
  candy: [
    "What flavor is the ground?",
    "Does everything taste as good as it looks?",
  ],
};

function pickRandom<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

export function getGreeting(): AIMessage {
  return {
    id: uuid(),
    role: 'ai',
    content: pickRandom(GREETING_PROMPTS),
    timestamp: new Date().toISOString(),
    suggestions: ['A magical forest', 'An underwater kingdom', 'A space adventure'],
  };
}

export function getContextualPrompt(
  objects: WorldObject[],
  theme: EnvironmentTheme,
  messageCount: number
): AIMessage {
  let content: string;
  let suggestions: string[] | undefined;

  if (objects.length === 0) {
    content = pickRandom(EMPTY_WORLD_PROMPTS);
    suggestions = ['Add a tree', 'Place a house', 'Try an animal'];
  } else if (objects.length < 4) {
    content = pickRandom(FEW_OBJECTS_PROMPTS);
    suggestions = ['Add more objects', 'Change colors', 'Try a new theme'];
  } else if (messageCount > 0 && messageCount % 5 === 0) {
    content = pickRandom(REFLECTION_PROMPTS);
  } else if (messageCount > 0 && messageCount % 3 === 0) {
    content = pickRandom(WHAT_IF_PROMPTS);
    suggestions = ['Try it!', 'Tell me more', 'Something else'];
  } else {
    const themePrompts = THEME_PROMPTS[theme];
    const allPrompts = [...MANY_OBJECTS_PROMPTS, ...themePrompts];
    content = pickRandom(allPrompts);
    suggestions = ['Good idea!', 'What if...', 'Help me think'];
  }

  return {
    id: uuid(),
    role: 'ai',
    content,
    timestamp: new Date().toISOString(),
    suggestions,
  };
}

export function respondToChild(childMessage: string, objects: WorldObject[], theme: EnvironmentTheme): AIMessage {
  const lower = childMessage.toLowerCase();

  let content: string;
  let suggestions: string[] | undefined;

  if (lower.includes('help') || lower.includes("don't know")) {
    content = "That's okay! There's no wrong way to build. Try placing any object and see how it feels. You can always change it later!";
    suggestions = ['Show me ideas', 'Pick for me', "I'll try something"];
  } else if (lower.includes('done') || lower.includes('finished')) {
    content = pickRandom(REFLECTION_PROMPTS);
    suggestions = ['Save my world', 'Keep building', 'Explore it'];
  } else if (lower.includes('what if') || lower.includes('idea')) {
    content = pickRandom(WHAT_IF_PROMPTS);
    suggestions = ['Try it!', 'Another idea', 'I like this one'];
  } else if (lower.includes('story') || lower.includes('tell')) {
    content = "Every world has a story! Look at what you've built - who lives here? What happened today in this world? What will happen tomorrow?";
    suggestions = ['A adventure!', 'A mystery!', 'A day in the life'];
  } else {
    content = `That's a great thought! ${pickRandom(MANY_OBJECTS_PROMPTS)}`;
    suggestions = ['Tell me more', 'What else?', 'Help me build'];
  }

  return {
    id: uuid(),
    role: 'ai',
    content,
    timestamp: new Date().toISOString(),
    suggestions,
  };
}

export const CHALLENGES = [
  {
    id: '1',
    title: 'My Dream Treehouse',
    description: 'Build the coolest treehouse you can imagine! What would it look like? Who would visit?',
    prompts: ['What makes your treehouse special?', 'How do you get up to it?', 'What can you see from the top?'],
    theme: 'meadow' as EnvironmentTheme,
    category: 'dream' as const,
  },
  {
    id: '2',
    title: 'Ocean Explorer',
    description: 'Create an underwater world full of amazing sea creatures and hidden treasures!',
    prompts: ['What lives in the deepest part?', 'Is there a sunken ship?', 'What colors do you see?'],
    theme: 'underwater' as EnvironmentTheme,
    category: 'habitat' as const,
  },
  {
    id: '3',
    title: 'Space Station',
    description: 'Design a space station where astronauts live and work among the stars!',
    prompts: ['What do astronauts do for fun?', 'Can you see Earth from here?', 'What alien friends visit?'],
    theme: 'space' as EnvironmentTheme,
    category: 'dream' as const,
  },
  {
    id: '4',
    title: 'A Feeling as a Place',
    description: 'What does happiness look like as a world? Or excitement? Pick a feeling and build it!',
    prompts: ['What colors is your feeling?', 'Is it loud or quiet?', 'What shape is it?'],
    theme: 'candy' as EnvironmentTheme,
    category: 'emotion' as const,
  },
  {
    id: '5',
    title: 'Story World',
    description: "Build a world from your favorite story or book! Where does the adventure happen?",
    prompts: ['Who is the hero?', 'What is the challenge?', 'How does it end?'],
    theme: 'sunset' as EnvironmentTheme,
    category: 'book' as const,
  },
  {
    id: '6',
    title: 'Animal Kingdom',
    description: 'Create a home for your favorite animals! What do they need to be happy?',
    prompts: ['What do they eat?', 'Where do they sleep?', 'Are they friends?'],
    theme: 'meadow' as EnvironmentTheme,
    category: 'habitat' as const,
  },
];
