#!/usr/bin/env tsx

import { execute } from '@oclif/core';

// Use tsx to run TypeScript source directly in dev mode
await execute({ development: true, dir: import.meta.url });
