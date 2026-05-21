# Extraction Checklist

Detailed checklists for extracting specifications from different element types. Use these to ensure completeness—every checkbox represents something that could cause replication failure if missed.

## General Principle

For every element, ask:
> "If I gave this spec to someone who has never seen the code, could they implement it correctly?"

If the answer is "maybe" or "probably", the spec is incomplete.

## Traceability (Recommended)

For each documented element, include at least one `Source:` anchor pointing to the implementation location in the original codebase. This enables automated Spec → Code checks and makes reviews faster.

Examples:
- `Source: path/to/file.ext`
- `Source: path/to/file.ext#SymbolName`
- `Source: path/to/file.ext:123`

---

## API Endpoint Checklist

### Basic Information
- [ ] HTTP method (GET, POST, PUT, PATCH, DELETE)
- [ ] Full URL path including all path parameters
- [ ] Purpose/description (what does this endpoint do?)

### Request
- [ ] Path parameters (name, type, validation)
- [ ] Query parameters (name, type, required?, default, validation)
- [ ] Request body schema (all fields, types, nested objects)
- [ ] Required vs optional fields clearly marked
- [ ] Field validation rules (min/max, regex, enum values)
- [ ] Content-Type requirements
- [ ] Size limits (max request body size)

### Authentication & Authorization
- [ ] Auth required? (Yes/No)
- [ ] Auth method (Bearer token, API key, session, etc.)
- [ ] Required permissions/roles
- [ ] Resource-level authorization rules

### Response
- [ ] Success response status code(s)
- [ ] Success response body schema
- [ ] All possible error status codes
- [ ] Error response body format
- [ ] Error conditions mapped to error codes

### Behavior
- [ ] Idempotency (is this safe to retry?)
- [ ] Rate limiting (limits, headers)
- [ ] Caching behavior (headers, TTL)
- [ ] Side effects (what else changes?)
- [ ] Async behavior (if any)

### Edge Cases
- [ ] Empty result handling
- [ ] Pagination (if list endpoint)
- [ ] Concurrent request handling
- [ ] Partial failure handling (batch operations)

---

## Database Entity Checklist

### Basic Information
- [ ] Entity name (table name)
- [ ] Purpose (what does this represent?)
- [ ] Relationship to domain concept

### Fields
For EACH field:
- [ ] Field name
- [ ] Data type (exact DB type)
- [ ] Nullable?
- [ ] Default value
- [ ] Constraints (unique, check, etc.)
- [ ] Description/purpose
- [ ] Valid value range or enum

### Indexes
- [ ] Primary key definition
- [ ] Unique indexes (which fields, why)
- [ ] Non-unique indexes (which fields, why)
- [ ] Composite indexes (field order matters!)
- [ ] Partial/filtered indexes (conditions)

### Relationships
- [ ] Foreign keys (to which table/field)
- [ ] Relationship type (1:1, 1:N, N:N)
- [ ] ON DELETE behavior
- [ ] ON UPDATE behavior
- [ ] Join table (for N:N)

### Data Lifecycle
- [ ] How records are created
- [ ] How records are updated
- [ ] Soft delete vs hard delete
- [ ] Audit fields (created_at, updated_at, etc.)
- [ ] Data retention policy

### Validation
- [ ] Application-level validation rules
- [ ] Business rules enforced by this entity
- [ ] Cross-field validation

### Performance
- [ ] Expected row count
- [ ] Growth rate
- [ ] Hot columns (frequently queried)
- [ ] Partitioning (if any)

---

## Business Logic Module Checklist

### Basic Information
- [ ] Module/class/function name
- [ ] Purpose (what business problem does it solve?)
- [ ] Where it fits in the architecture

### Interface
- [ ] All input parameters
- [ ] Input types and validation
- [ ] Return type(s)
- [ ] Exceptions/errors thrown
- [ ] Side effects

### Logic
- [ ] Main algorithm/flow (step by step)
- [ ] All conditional branches
- [ ] Loop conditions and bounds
- [ ] Calculations/formulas (exact, not approximate)
- [ ] Decision trees (if complex branching)

### Business Rules
- [ ] What rules are enforced?
- [ ] Why do these rules exist?
- [ ] What happens when rules are violated?

### Dependencies
- [ ] Other modules/services called
- [ ] External APIs used
- [ ] Database queries made
- [ ] Events emitted

### State Changes
- [ ] What data is modified?
- [ ] Transaction boundaries
- [ ] Rollback behavior

### Edge Cases
- [ ] Null/empty input handling
- [ ] Maximum/minimum values
- [ ] Concurrent execution
- [ ] Partial failure

### Performance
- [ ] Time complexity
- [ ] Expected execution time
- [ ] Resource usage (memory, CPU)

---

## UI Component Checklist

### Basic Information
- [ ] Component name
- [ ] Purpose (what UI need does it serve?)
- [ ] Where it's used (pages/parent components)

### Props/Inputs
For EACH prop:
- [ ] Prop name
- [ ] Type
- [ ] Required vs optional
- [ ] Default value
- [ ] Validation/constraints

### State
- [ ] Internal state variables
- [ ] Initial state values
- [ ] State update triggers
- [ ] External state consumed (context, store)

### Rendering
- [ ] Visual structure/layout
- [ ] Variants (size, color, etc.)
- [ ] Conditional rendering rules
- [ ] Loading state appearance
- [ ] Error state appearance
- [ ] Empty state appearance

### Interaction
- [ ] User events handled (click, hover, etc.)
- [ ] Event handler behavior
- [ ] Form submission (if applicable)
- [ ] Navigation triggered

### Accessibility
- [ ] ARIA roles/labels
- [ ] Keyboard navigation
- [ ] Focus management
- [ ] Screen reader behavior

### Responsive
- [ ] Breakpoint behavior
- [ ] Mobile-specific features
- [ ] Touch interactions

### Styling
- [ ] CSS/style approach
- [ ] Theme integration
- [ ] Customization points

---

## Background Job Checklist

### Basic Information
- [ ] Job name/identifier
- [ ] Purpose (what task does it perform?)
- [ ] Trigger (cron, event, manual)

### Scheduling
- [ ] Schedule/frequency (cron expression)
- [ ] Timezone considerations
- [ ] Overlap handling (allow concurrent?)
- [ ] Timeout settings

### Execution
- [ ] Input/parameters
- [ ] Main logic flow
- [ ] External calls made
- [ ] Data processed/modified

### Error Handling
- [ ] Retry policy (count, backoff)
- [ ] Dead letter handling
- [ ] Alert/notification on failure
- [ ] Manual recovery procedures

### Performance
- [ ] Expected duration
- [ ] Resource requirements
- [ ] Batch size (if processing batches)

### Observability
- [ ] Logging (what's logged)
- [ ] Metrics captured
- [ ] Health check integration

---

## Integration/External API Checklist

### Basic Information
- [ ] Service name
- [ ] Purpose (why we integrate)
- [ ] API documentation link

### Connection
- [ ] Base URL(s) (per environment)
- [ ] Authentication method
- [ ] Required credentials/keys

### Endpoints Used
For EACH endpoint:
- [ ] HTTP method and path
- [ ] Request format
- [ ] Response format
- [ ] Error responses

### Error Handling
- [ ] Retry policy
- [ ] Circuit breaker settings
- [ ] Fallback behavior
- [ ] Timeout settings

### Rate Limiting
- [ ] Known limits
- [ ] Rate limit handling
- [ ] Backoff strategy

### Data Mapping
- [ ] External → Internal mapping
- [ ] Internal → External mapping
- [ ] Transformation logic

### Testing
- [ ] Mock/sandbox environment
- [ ] Test credentials
- [ ] Integration test approach

---

## Configuration Checklist

### Environment Variables
For EACH variable:
- [ ] Variable name
- [ ] Type (string, number, boolean, JSON)
- [ ] Required vs optional
- [ ] Default value (if optional)
- [ ] Valid values/format
- [ ] What it controls
- [ ] Security sensitivity (should it be secret?)

### Feature Flags
For EACH flag:
- [ ] Flag name
- [ ] Type
- [ ] Default value
- [ ] What it enables/disables
- [ ] Affected code paths
- [ ] Rollout strategy

### Configuration Files
For EACH config file:
- [ ] File path
- [ ] Format (JSON, YAML, etc.)
- [ ] Schema/structure
- [ ] Environment-specific variants
- [ ] Validation rules

---

## Cross-Cutting Concerns Checklist

### Error Handling
- [ ] Global error handler behavior
- [ ] Error categorization (client vs server)
- [ ] Error logging format
- [ ] Error response format
- [ ] User-facing error messages

### Logging
- [ ] Log levels used and when
- [ ] Log format/structure
- [ ] Sensitive data handling
- [ ] Log destinations

### Authentication
- [ ] Auth mechanism(s)
- [ ] Session management
- [ ] Token format and validation
- [ ] Refresh token flow

### Authorization
- [ ] Permission model
- [ ] Role definitions
- [ ] Resource-level access control
- [ ] Permission checking flow

### Caching
- [ ] What's cached
- [ ] Cache keys
- [ ] TTL settings
- [ ] Invalidation triggers

### Performance
- [ ] Response time requirements
- [ ] Throughput requirements
- [ ] Resource limits
- [ ] Monitoring metrics

---

## Hard-to-Miss Details

These are commonly forgotten but critical for accurate replication:

### Data
- [ ] Timezone handling (storage, display, conversion)
- [ ] Decimal precision and rounding rules
- [ ] Currency handling
- [ ] Date/time formats
- [ ] Character encoding

### Logic
- [ ] Off-by-one boundaries
- [ ] Null propagation
- [ ] Default value initialization
- [ ] Implicit type conversions
- [ ] Floating point comparison

### UI
- [ ] Focus management after actions
- [ ] Loading indicator thresholds
- [ ] Animation timing
- [ ] Scroll position restoration
- [ ] Form reset behavior

### Security
- [ ] Input sanitization
- [ ] Output encoding
- [ ] CORS configuration
- [ ] CSP headers
- [ ] Rate limiting per user/IP

### Concurrency
- [ ] Race condition prevention
- [ ] Optimistic vs pessimistic locking
- [ ] Idempotency keys
- [ ] Distributed locks
