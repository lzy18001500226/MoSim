---
id: doc-reflexes
name: Doc Reflexes
description: Automatically documents non-obvious decisions and changes
icon: doc-reflexes.png
category: documentation
activationTriggers:
  - document
  - explain
  - readme
  - comment
  - why
---

# Instructions

Automatically document non-obvious decisions, API changes, and setup requirements.

## Behavioral Guidelines

- Document the "why", not just the "what"
- Update READMEs with new setup steps
- Add JSDoc for public APIs
- Include examples in documentation
- Keep docs close to code
- Update docs with code changes

## What to Document

- Non-obvious design decisions
- API contracts and breaking changes
- Setup and configuration steps
- Known limitations and workarounds
- Performance characteristics
- Security considerations

## Documentation Examples

```typescript
/**
 * Retries failed operations with exponential backoff.
 *
 * @remarks
 * Uses jitter to prevent thundering herd in distributed systems.
 * Max delay capped at 30s to prevent blocking too long.
 *
 * @param operation - Async function to retry
 * @param maxRetries - Maximum retry attempts (default: 3)
 * @returns Result of successful operation
 * @throws Last error after all retries exhausted
 */
async function withRetry<T>(
  operation: () => Promise<T>,
  maxRetries = 3
): Promise<T>
```
