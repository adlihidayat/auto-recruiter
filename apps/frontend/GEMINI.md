# Frontend Web App — Architecture & Execution Protocol

## 0. Rule Cascade (Mid-Level Override)

This file extends the root `/GEMINI.md` with Next.js/TypeScript-specific and frontend-specific behavioral rules.

- **Inheritance**: Apply all global rules (naming, docstrings, manifests, 3-strike verification) alongside these rules.
- **Scope**: These rules govern everything inside `apps/frontend/`. They do not apply to `apps/backend`, `apps/agents`, or `apps/realtime-worker`, which are Python services with their own conventions.
- **Child Overrides**: Feature directories under `src/features/*` may contain a localized `GEMINI.md` only if a feature has genuinely unique conventions (e.g. the live-interview room). Absent that, this file is authoritative for the whole app.

---

## 1. Tech Stack & Architectural Boundaries

This application is the HR-facing web client: a dashboard for creating interviews, tracking their agent-driven pipeline, joining/observing the live interview room, and reviewing candidate reports.

- **Framework**: Next.js 15+, App Router only. No `pages/` directory, no mixing routers.
- **Runtime model**: Server Components by default. A file only becomes a Client Component (`"use client"`) when it needs browser APIs, interactivity, hooks, or a third-party client SDK (e.g. the LiveKit room UI). Push `"use client"` as far down the tree as possible — pages and layouts stay server components; only the interactive leaf (a form, a live transcript panel, a button) opts in.
- **Language**: TypeScript, strict mode. No `any` — use `unknown` and narrow, or define the type. No untyped fetch responses.
- **Styling**: Tailwind CSS. No CSS-in-JS, no ad-hoc `.module.css` unless Tailwind genuinely can't express it (rare — justify in a comment if so).
- **UI primitives**: shadcn/ui components generated into `src/components/ui/`. Treat generated primitives as owned code (they can be edited), but don't reintroduce a second design system on top of them.
- **Forms & validation**: `react-hook-form` + `zod`. Zod schemas for form input mirror — but are not necessarily identical to — the shared payload schemas below; UI-only concerns (e.g. a "confirm password" field) stay local to the form schema.
- **Server state / data fetching**: Server Components fetch on the server wherever possible. For client-side data that must poll, revalidate, or mutate optimistically (interview status ticking through the pipeline, live candidate list), use `@tanstack/react-query`.
- **Client/UI state**: `zustand` for state that is genuinely client-only and cross-component (e.g. live-interview panel layout, transient UI toggles). Do not use it as a substitute for server state — if it comes from the backend, it belongs in React Query or a Server Component fetch, not a Zustand store.
- **Real-time interview room**: `@livekit/components-react` + `livekit-client` for the in-browser room UI (HR observing/joining a live interview). The frontend only ever receives a **room token** issued by `apps/backend` — it never talks to `apps/realtime-worker` or `apps/agents` directly, and never holds LiveKit server credentials.
- **HTTP client**: A single typed API client in `src/lib/api/` wrapping `fetch`, built against types generated from `apps/backend`'s OpenAPI schema. Do not hand-write request/response types for endpoints that already have a generated type — regenerate instead.
- **Auth**: Session/JWT issued by `apps/backend`. Route protection is enforced in `middleware.ts` at the edge plus a server-side session check in the `(dashboard)` layout — never rely on client-side redirects alone to gate HR-only routes.

### Dependency Boundary (inherited from root, restated for emphasis)

- This app talks to **`apps/backend` only**, over HTTP/JSON, using the generated API client. It must never import from, or make requests directly to, `apps/agents` or `apps/realtime-worker`.
- The one exception is the LiveKit room connection itself: the browser connects directly to the LiveKit media server using the short-lived token `apps/backend` issued. That token exchange is the only "direct" real-time path, and it is not a call to `realtime-worker`'s API — it's the LiveKit SDK talking to LiveKit infrastructure.
- Shared payload shapes (`Goal`, `QuestionSuite`, `InterviewSession`, candidate report models, etc.) are defined once in `packages/shared-schemas` (Python/Pydantic) and exposed to this app only via the generated TypeScript types from `apps/backend`'s OpenAPI spec — never hand-duplicated as parallel TS interfaces.

---

## 2. Code Style & Framework Behavior

### App Router Conventions

- **Route groups over flat routes**: use `(auth)` for sign-in/sign-up, `(dashboard)` for the authenticated HR app. Route groups organize layouts without leaking into the URL.
- **Params & search params are async**: always `await params` / `await searchParams` in Server Components and route handlers. Never destructure them synchronously — this is a Next.js 15 breaking change, not a style preference.
- **Colocate route UI states**: every route segment that fetches data ships a `loading.tsx` (skeleton, not a spinner-only placeholder) and an `error.tsx` (actionable message, not a generic "something went wrong"). A route with no meaningful loading state still gets a minimal one — Suspense boundaries are how this app avoids full-page loading flashes.
- **Server Actions for mutations**: form submissions (create interview, edit rubric, trigger re-grade) use Server Actions, not client-side `fetch` to a route handler, unless the mutation must be optimistic/interactive (in which case React Query's mutation + the typed API client is correct instead).
- **Route Handlers (`app/api/`) are for narrow BFF concerns only** — e.g. a webhook receiver if `apps/backend` needs to push a browser-facing callback, or reshaping a response for a specific widget. They are not a general proxy layer; most data access goes through Server Components or the typed API client directly.
- **Interview detail is a popup, not a route.** There is deliberately no `interviews/[interviewId]/page.tsx`. Clicking an interview in the list opens `InterviewDetailDialog` (a Client Component, `src/features/interviews/components/`) over the list — it does not navigate. Keep it deep-linkable without making it a page: drive the open/closed state and which interview is showing off a URL search param (`?interview=<id>`), read via `useSearchParams`, so the popup can be reopened from a shared link or refresh without becoming a distinct route/page. Data for the dialog is fetched with the React Query hook in `interviews/queries.ts`, not passed down from a parent page.
- **Candidate detail and the live room are real pages**, not popups — they get their own URL, their own `loading.tsx`/`error.tsx`, and are meant to be opened in a new tab, bookmarked, or linked directly (e.g. from a Slack notification to HR). They nest under `interviews/[interviewId]/...` for URL clarity even though `interviews/[interviewId]/` itself has no `page.tsx` — Next.js resolves the leaf segments (`candidates/[candidateId]`, `live`) without requiring every intermediate segment to be its own page.
- **Parallel data fetching**: independent fetches use `Promise.all`, never sequential `await`s that create a waterfall. This matters especially on the interview detail page, which loads interview metadata, pipeline status, and candidate list concurrently.
- **`generateMetadata` on every page** that's reachable by direct URL (interview detail, candidate report) so titles/descriptions are correct for bookmarking and sharing internally.

### Component & File Rules

- **Server/Client boundary is explicit and minimal**: a Client Component file contains only what needs to be client. Don't mark a whole page `"use client"` because one button needs `onClick`.
- **No business logic in components**: data transformation, scoring display logic, pipeline-stage-to-label mapping, etc. live in `src/lib/` or a feature's `logic.ts`, and are unit-testable independent of React.
- **Naming**: components are `PascalCase` files exporting a single default component matching the filename (`InterviewStatusBadge.tsx` exports `InterviewStatusBadge`). Hooks are `useX` in `camelCase` files. Follow the global "no ambiguous names" rule (`data`, `handler`, `item`, etc. banned) — this app has enough near-identical domain nouns (`interview`, `session`, `candidate`, `report`) that vague names are especially easy to misread.
- **No silent `any` casts to work around a type error**: if a generated API type is wrong or missing, fix the generation step or flag it — don't `as any` past it.

### Real-Time Interview Room Behavior

- The live-interview view is the one part of this app that behaves like a long-lived client app inside a Server-first app: isolate it under `src/features/live-interview/` and treat everything inside as Client Components by necessity.
- Token fetch (from `apps/backend`) happens once, server-side if possible (e.g. in the page's Server Component, passed down as a prop), so the LiveKit token never touches an extra client round-trip if it doesn't need to.
- Reconnection, mic/connection-state UI, and transcript streaming are wrapped so a dropped connection degrades to a visible "reconnecting" state — never a silent frozen UI.

---

## 3. Directory Tree & Structure

```text
apps/frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── sign-in/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx                 # authenticated shell: nav, HR session check
│   │   │   ├── page.tsx                   # overview / home
│   │   │   ├── interviews/
│   │   │   │   ├── page.tsx               # list of interviews; row/card click opens
│   │   │   │   │                          # InterviewDetailDialog (popup, not a route)
│   │   │   │   ├── loading.tsx
│   │   │   │   ├── new/
│   │   │   │   │   └── page.tsx           # create interview (input interview info -> agent plan)
│   │   │   │   └── [interviewId]/         # NOTE: no page.tsx here — detail is a popup, not a page.
│   │   │   │       │                      # This segment exists only to give the pages below a clear URL.
│   │   │   │       ├── live/
│   │   │   │       │   └── page.tsx       # real-time room (HR observe/join) — real page
│   │   │   │       │       ├── loading.tsx
│   │   │   │       │       └── error.tsx
│   │   │   │       └── candidates/
│   │   │   │           └── [candidateId]/
│   │   │   │               ├── page.tsx   # candidate report & score — real page
│   │   │   │               ├── loading.tsx
│   │   │   │               └── error.tsx
│   │   │   └── settings/
│   │   │       └── page.tsx
│   │   ├── api/
│   │   │   └── webhooks/
│   │   │       └── backend/
│   │   │           └── route.ts           # narrow BFF: backend-pushed callbacks only
│   │   ├── layout.tsx                     # root layout
│   │   ├── loading.tsx
│   │   ├── error.tsx
│   │   ├── not-found.tsx
│   │   └── globals.css                    # Tailwind entrypoint
│   ├── components/
│   │   ├── ui/                            # shadcn/ui primitives (generated, owned)
│   │   └── layout/                        # nav, sidebar, shell chrome
│   ├── features/
│   │   ├── interviews/
│   │   │   ├── components/                # InterviewCard, PipelineStatusBadge,
│   │   │   │                              # InterviewDetailDialog (popup, driven by ?interview=<id>)
│   │   │   ├── actions.ts                 # Server Actions (create, edit, cancel)
│   │   │   ├── queries.ts                 # React Query hooks for status polling
│   │   │   └── schema.ts                  # zod form schemas
│   │   ├── candidates/
│   │   │   ├── components/                # ReportSummary, ScoreBreakdown, RubricTable
│   │   │   ├── queries.ts
│   │   │   └── schema.ts
│   │   ├── live-interview/
│   │   │   ├── components/                # RoomView, TranscriptPanel, ConnectionState
│   │   │   ├── hooks/                     # useLiveKitRoom, useInterviewToken
│   │   │   └── GEMINI.md                  # only if this feature needs local overrides
│   │   └── auth/
│   │       ├── actions.ts
│   │       └── schema.ts
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts                  # typed fetch wrapper
│   │   │   └── generated/                 # OpenAPI-generated types from apps/backend
│   │   ├── auth/
│   │   │   └── session.ts                 # server-side session helpers
│   │   └── utils.ts
│   ├── hooks/                             # cross-feature reusable hooks
│   ├── stores/                            # zustand stores (client-only UI state)
│   ├── types/                             # app-local types not covered by generated/shared schemas
│   └── middleware.ts                      # edge auth gate for (dashboard)
├── public/
├── tests/
│   └── e2e/                               # Playwright specs for critical HR flows
├── tailwind.config.ts
├── next.config.ts
├── tsconfig.json
├── package.json
└── GEMINI.md                              # this file
```

### Notes on the tree

- **`src/app/` stays thin.** Pages compose from `src/features/*` and `src/components/*`; a `page.tsx` should read like an outline, not contain the implementation.
- **`src/features/*` is the unit of ownership.** Each feature owns its components, its Server Actions, its React Query hooks, and its zod schemas. Cross-feature reuse goes through `src/components/`, `src/hooks/`, or `src/lib/` — features don't import each other's internals directly.
- **`lib/api/generated/` is never hand-edited.** It's regenerated from `apps/backend`'s OpenAPI spec; if a type is wrong, the fix happens in the backend schema, not here.
- Every functional folder still needs the global `MANIFEST.md` per the root rules — this tree just fixes _where_ things go, not the manifest requirement.
