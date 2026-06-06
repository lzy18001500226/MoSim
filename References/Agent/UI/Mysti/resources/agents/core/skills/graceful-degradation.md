---
id: graceful-degradation
name: Graceful Degradation
description: Handles errors and edge cases without catastrophic failure
icon: graceful-degradation.png
category: reliability
activationTriggers:
  - error
  - fallback
  - resilient
  - robust
  - edge case
  - fail
---

# Instructions

Handle errors, edge cases, and unexpected states without catastrophic failure. Build resilient systems.

## Behavioral Guidelines

- Anticipate failure modes
- Provide meaningful fallbacks
- Log errors for debugging
- Never swallow exceptions silently
- Design for partial failures
- Implement circuit breakers where appropriate

## Error Handling Patterns

```typescript
// Good: Graceful degradation with fallback
async function fetchUserData(userId: string) {
  try {
    return await api.getUser(userId);
  } catch (error) {
    logger.warn('API unavailable, using cache', { userId, error });
    return await cache.getUser(userId);
  }
}

// Good: Meaningful error boundaries
if (!config.apiKey) {
  logger.error('Missing API key - falling back to demo mode');
  return DemoProvider.getInstance();
}
```

## Checklist

- [ ] All async operations have error handling
- [ ] Fallbacks exist for external dependencies
- [ ] Errors are logged with context
- [ ] User sees helpful error messages
- [ ] System remains functional in degraded state
