# hook-governance — Manual Test Script

## Prerequisites

1. Node.js ≥ 20 installed
2. SDK is built: `cd ../../ && npm run build`

## Steps

### 1. Install dependencies

```bash
cd samples/hook-governance
npm install
```

**Expected:** Clean install, no errors.

### 2. Run the sample

```bash
npm start
```

**Expected:**
- Demo 1: `src/utils/helper.ts` write → allowed; `/etc/passwd` write → blocked with reason
- Demo 2: Three email addresses redacted to `[EMAIL_REDACTED]`; nested object also scrubbed
- Demo 3: Backend blocked from `src/auth.ts`; Frontend allowed
- Demo 4: Ask #1–#3 allowed; Ask #4–#5 blocked with rate limit reason

**Verify:** Exit code is 0.

### 3. Run automated tests

```bash
npm test
```

**Expected:** All tests pass.

### 4. Verify types compile

```bash
npx tsc --noEmit
```

**Expected:** Zero errors.

### 5. Verify combined policies

Look at the "Combined Pipeline" test in `tests/hook-governance.test.ts` — it creates a single pipeline with all four policies active and verifies they all enforce simultaneously.
