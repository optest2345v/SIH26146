# SIH26146 Project Context System

This package is designed to be merged into the SIH26146 project root.

## What to keep

- `MASTER_PROJECT_PROMPT.md` — the foundational project specification. Keep this file as the authoritative high-level definition of the project. It should not be rewritten casually.
- `PROJECT_CONTEXT.md` — the small entry-point context file. Keep this short and current.
- `docs/` — specialized persistent documentation. Update only the files relevant to a change.
- `AGENTS.md` / `CLAUDE.md` — lightweight agent entry instructions that point AI tools to the documentation system.
- `temporary/` — disposable working memory. Do not treat it as authoritative project knowledge.

## First-time setup

1. Extract this package into the SIH26146 project root.
2. Keep your existing `src/`, `tests/`, `data/`, `models/` and application files if they already exist; merge rather than replace them.
3. Review `PROJECT_CONTEXT.md` and update the `current_status` section only after inspecting the actual repository.
4. Read `docs/AI_DOCUMENTATION_INSTRUCTION.md` before giving an AI agent ongoing implementation work.
5. Let the AI read `PROJECT_CONTEXT.md` and `docs/00-index.md` first, then only the relevant specialist documents.

## Source-of-truth hierarchy

1. Latest authoritative SIH/sponsor requirement
2. `MASTER_PROJECT_PROMPT.md`
3. Relevant specialist document under `docs/`
4. Accepted decisions in `docs/10-decisions.md`
5. Current implementation in code
6. `docs/14-what-the-ai-has-done.md`
7. `temporary/`
8. AI assumptions

When a conflict exists, document it; do not silently choose one interpretation.

## Token / credit principle

Do not send the entire Master Prompt on every task. Use the routing strategy in `docs/AI_DOCUMENTATION_INSTRUCTION.md`. The expected everyday load is usually:

`PROJECT_CONTEXT.md` + `docs/00-index.md` + 1–3 relevant specialist files.
