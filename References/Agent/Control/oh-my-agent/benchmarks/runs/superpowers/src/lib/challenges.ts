import type { CreativeChallenge } from "@/types/world";

export const CHALLENGES: CreativeChallenge[] = [
  {
    id: "dream-world",
    title: "Dream World",
    description: "Build a world from your wildest dream!",
    prompts: [
      "What did you see in your dream?",
      "Was it daytime or nighttime?",
      "Who was there with you?",
    ],
    category: "dream",
  },
  {
    id: "ocean-habitat",
    title: "Ocean Home",
    description: "Create a home under the sea!",
    prompts: [
      "What creatures live here?",
      "Is the water warm or cold?",
      "What is hidden on the ocean floor?",
    ],
    theme: "ocean",
    category: "habitat",
  },
  {
    id: "story-land",
    title: "Story Land",
    description: "Build a world for your favorite story!",
    prompts: [
      "What story are you thinking of?",
      "Where does the story take place?",
      "Who is the main character?",
    ],
    category: "book",
  },
  {
    id: "happy-place",
    title: "Happy Place",
    description: "Build a place that shows happiness!",
    prompts: [
      "What makes you happy?",
      "What colors feel happy to you?",
      "What things would be in your happiest place?",
    ],
    category: "emotion",
  },
  {
    id: "candy-kingdom",
    title: "Candy Kingdom",
    description: "Create a sweet kingdom made of treats!",
    prompts: [
      "What is the castle made of?",
      "Who rules the candy kingdom?",
      "What is the sweetest part?",
    ],
    theme: "candy",
    category: "dream",
  },
  {
    id: "space-station",
    title: "Space Station",
    description: "Build a station floating in space!",
    prompts: [
      "What can you see from the windows?",
      "Who lives on the station?",
      "What is the coolest room?",
    ],
    theme: "space",
    category: "storytelling",
  },
];
