# Operations & Deployment Specification Guide

How to specify deployment, configuration, monitoring, and operational procedures so a system can be run and maintained from day one.

---

## Principle

If it's not in the spec, it doesn't exist in production. Operations specifications are **not optional**—they're what makes the difference between "it works on my machine" and "it runs reliably in production."

---

## 1. Environment Specification

### Environment Matrix

| Attribute | Development | Staging | Production |
|-----------|-------------|---------|------------|
| **Purpose** | Local development | Pre-production testing | Live traffic |
| **Data** | Seed/mock data | Anonymized production clone | Real data |
| **Scale** | Single instance | Production-like | Full scale |
| **External services** | Mocked/sandbox | Sandbox with real auth | Production |
| **Access** | All developers | Team + QA | Restricted (on-call + deploy) |
| **URL** | localhost:XXXX | staging.example.com | api.example.com |

### Provisioning

For each environment, specify:
- How to create from scratch (IaC template, scripts, or manual steps)
- How to tear down
- How to reset to clean state
- Time to provision a new environment

---

## 2. Deployment Specification

### Deployment Architecture

```
[Specify your deployment topology]

Example:
┌─────────────────────────────────────────────────────────────┐
│ Load Balancer (ALB)                                          │
│   ├── API Service (3 replicas, 512MB/0.5CPU each)           │
│   ├── Worker Service (2 replicas, 1GB/1CPU each)            │
│   └── Scheduler (1 replica)                                  │
│                                                              │
│ Data Stores:                                                 │
│   ├── PostgreSQL (RDS, db.r6g.large, Multi-AZ)             │
│   ├── Redis (ElastiCache, cache.t3.medium)                  │
│   └── S3 (file storage)                                      │
│                                                              │
│ External:                                                    │
│   ├── Auth Provider (Auth0)                                  │
│   └── Email Service (SendGrid)                               │
└─────────────────────────────────────────────────────────────┘
```

### CI/CD Pipeline

```
Code Push → Lint/Format → Unit Tests → Build → Integration Tests
  → Security Scan → Deploy Staging → E2E Tests → Manual Approval
  → Deploy Production (canary 10% → 50% → 100%)
```

**Per stage, specify:** trigger, tools, success criteria, failure action, timeout.

### Rollout Strategy

| Strategy | Specification |
|----------|--------------|
| **Method** | Rolling / Blue-Green / Canary |
| **Canary %** | [X]% initial, [Y]% after [Z] minutes |
| **Health check** | Endpoint, expected response, check interval |
| **Auto-rollback** | Trigger conditions (error rate > [X]%, latency > [Y]ms) |
| **Manual rollback** | Command/procedure, expected time |
| **Database migrations** | Run before/after deploy? Backward compatible? |

---

## 3. Configuration Specification

### Configuration Registry

**Every** configurable parameter must be documented:

| Name | Type | Default | Required | Description | Allowed Values | Sensitive |
|------|------|---------|----------|-------------|---------------|-----------|
| `DATABASE_URL` | string | - | Yes | PostgreSQL connection string | Valid PG URI | Yes |
| `LOG_LEVEL` | enum | info | No | Application log level | debug, info, warn, error | No |
| `MAX_UPLOAD_SIZE_MB` | int | 10 | No | Maximum file upload size | 1-100 | No |
| `FEATURE_NEW_UI` | bool | false | No | Feature flag: new UI | true, false | No |
| `LLM_API_KEY` | string | - | Yes | API key for LLM provider | Valid API key | Yes |
| `LLM_MODEL` | string | gpt-4 | No | Model identifier | See provider docs | No |
| `LLM_MAX_TOKENS` | int | 4096 | No | Max output tokens | 1-128000 | No |

### Configuration Hierarchy

```
Defaults (in code) → Config file → Environment variables → Runtime overrides
(lowest priority)                                        (highest priority)
```

### Feature Flags

| Flag | Default | Description | Rollout Plan |
|------|---------|-------------|-------------|
| `FEATURE_X` | false | [Description] | 10% → 50% → 100% over 2 weeks |

---

## 4. Monitoring Specification

### Key Metrics

#### System Metrics

| Metric | Source | Alert Threshold | Severity |
|--------|--------|----------------|----------|
| CPU utilization | Container/host | > 80% for 5 min | Warning |
| Memory utilization | Container/host | > 85% for 5 min | Warning |
| Disk usage | Volume | > 80% | Warning |
| Container restarts | Orchestrator | > 3 in 10 min | Critical |

#### Application Metrics

| Metric | Source | Alert Threshold | Severity |
|--------|--------|----------------|----------|
| Request rate (RPS) | Load balancer | >[X] (capacity) | Warning |
| Error rate (5xx) | Application | > 1% for 5 min | Critical |
| Response time (P95) | Application | > [X]ms for 5 min | Warning |
| Response time (P99) | Application | > [Y]ms for 5 min | Critical |
| Queue depth | Message queue | > [X] for 10 min | Warning |
| DB connection pool | Application | > 80% utilized | Warning |

#### Business Metrics

| Metric | Source | Alert Threshold | Severity |
|--------|--------|----------------|----------|
| [Business metric 1] | Application | [condition] | [level] |
| Successful transactions/min | Application | < [X] (anomaly) | Warning |

#### AI-Specific Metrics (if applicable)

| Metric | Source | Alert Threshold | Severity |
|--------|--------|----------------|----------|
| LLM latency (P95) | Application | > [X]s | Warning |
| Token usage per request | Application | > [X] (cost control) | Warning |
| Tool call failure rate | Application | > [X]% | Critical |
| RAG retrieval empty rate | Application | > [X]% | Warning |

### Dashboard Specification

Define dashboards by audience:

| Dashboard | Audience | Key Panels |
|-----------|----------|-----------|
| **System Health** | On-call | Error rate, latency, saturation, traffic (RED/USE) |
| **Business** | Product team | Active users, conversion, key business metrics |
| **AI/Agent** | ML team | Quality scores, cost, latency, failure modes |

---

## 5. Logging Specification

### Log Format

```json
{
  "timestamp": "ISO-8601",
  "level": "INFO|WARN|ERROR",
  "service": "api-service",
  "trace_id": "uuid",
  "span_id": "uuid",
  "message": "Human-readable message",
  "context": { "user_id": "...", "request_id": "..." },
  "error": { "type": "...", "message": "...", "stack": "..." }
}
```

### Logging Levels

| Level | Use For | Examples |
|-------|---------|---------|
| ERROR | Failures requiring attention | Unhandled exceptions, data corruption |
| WARN | Degraded but functional | Retry succeeded, approaching limits |
| INFO | Significant state changes | Request handled, job completed |
| DEBUG | Development troubleshooting | Variable values, branch decisions |

### PII in Logs

- **Never** log: passwords, tokens, full credit cards, SSN
- **Mask**: email (j***@example.com), phone (***-***-1234), names in non-audit logs
- **Allowed**: user IDs, anonymized identifiers

---

## 6. Scaling Specification

### Scaling Strategy

| Component | Scaling Type | Trigger | Min | Max | Cooldown |
|-----------|-------------|---------|-----|-----|----------|
| API service | Horizontal auto-scale | CPU > 70% | 2 | 10 | 5 min |
| Worker | Horizontal auto-scale | Queue depth > 100 | 1 | 5 | 3 min |
| Database | Vertical (manual) | Connection saturation | - | - | - |
| Cache | Vertical (manual) | Memory > 80% | - | - | - |

### Resource Limits Per Container

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|------------|-----------|----------------|-------------|
| API | 250m | 500m | 256Mi | 512Mi |
| Worker | 500m | 1000m | 512Mi | 1Gi |

---

## 7. Disaster Recovery

### Backup Specification

| Data Store | Method | Frequency | Retention | Tested |
|-----------|--------|-----------|-----------|--------|
| PostgreSQL | Automated snapshots | Daily + WAL streaming | 30 days | Monthly |
| Redis | RDB snapshot | Every 6 hours | 7 days | Monthly |
| File storage | Cross-region replication | Continuous | Permanent | Quarterly |

### Recovery Objectives

| Metric | Target | How Achieved |
|--------|--------|-------------|
| RTO (Recovery Time Objective) | < [X] hours | [Strategy: multi-AZ, failover] |
| RPO (Recovery Point Objective) | < [X] minutes | [Strategy: WAL, replication] |

### Recovery Procedures

| Scenario | Procedure | Expected Time | Owner |
|----------|-----------|--------------|-------|
| Single service failure | Auto-restart + health check | < 2 min | Automated |
| Database failure | Failover to replica | < 5 min | Automated |
| Region failure | DNS failover to DR region | < 30 min | On-call |
| Data corruption | Point-in-time recovery | < 2 hours | DBA + on-call |

---

## 8. Runbook Template

For each operational scenario, provide:

```markdown
## Runbook: [Scenario Name]

### Symptoms
[How to recognize this is happening]

### Impact
[What is affected and how severely]

### Diagnosis Steps
1. Check [metric/log/dashboard]
2. Verify [condition]
3. If [condition], proceed to Resolution

### Resolution Steps
1. [Step with exact commands]
2. [Step with exact commands]
3. Verify resolution: [how to confirm]

### Escalation
- If unresolved after [X] minutes: contact [team/person]
- If data loss suspected: [procedure]

### Prevention
[What to do to prevent recurrence]
```
