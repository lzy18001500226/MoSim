# Security Architecture Specification Guide

How to convert security requirements from a PRD into implementable security engineering specifications.

---

## Principle

Security is **architecture**, not a checklist. Every security decision affects system design, performance, and user experience. Specify it as thoroughly as you specify data models and APIs.

---

## 1. Authentication

### Authentication Flow Specification

| Attribute | Specify |
|-----------|---------|
| **Protocol** | OAuth2 / OIDC / SAML / API Key / Custom |
| **Identity Provider** | Self-hosted / Auth0 / Cognito / Firebase Auth |
| **Login Methods** | Email+password, social login, SSO, magic link, passkey |
| **MFA** | Required for whom? Methods (TOTP, SMS, WebAuthn)? |
| **Token Type** | JWT / opaque / session cookie |
| **Token Lifetime** | Access token TTL, refresh token TTL |
| **Refresh Flow** | Rotation policy, revocation on compromise |
| **Session Management** | Max concurrent sessions, idle timeout, absolute timeout |

### Token Specification (if JWT)

```yaml
jwt:
  algorithm: RS256
  issuer: "https://auth.example.com"
  audience: "https://api.example.com"
  access_token:
    ttl: 15m
    claims: [sub, email, roles, permissions]
  refresh_token:
    ttl: 7d
    rotation: true  # New refresh token on each use
    revocation: true  # Can be explicitly revoked
```

### Authentication Error Handling

| Scenario | Response | User Experience |
|----------|----------|----------------|
| Invalid credentials | 401, generic message | "Invalid email or password" (no hint which) |
| Expired token | 401 + WWW-Authenticate | Auto-refresh, transparent to user |
| Revoked token | 401 | Redirect to login |
| Account locked | 403 | "Account locked. Try again in [X] minutes." |
| MFA required | 403 + mfa_required | Redirect to MFA flow |

---

## 2. Authorization

### Permission Model

Choose and specify:

| Model | Use When | Specify |
|-------|----------|---------|
| **RBAC** | Clear role hierarchies | Role definitions, role-permission matrix |
| **ABAC** | Context-dependent access | Attribute definitions, policy rules |
| **ReBAC** | Social/graph-based access | Relationship definitions, traversal rules |

### Role-Permission Matrix (RBAC example)

| Permission | Admin | Manager | Member | Viewer | Guest |
|------------|-------|---------|--------|--------|-------|
| Create resource | ✅ | ✅ | ✅ | ❌ | ❌ |
| Read own resource | ✅ | ✅ | ✅ | ✅ | ❌ |
| Read team resource | ✅ | ✅ | ✅ | ✅ | ❌ |
| Update own resource | ✅ | ✅ | ✅ | ❌ | ❌ |
| Delete own resource | ✅ | ✅ | ❌ | ❌ | ❌ |
| Manage users | ✅ | ✅ | ❌ | ❌ | ❌ |
| System settings | ✅ | ❌ | ❌ | ❌ | ❌ |

### Enforcement Points

| Layer | Mechanism | What It Checks |
|-------|-----------|----------------|
| API Gateway | Token validation | Authentication, basic role check |
| Application | Middleware/decorator | Permission for specific action |
| Data layer | Row-level security / query filter | Data ownership, tenant isolation |
| UI | Conditional rendering | Hide unauthorized actions (defense in depth) |

---

## 3. Data Security

### Data Classification

| Level | Definition | Examples | Handling |
|-------|-----------|----------|----------|
| **Public** | No restrictions | Marketing content | No special handling |
| **Internal** | Business-only | Analytics, metrics | Access control |
| **Confidential** | Restricted access | Financial data, contracts | Encryption + audit |
| **PII** | Personal data (regulated) | Name, email, phone, address | Encryption + GDPR/CCPA compliance |
| **Sensitive PII** | High-risk personal data | SSN, health records, biometrics | Encryption + strict access + masking |

### Encryption Specification

| Data State | Method | Standard | Key Management |
|------------|--------|----------|----------------|
| **In transit** | TLS | 1.3 minimum | Managed certificates |
| **At rest (DB)** | AES-256 | Column-level or full-disk | KMS (AWS/GCP/Azure) |
| **At rest (files)** | AES-256-GCM | Per-file encryption | KMS with rotation |
| **In application** | Field-level encryption | For PII fields | Application-managed |

### PII Handling

| Operation | Specification |
|-----------|--------------|
| Collection | Minimum necessary; explicit consent; privacy notice |
| Storage | Encrypted; retention period defined; deletion procedure |
| Access | Logged; role-restricted; purpose-bound |
| Display | Masked by default (show last 4); unmasked only with audit |
| Export | Encrypted in transit; format specified; access logged |
| Deletion | Hard delete with verification; cascade to backups within [X] days |

---

## 4. Input Security

### Validation Strategy

| Attack Vector | Defense | Implementation |
|--------------|---------|----------------|
| SQL Injection | Parameterized queries | ORM/query builder; never string concat |
| XSS | Output encoding | Template engine auto-escape; CSP headers |
| CSRF | Token-based | Synchronizer token or SameSite cookies |
| File Upload | Type + size + scan | Whitelist extensions; virus scan; isolated storage |
| Path Traversal | Input sanitization | Canonicalize paths; reject `..` |
| Mass Assignment | Explicit allowlists | DTO/schema validation; never bind raw input |

### Rate Limiting

| Endpoint Type | Limit | Window | Key | Response |
|--------------|-------|--------|-----|----------|
| Login | 5 attempts | 15 min | IP + email | 429 + Retry-After |
| API (authenticated) | 100 req | 1 min | User ID | 429 + Retry-After |
| API (unauthenticated) | 20 req | 1 min | IP | 429 + Retry-After |
| File upload | 10 files | 1 hour | User ID | 429 + message |

---

## 5. Audit Logging

### Events to Log

| Category | Events |
|----------|--------|
| Authentication | Login success/failure, logout, token refresh, MFA attempt |
| Authorization | Permission denied, role change, escalation attempt |
| Data Access | Read of sensitive data, bulk export, search of PII |
| Data Modification | Create/update/delete of any resource |
| Administration | User management, config changes, deployment |
| Security | Rate limit hit, injection attempt, invalid token |

### Log Format

```json
{
  "timestamp": "2025-01-15T10:30:00.000Z",
  "level": "INFO",
  "event": "auth.login.success",
  "actor": { "id": "user-123", "ip": "192.168.1.1", "user_agent": "..." },
  "resource": { "type": "session", "id": "sess-456" },
  "action": "create",
  "result": "success",
  "metadata": { "mfa_used": true, "login_method": "password" },
  "trace_id": "abc-def-123"
}
```

### Log Security

| Requirement | Specification |
|------------|--------------|
| PII in logs | Redacted or tokenized (never plain text) |
| Retention | [X] days online, [Y] days archive |
| Access | Security team + on-call only; logged |
| Tamper protection | Write-once storage or signed entries |
| Compliance | Meet [GDPR/HIPAA/SOC2] requirements |

---

## 6. Secrets Management

| Secret Type | Storage | Rotation | Access |
|-------------|---------|----------|--------|
| API keys (ours) | Vault / KMS | Every [X] days | Application identity |
| API keys (third-party) | Vault / KMS | Per vendor policy | Application identity |
| DB credentials | Vault / KMS | Every [X] days | Application identity |
| Encryption keys | KMS | Automatic | KMS policy |
| JWT signing keys | Vault / KMS | Every [X] days | Auth service only |

### Rules

- **Never** store secrets in code, config files, or environment variables at build time
- **Never** log secrets (even at DEBUG level)
- **Always** use a secrets manager in production
- **Always** have a rotation plan before launch
- **Always** have a revocation procedure for compromised secrets
