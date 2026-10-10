# Database approach

## Summary

The MVP will use SQLite as the local database layer. SQLite is a good fit for this project because it is file-based, simple to run in a container, and easy to initialize on first use without external services.

## Design decisions

- SQLite is stored as a local file in the project environment.
- The database is created automatically if it does not already exist.
- The schema is intentionally straightforward and aligned with the Kanban board data model already used by the frontend.
- The MVP supports a single board per user, while the schema is still structured for future multi-user expansion.

## Schema model

The database uses a relational structure rather than storing a single JSON blob for the full board:

- users: stores user accounts
- boards: stores the board metadata for each user
- columns: stores column definitions and their order
- cards: stores card details, content, and current column placement

This keeps the model easy to query and update while preserving the same logical board representation the UI already expects.

## Why this fits the MVP

The current project requirements are intentionally narrow:

- one default user with hardcoded credentials
- one board per user
- editable column titles
- draggable cards across columns
- persisted card data inside the local SQLite database

The column and card tables support all of this without adding unnecessary complexity.

## JSON schema

The full database structure proposal is saved in [kanban-database-schema.json](kanban-database-schema.json).

## Future extension path

When the app grows beyond the MVP, the schema can support:

- multiple users with separate boards
- multiple board records per user
- additional board metadata such as labels or statuses
- richer card metadata or comments
- audit/history tables for board changes

## Sign-off

This schema is ready for review and approval before moving into backend persistence work.
