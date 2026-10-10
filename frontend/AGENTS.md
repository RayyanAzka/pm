# Frontend agent guide

## Purpose

This frontend is a demo Kanban board application built as a Next.js + React + TypeScript app. It is currently a frontend-only prototype and is not yet wired into the Docker deployment, backend API, or user authentication flow.

The current goal is to provide a working Kanban board experience with drag-and-drop card movement, column renaming, and card creation/deletion.

## Stack

- Next.js 16
- React 19
- TypeScript
- @dnd-kit for drag-and-drop interactions
- Vitest for unit tests
- Playwright for browser-level tests
- Tailwind CSS for styling

## High-level structure

### app/

- `src/app/layout.tsx`: root layout, app metadata, and font setup.
- `src/app/page.tsx`: renders the main board by mounting `KanbanBoard`.
- `src/app/globals.css`: theme tokens and styling variables matching the project color system.

### components/

- `KanbanBoard.tsx`: main board state container. It owns the `board` state, drag handlers, column rename logic, card creation, and card deletion.
- `KanbanColumn.tsx`: renders a single board column, handles droppable column area, and manages each column’s visible card list.
- `KanbanCard.tsx`: displays a card with its title and details.
- `KanbanCardPreview.tsx`: lightweight drag preview used during drag operations.
- `NewCardForm.tsx`: inline form opened to add a new card to a column.

### lib/

- `kanban.ts`: contains the board data model and move logic.
  - `BoardData`, `Column`, and `Card` define the board schema.
  - `initialData` is the starter board state.
  - `moveCard` handles drag-and-drop movement between columns and within a column.
  - `createId` creates IDs used for new cards.

### tests/

- `src/lib/kanban.test.ts`: tests the board movement logic.
- `src/components/KanbanBoard.test.tsx`: tests user interactions such as renaming columns and adding/removing cards.
- `tests/kanban.spec.ts`: Playwright browser tests for key user flows.
- `src/test/setup.ts`: test setup for the frontend test environment.

## Current app behavior

The app currently:

- renders a five-column Kanban board with sample cards;
- allows columns to be renamed inline;
- supports drag-and-drop card movement across columns;
- allows adding new cards to a column;
- allows deleting cards from a column;
- uses a fixed theme with the project color palette.

## Project constraints to keep in mind

- This is a demo and not yet connected to any backend persistence.
- There is no real login flow yet.
- There is no AI integration yet.
- This UI is designed to later be served by the FastAPI backend.
- The board model should keep the shapes and logic simple and compatible with future API-backed persistence.

## Validation commands

Run from the `frontend` directory:

```bash
npm install
npm run test
npm run test:e2e
npm run build
```

## Working guidance for future implementation

- Keep the board model simple and JSON-friendly so it can eventually be persisted in SQLite.
- Prefer the existing shape of `BoardData` and `Column` when adding backend or API features.
- Preserve the current UI patterns and theme variables before adding authentication or AI chat.
- Add tests before changing the board behavior, especially for drag-and-drop logic and state transitions.

## Important note

This frontend is not yet integrated with the production architecture. Any future work should treat it as the current visual and interaction baseline for a later API-backed project management app.
