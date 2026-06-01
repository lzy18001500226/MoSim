# Agor UI

UI components for Agor - Agent Orchestrator

## Tech Stack

- **Vite + React + TypeScript** - Fast, modern development
- **Ant Design** - UI component library
- **React Flow** - Interactive session tree canvas
- **Storybook** - Component development and documentation

## Getting Started

```bash
# Install dependencies
npm install

# Run Storybook (component development)
npm run storybook

# Run type checking
npm run typecheck

# Run linter
npm run lint

# Build for production
npm run build
```

## Project Structure

```
src/
├── types/          # TypeScript type definitions
│   ├── session.ts  # Session types
│   ├── task.ts     # Task types
│   └── concept.ts  # Concept types
│
├── components/     # React components
│   ├── TaskListItem/
│   ├── SessionCard/
│   └── SessionCanvas/
│
└── mocks/          # Mock data for Storybook
    ├── sessions.ts
    ├── tasks.ts
    └── concepts.ts
```

## Components

### TaskListItem

Compact task display showing status, description, and metadata.

### SessionCard

Session information card containing tasks, git state, concepts, and genealogy.

### SessionCanvas

Interactive canvas for visualizing session trees with React Flow.

## Development

- **Storybook**: http://localhost:6006/
- All components have `.stories.tsx` files for isolated development
- Mock data available in `src/mocks/`

## Scripts

- `npm run dev` - Start Vite dev server
- `npm run storybook` - Start Storybook
- `npm run typecheck` - Run TypeScript type checking
- `npm run lint` - Run Biome linter
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Linting

This project uses [Biome](https://biomejs.dev/) for linting and formatting. Configuration is in the root `biome.json` file, which includes:

- React hooks validation
- Accessibility (a11y) rules
- Unused imports/variables detection
- Consistent code formatting

Biome automatically runs on all files via pre-commit hooks (lint-staged).
