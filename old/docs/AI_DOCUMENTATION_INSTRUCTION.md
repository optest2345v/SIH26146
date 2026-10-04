# SIH26146 — AI Documentation Operating Instruction

You are an AI agent working on the SIH26146 project.

The repository contains persistent Markdown documentation. Treat that documentation as the project's long-term memory and use it efficiently.

## 1. First actions on a new session

Read:

1. `PROJECT_CONTEXT.md`
2. `docs/00-index.md`

Then determine which specialist documents are relevant to the task.

Do **not** read the entire documentation tree by default.

## 2. Source-of-truth hierarchy

Use:

1. Latest authoritative sponsor requirement
2. `MASTER_PROJECT_PROMPT.md`
3. Relevant specialist documentation
4. Accepted decisions in `docs/10-decisions.md`
5. Actual code
6. Durable AI work log
7. Temporary notes
8. Your assumptions

When the code conflicts with documentation, surface the conflict.

## 3. Context-loading strategy

### General project understanding

Read:

- `PROJECT_CONTEXT.md`
- `docs/00-index.md`
- relevant part of `MASTER_PROJECT_PROMPT.md` only when necessary

### Requirements

Read:

- `docs/02-requirements.md`

### Architecture

Read:

- `docs/03-architecture.md`
- relevant ADRs in `docs/10-decisions.md`
- `docs/11-current-status.md`

### Data

Read:

- `docs/04-data-contract.md`
- `docs/02-requirements.md`

### Correlation

Read:

- `docs/05-correlation-spec.md`
- `docs/04-data-contract.md`
- `docs/03-architecture.md`
- relevant ADRs

### ML

Read:

- `docs/06-ml-specification.md`
- `docs/04-data-contract.md`
- `docs/05-correlation-spec.md`
- `docs/09-testing-validation.md`

### Dashboard

Read:

- `docs/07-dashboard-spec.md`
- `docs/11-current-status.md`

### Security/privacy

Read:

- `docs/08-security-privacy.md`
- `docs/03-architecture.md`

### Testing

Read:

- `docs/09-testing-validation.md`
- `docs/02-requirements.md`
- `docs/11-current-status.md`

### Current progress

Read:

- `docs/11-current-status.md`

Do not infer completion from old conversations or file existence.

## 4. Information classification

When documenting a claim or decision, distinguish:

- `MANDATORY`
- `REQUIRED BY PROJECT`
- `RECOMMENDED`
- `OPTIONAL`
- `EXPERIMENTAL`
- `PROPOSED`
- `DEPRECATED`
- `UNKNOWN`
- `CONFLICTING`

Never present a recommendation as if it were a sponsor requirement.

## 5. Before changing architecture

Check:

- affected requirements;
- affected data contracts;
- affected interfaces;
- offline compatibility;
- security/privacy;
- tests;
- demo workflow;
- existing accepted decisions.

## 6. After a meaningful change

Update only the relevant documentation:

| Change | File |
|---|---|
| Requirement | `02-requirements.md` |
| Architecture | `03-architecture.md`, `10-decisions.md` if a decision was made |
| Schema | `04-data-contract.md` |
| Correlation | `05-correlation-spec.md` |
| ML | `06-ml-specification.md` |
| UI | `07-dashboard-spec.md` |
| Security | `08-security-privacy.md` |
| Tests | `09-testing-validation.md` |
| Major decision | `10-decisions.md` |
| Current state | `11-current-status.md` |
| Backlog | `12-backlog.md` |
| Reference | `13-references.md` |
| Durable AI change | `14-what-the-ai-has-done.md` |

## 7. Avoid duplication

Each fact should have one primary home. Prefer references over copying large blocks between files.

## 8. Temporary vs permanent knowledge

Put into `temporary/`:

- failed experiments;
- debug notes;
- one-off scratch reasoning;
- discarded ideas;
- temporary logs.

Put into `docs/` only information that future work needs to remain consistent.

## 9. Conflict handling

If documentation says X and code does Y, report:

```text
Documentation:
X

Implementation:
Y

Conflict:
...

Impact:
...

Recommended resolution:
...
```

Do not silently pick one when the difference matters.

## 10. Status discipline

Use:

- NOT STARTED
- PLANNED
- IN PROGRESS
- BLOCKED
- IMPLEMENTED
- TESTED
- VERIFIED
- DEPRECATED
- UNKNOWN

A feature is not complete merely because code exists.

## 11. AI implementation behavior

- Preserve mandatory SIH requirements.
- Prefer the smallest change that solves the requested problem.
- Do not introduce runtime internet dependencies into the core path.
- Do not fabricate data, scores, benchmarks or claims.
- Do not replace genuine ML with rules and still call it ML.
- Preserve explainability and provenance.
- Make uncertainty visible.
- Add tests for meaningful behavioral changes.
- Update documentation after meaningful changes.

## 12. Final project principle

Use the minimum amount of project context necessary to produce a correct result.

`PROJECT_CONTEXT.md` is the entry point.
`docs/00-index.md` is the router.
Specialist docs hold detailed knowledge.
`10-decisions.md` records important reasoning.
`11-current-status.md` records current state.
`temporary/` is disposable memory.

END OF INSTRUCTION
