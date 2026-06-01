# AI-Driven 3D Creative Learning Platform Prompt

Build an AI-driven creative learning platform for children under Grade 6 where they can create, explore, and interact with their own 3D worlds.

## Project Goal

Design an immersive, playful, and highly intuitive learning experience where creation itself is the learning process. The product should help children express ideas, stories, emotions, and concepts by building simple 3D environments and objects, while an AI creative partner guides their imagination through prompts, variations, and reflection.

## Core Problem to Solve

Most educational tools focus on content delivery and knowledge acquisition, but do not actively develop creativity, imagination, artistic expression, and divergent thinking. Existing AI and 3D tools are often too technical, too open-ended without support, or disconnected from learning goals. This product should close that gap by making AI-assisted 3D creation accessible, structured, and meaningful for young learners.

## Target Users

- Primary school students, especially children below Grade 6
- Learners in arts, storytelling, language, humanities, and informal creative learning
- Teachers and facilitators who need a low-friction classroom-friendly tool

## Product Vision

Create a child-friendly platform where students move from consumers to creators. They should be able to imagine a world, build it visually, place characters and objects, modify scenes, test ideas, and reflect on what they made. AI should act as a creative partner, not an answer machine.

## Key Product Principles

- Creation-first, not content-first
- AI guides thinking, not replaces it
- Build -> test -> modify -> reflect loop
- Very low barrier to entry
- Intuitive and playful interactions
- Structured openness with light scaffolding
- Classroom-friendly and also usable independently at home

## Main Experience Flow

1. A child starts with a creative challenge, theme, or blank canvas.
2. The AI asks simple imagination prompts such as:
   - "What kind of world do you want to build?"
   - "Who lives here?"
   - "What happens in this place?"
   - "What if it became night, underwater, or giant-sized?"
3. The child creates a 3D world using simple drag-and-drop blocks, environments, props, colors, characters, and effects.
4. The child can enter or preview the world and interact with it.
5. The AI suggests creative extensions, variations, or reflection prompts.
6. The child edits the world iteratively.
7. The child saves, shares, presents, or explores worlds created by others.

## Essential Features

- Child-friendly onboarding with almost no setup
- 3D world builder with simple manipulation:
  - place objects
  - move, rotate, and scale
  - change colors or textures
  - choose environment themes
  - add simple animations or interactions
- AI creative partner panel for:
  - idea prompting
  - "what if" questions
  - story expansion
  - creative constraints
  - reflection prompts
- Creative challenge modes:
  - storytelling
  - build a habitat
  - build a dream world
  - build a place from a book
  - build an emotion as a world
- Iteration loop support:
  - versioning or undo/redo
  - remix mode
  - revise based on prompts
- Simple interaction mode:
  - explore the world
  - click objects for reactions
  - trigger animations
  - scene transitions
- Gallery and sharing:
  - save creations
  - view classmates' or community worlds
  - reflect on different perspectives
- Teacher and facilitator support:
  - assign prompts
  - monitor student creations
  - optional reflection questions

## AI Behavior Requirements

- AI should never dominate the creative process
- AI must guide through short, age-appropriate prompts
- AI should encourage experimentation, not perfection
- AI should offer options instead of single "correct" answers
- AI responses must be safe, warm, simple, and child-appropriate
- AI should support divergent thinking with prompts like:
  - "Can you make it stranger?"
  - "What would happen if gravity changed?"
  - "Can your world tell a feeling?"
  - "What is missing from this place?"
- AI can suggest:
  - new objects
  - changes in mood
  - alternate story paths
  - challenges and mini-missions
  - reflection questions after creation

## UX/UI Requirements

- Design for children first
- Big click and tap targets
- Minimal text, strong visual guidance
- Friendly, playful, calm visual style
- No cluttered dashboards
- Keep the interface simple and obvious
- Use progressive disclosure so advanced options appear only when needed
- Ensure accessibility for different digital literacy levels
- Responsive design for desktop and tablet
- Avoid complex menus and technical terminology

## Learning Design Requirements

- The product must clearly show learning value through creative expression
- Support creative confidence, imagination, experimentation, reflection, and communication
- Do not frame activities as tests
- Use light scaffolding instead of rigid instructions
- Include optional reflection questions such as:
  - "Why did you build it this way?"
  - "What feeling does your world show?"
  - "What changed after your first idea?"
  - "What would you build next?"

## Suggested App Structure

- Landing page
- Child onboarding or start screen
- World builder workspace
- AI creative companion sidebar or floating guide
- Play or explore mode
- Gallery or sharing mode
- Teacher prompt dashboard for a simple MVP

## Suggested MVP Scope

Build a polished MVP that includes:

- child onboarding
- one 3D world builder
- drag-and-drop object placement
- simple environment customization
- AI prompt assistant
- play mode to explore created worlds
- save and load projects
- basic gallery

## Recommended Tech Direction

- Frontend: Next.js + TypeScript
- 3D: React Three Fiber + Drei
- Styling: Tailwind CSS
- State: lightweight and simple
- AI: OpenAI API for prompt guidance and creative interaction
- Storage: simple database or local/cloud project persistence
- Keep the architecture clean, modular, and easy to extend

## Implementation Constraints

- Prioritize simplicity over feature overload
- Every feature must support creativity or reflection
- Avoid making this feel like a professional 3D editor
- Avoid overly game-like mechanics unless they directly support learning
- Keep performance smooth on typical school devices
- Make onboarding possible in under 1 minute

## Output I Want From You

1. Product concept summary
2. User personas
3. Core user journeys
4. Feature list prioritized for MVP
5. Information architecture
6. UX/UI design direction
7. Technical architecture
8. Database schema proposal
9. AI prompt system design
10. Safety and moderation considerations for children
11. Step-by-step implementation plan
12. Starter code structure for the MVP
13. Screens and components to build first

## Important

This should feel magical, creative, and empowering for children, but also practical for classrooms. The product must make children feel that their ideas matter and that building worlds is a way of thinking, learning, and expressing themselves.
