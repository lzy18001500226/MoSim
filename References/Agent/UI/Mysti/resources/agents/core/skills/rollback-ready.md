---
id: rollback-ready
name: Rollback Ready
description: Structures changes to be easily reversible
icon: rollback-ready.png
category: reliability
activationTriggers:
  - rollback
  - revert
  - deploy
  - release
  - safe
---

# Instructions

Structure changes to be easily reversible. Maintain clear checkpoints for safe rollback.

## Behavioral Guidelines

- Keep commits atomic and revertable
- Use feature flags for risky changes
- Deploy database changes separately
- Maintain backwards compatibility during transitions
- Test rollback procedures
- Document rollback steps

## Rollback Patterns

### Feature Flags
```typescript
if (featureFlags.isEnabled('new-checkout-flow')) {
  return newCheckoutFlow(cart);
}
return legacyCheckoutFlow(cart);
```

### Database Migrations
```sql
-- Up: Add new column (backwards compatible)
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Down: Remove column (safe rollback)
ALTER TABLE users DROP COLUMN phone;
```

### Deployment Strategy
1. Deploy backwards-compatible changes
2. Enable feature flag for small %
3. Monitor metrics and errors
4. Gradually increase rollout
5. Remove old code path after stable

## Checklist

- [ ] Changes are atomic and revertable
- [ ] Database changes are backwards compatible
- [ ] Feature flags protect risky changes
- [ ] Rollback procedure documented
- [ ] Monitoring in place for issues
