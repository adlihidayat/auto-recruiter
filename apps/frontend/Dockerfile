FROM node:20-bookworm-slim AS base

FROM base AS builder
WORKDIR /app

# Copy root workspace manifests
COPY package.json package-lock.json ./
# Copy workspace packages package.json
COPY apps/frontend/package.json ./apps/frontend/package.json
COPY packages/shared-ui/package.json ./packages/shared-ui/package.json

# Install all dependencies (this step will be cached unless dependencies change)
RUN npm ci

# Copy the actual source code
COPY packages/shared-ui ./packages/shared-ui
COPY apps/frontend ./apps/frontend

# Next.js telemetry is disabled
ENV NEXT_TELEMETRY_DISABLED=1

# Build the frontend (this will create .next/standalone/apps/frontend)
RUN npm run build -w frontend

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/apps/frontend/public ./apps/frontend/public
# Copy the standalone output
COPY --from=builder --chown=nextjs:nodejs /app/apps/frontend/.next/standalone ./
# Copy the static folder (Next.js does not copy this to standalone automatically)
COPY --from=builder --chown=nextjs:nodejs /app/apps/frontend/.next/static ./apps/frontend/.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000

CMD ["node", "apps/frontend/server.js"]
