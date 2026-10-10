# Project plan and execution checklist

## Approval gate

This document is the implementation plan for the project. The agent must complete the work in the sequence below and only move forward when the user reviews and approves the plan.

The agent is expected to maintain a checklist, mark progress as it completes each item, and use the stated tests and success criteria as the definition of done for each phase.

---

## Part 1: Plan

### Checklist

- [ ] Review the root project requirements in [AGENTS.md](../AGENTS.md) and confirm the project constraints.
- [ ] Review the existing frontend demo in [frontend](../frontend) and capture the current state, stack, and architecture.
- [ ] Write a frontend-specific AGENTS file in [frontend/AGENTS.md](../frontend/AGENTS.md) describing the existing code and how the demo is organized.
- [ ] Expand this plan document into a detailed execution plan with substeps, tests, and success criteria for each remaining phase.
- [ ] Present the plan to the user and wait for explicit approval before starting implementation work.

### Tests and validation

- No code changes are required beyond documentation in this phase.
- Validation is a review step: confirm that the plan matches the user requirements, technical constraints, and the current frontend state.

### Success criteria

- The project owner understands the exact roadmap.
- The frontend AGENTS file explains the current codebase enough for future work to start safely.
- The plan clearly shows what is implemented in each phase, what will be tested, and how success is measured.

---

## Part 2: Scaffolding

### Checklist

- [ ] Create the Docker configuration required to run the app locally.
- [ ] Create the FastAPI backend app under [backend](../backend) with a minimal working service.
- [ ] Add a simple health or hello-world route that confirms the backend is running.
- [ ] Add a second backend route or example response proving API access works locally.
- [ ] Add start and stop scripts under [scripts](../scripts) for Mac, Windows, and Linux.
- [ ] Ensure the app can run locally and the backend responds to a local request.

### Tests

- Backend smoke test: confirm a local request returns the expected success response.
- Docker smoke check: container starts successfully and exposes the app locally.
- Static served hello-world check: confirm an HTTP response is returned from the local stack.

### Success criteria

- The app can be started from the project root using the provided scripts.
- The backend is reachable over HTTP.
- A minimal static or health response proves the infrastructure is working before feature development begins.

---

## Part 3: Add in Frontend

### Checklist

- [ ] Integrate the existing Next.js frontend into the app container so it is built and served from the backend.
- [ ] Ensure the app loads at the root route `/` and displays the demo Kanban board.
- [ ] Preserve the current frontend functionality, including the column layout, drag-and-drop board interactions, and add-card workflow.
- [ ] Verify the static build process completes successfully.
- [ ] Add or retain frontend unit tests and end-to-end tests covering board rendering and card interaction.

### Tests

- `npm run test:unit` for the frontend logic and render-level tests.
- `npm run test:e2e` for browser-level checks of the home page and kanban behavior.
- Production build verification: `npm run build` succeeds.

### Success criteria

- The board appears at `/` when the app is running.
- Existing board interactions continue to work without regression.
- Unit and e2e tests pass for the frontend demo experience.

---

## Part 4: Fake user sign in experience

### Checklist

- [ ] Add a sign-in experience on first visit to `/`.
- [ ] Use the dummy credentials `user` / `password` to allow access to the board.
- [ ] Prevent the Kanban board from rendering until authentication succeeds.
- [ ] Add a sign-out flow that clears the session state and returns the user to the login screen.
- [ ] Protect the app from unauthorized access to the board route.

### Tests

- Unit test for login validation and failure state.
- Unit test for successful sign-in redirect to the board.
- Unit test for sign-out returning the user to the login screen.
- E2E test covering sign-in and sign-out flow.

### Success criteria

- A user cannot access the Kanban without valid credentials.
- Correct credentials unlock the workspace.
- Sign-out clears access and returns to a secure login state.

---

## Part 5: Database modeling

### Checklist

- [ ] Define the board data model for a signed-in user.
- [ ] Include board, column, and card structure in a schema proposal.
- [ ] Save the schema as JSON in the docs directory.
- [ ] Document SQLite usage and planned future multi-user support within the implementation approach.
- [ ] Present the schema to the user for approval before implementing persistence.

### Tests

- Schema review against the actual data model used by the frontend and backend.
- Validation that the proposed structure supports column names, card contents, positions, and user ownership.

### Success criteria

- The schema is clear, realistic, and consistent with the MVP requirements.
- The user approves the persistence model before code is written against it.
- The database design supports the future expansion to multiple users without breaking the current MVP structure.

---

## Part 6: Backend API

### Checklist

- [ ] Create database initialization so SQLite is created automatically if missing.
- [ ] Add a user model and board model aligned with the approved schema.
- [ ] Implement API routes to read the user's board.
- [ ] Implement API routes to update the board, columns, and cards for the signed-in user.
- [ ] Validate that updates are persisted to SQLite and returned in the expected format.
- [ ] Add backend unit tests covering read, write, and edge cases.

### Tests

- Backend unit tests for creating a new board and user data.
- Tests for reading existing board state.
- Tests for adding, renaming, moving, and deleting cards.
- Tests for invalid or missing data handling.

### Success criteria

- The database is created automatically when absent.
- Board updates are durable and retrievable.
- Backend tests show correct CRUD behavior for the Kanban data.

---

## Part 7: Frontend + Backend integration

### Checklist

- [ ] Replace local-only demo state with API-backed board reads and writes.
- [ ] Ensure the frontend authenticates as the current mock user and loads the correct Kanban board.
- [ ] Sync all board actions (rename, move, add, delete) to the backend.
- [ ] Handle loading and error states gracefully while data is being fetched or saved.
- [ ] Verify that the board persists across page reloads.

### Tests

- E2E tests for creating and persisting a board state.
- Unit/integration tests for API fetch and state synchronization.
- Regression checks for drag-and-drop and card editing behavior.

### Success criteria

- The board is persistent across sessions for the signed-in user.
- The UI reflects the backend state after every update.
- Existing user interaction flows still work with persisted data.

---

## Part 8: AI connectivity

### Checklist

- [ ] Configure the backend to call OpenRouter using the approved model.
- [ ] Load the API key from the environment and validate that it is present.
- [ ] Test connectivity with a simple prompt such as `2 + 2`.
- [ ] Confirm the backend can receive and parse a successful AI response.
- [ ] Document the failure modes for network, authentication, and model errors.

### Tests

- Local AI connectivity smoke test using a trivial prompt.
- Error-path test when the API key is missing or invalid.
- Validation that the backend logs or surfaces model failures cleanly.

### Success criteria

- The backend can successfully call the AI service.
- A simple prompt receives a valid response.
- The system is stable and debug-friendly when AI requests fail.

---

## Part 9: Structured AI board actions

### Checklist

- [ ] Send the Kanban JSON and the current user prompt to the AI call.
- [ ] Include relevant conversation history in the request payload.
- [ ] Require structured output from the model that includes both a user-facing response and any optional Kanban update.
- [ ] Validate the response schema before applying any board change.
- [ ] Apply only safe, validated board updates from AI output.
- [ ] Add concurrency and schema-validation safeguards around AI-driven edits.

### Tests

- Unit tests for request payload composition.
- Tests verifying AI structured output validation.
- Tests for safe board update handling when the model suggests no change.
- Tests for invalid or malformed AI responses.

### Success criteria

- The AI can act on board state and produce structured output in a predictable format.
- Invalid responses do not break the app or corrupt board state.
- User-facing AI responses and board updates remain consistent and understandable.

---

## Part 10: AI sidebar chat UI

### Checklist

- [ ] Add a sidebar to the main board layout for AI chat.
- [ ] Support user prompts and conversation history.
- [ ] Allow the LLM to update the board when its structured output includes valid changes.
- [ ] Automatically refresh the board after accepted AI updates.
- [ ] Make the UI visually aligned with the existing design language and color palette.
- [ ] Ensure the AI chat remains usable without breaking the board interactions.

### Tests

- E2E tests for sending a prompt and seeing a response.
- E2E tests for AI-driven board mutation and page refresh.
- Regression checks for drag-and-drop, add-card, and rename flows while the sidebar is open.

### Success criteria

- The user can chat with the AI from the board UI.
- Accepted AI updates modify the board and reflect immediately.
- The board remains responsive and visually consistent after AI-driven changes.

---

## Definition of done

The project is considered done only when:

- All checklist items in each phase have been completed.
- Every phase has passed the required tests and validation steps.
- The final app runs locally in Docker with proper backend, frontend, and AI connectivity.
- The project matches the business requirements and documented constraints.
- The user has reviewed and approved the implementation outcome.
