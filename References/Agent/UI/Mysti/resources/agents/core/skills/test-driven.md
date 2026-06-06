---
id: test-driven
name: Test-Driven
description: Writes or updates tests alongside code changes
icon: test-driven.png
category: quality
activationTriggers:
  - test
  - TDD
  - coverage
  - spec
  - unit test
  - integration test
---

# Instructions

Write or update tests alongside code changes. Validate behavior before marking complete.

## Behavioral Guidelines

- Write tests for new functionality
- Update tests when changing behavior
- Run tests before committing
- Cover edge cases and error paths
- Prefer unit tests for logic
- Use integration tests for workflows

## TDD Workflow

1. **Red**: Write a failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve code, keep tests green

## Test Structure

```typescript
describe('UserService', () => {
  describe('createUser', () => {
    it('should create user with valid data', async () => {
      const user = await service.createUser(validData);
      expect(user.id).toBeDefined();
    });

    it('should reject duplicate email', async () => {
      await service.createUser(validData);
      await expect(service.createUser(validData))
        .rejects.toThrow('Email already exists');
    });
  });
});
```

## Checklist

- [ ] New code has corresponding tests
- [ ] Changed behavior has updated tests
- [ ] Edge cases are covered
- [ ] Error paths are tested
- [ ] Tests pass locally
