# Multi-stage build for knock-knock Squad SDK sample

FROM node:22-alpine AS builder

WORKDIR /build

# Copy SDK package.json and strip lifecycle scripts so npm won't rebuild
COPY packages/squad-sdk/package.json packages/squad-sdk/
RUN node -e "\
  const fs = require('fs');\
  const p = JSON.parse(fs.readFileSync('/build/packages/squad-sdk/package.json','utf8'));\
  delete p.scripts.prepare;\
  delete p.scripts.prepublishOnly;\
  fs.writeFileSync('/build/packages/squad-sdk/package.json', JSON.stringify(p,null,2))"

# Install SDK dependencies (includes devDeps like @opentelemetry/api used at runtime)
WORKDIR /build/packages/squad-sdk
RUN npm install

# Copy pre-built SDK dist
COPY packages/squad-sdk/dist /build/packages/squad-sdk/dist

# Copy the sample source
WORKDIR /build
COPY samples/knock-knock/package.json samples/knock-knock/
COPY samples/knock-knock/tsconfig.json samples/knock-knock/
COPY samples/knock-knock/index.ts samples/knock-knock/

# Install sample dependencies (resolves file: link to local SDK)
WORKDIR /build/samples/knock-knock
RUN npm install

# Production stage
FROM node:22-alpine

WORKDIR /app

# Copy everything needed
COPY --from=builder /build/samples/knock-knock /app
COPY --from=builder /build/packages/squad-sdk /packages/squad-sdk

CMD ["npx", "tsx", "index.ts"]
