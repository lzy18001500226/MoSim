# hello-squad — Manual Test Script

## Prerequisites

1. Node.js ≥ 20 installed
2. SDK is built: `cd ../../ && npm run build`

## Steps

### 1. Install dependencies

```bash
cd samples/hello-squad
npm install
```

**Expected:** Clean install, no errors.

### 2. Run the sample

```bash
npm start
```

**Expected:**
- Step 1: `.squad/` directory created in a temp directory
- Step 2: 4 agents cast from "The Usual Suspects" — Keyser (lead), McManus (developer), Fenster (tester), Verbal (scribe)
- Step 3: Each agent onboarded with charter + history files
- Step 4: Team roster printed in a table
- Step 5: Casting history shows 2 records; names match across both casts

**Verify:** Exit code is 0.

### 3. Run again (idempotency check)

```bash
npm start
```

**Expected:**
- Step 1: `.squad/` already exists
- Step 3: Agents skipped ("already onboarded")
- Step 5: Names still match

### 4. Run automated tests

```bash
npm test
```

**Expected:** All tests pass.

### 5. Verify types compile

```bash
npx tsc --noEmit
```

**Expected:** Zero errors.
