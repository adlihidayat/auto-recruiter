# The Code Style (Behavior) & Execution Protocol

## 0. Rule Cascade & Local Overrides (Hierarchical Architecture)

This workspace uses a hierarchical configuration model. The global `GEMINI.md` (this file) defines universal behaviors and boundaries. However, individual applications and packages maintain their own localized tech stacks and rules.

- **Always Check Local Rules First**: Before generating, editing, or analyzing code inside any subdirectory under `apps/*` or `packages/*`, you must check if a localized `GEMINI.md` exists in that specific app or package root.
- **Inheritance**: You must combine the global behavioral rules from this file with the specific technical constraints found in the local `GEMINI.md`.
- **Conflict Resolution**: If a localized `GEMINI.md` rule explicitly contradicts a global rule (e.g., a specific naming convention for a framework), **the localized rule always takes precedence** for files within that directory.

You are operating within a monorepo workspace. You must strictly adhere to the following behavioral, structural, and procedural rules across all files and languages.

## 1. Documentation & Commenting Standards

Code must be self-documenting through naming, but explicitly annotated for architectural intent and future readability.

### File Header Docstrings

Every file created or significantly modified must start with a high-density docstring block answering:

- **What**: The primary responsibility of this file (1-2 sentences).
- **Why**: Why this module exists within the broader architecture.
- **Boundaries**: What this file explicitly _does not_ handle (to prevent scope creep).

### Function & Complex Logic Micro-Comments

Do not write noise comments that merely restate syntax (e.g., do NOT write `// filter active users` above `users.filter(u => u.active)`). Instead:

- **Function/Method Docstrings**: Every exported function, class, or complex method must have a concise 1-2 line comment (JSDoc/TSDoc style) explaining its **intent**, any non-obvious parameters, and expected return values.
- **The "Why" Over "What"**: For intricate business logic, regex, or algorithmic blocks, add a short inline comment explaining _why_ this approach was chosen or what edge case it prevents so future developers can understand the reasoning.

## 2. High-Density Semantic Naming

Adopt an expressive, highly semantic naming convention to maximize code readability without relying on inline comments.

- **Formulas for Functions/Methods**: Use `Action + Target + Context/Condition` (e.g., `extractUserSessionFromToken()`, `validateOrderPayloadOrReject()`).
- **Formulas for Variables/State**: Clearly describe the content and state (e.g., `isUserAuthenticated`, `activeClientConnectionPool`).
- **Strictly Banned Terms**: Do not use ambiguous, generic names such as `data`, `res`, `val`, `item`, `manager`, `handler`, `temp`, or `obj`. If a variable represents a list of active users, name it `activeUserAccounts`, not `userList` or `data`.

## 3. Sub-directory Mini Manifests

To maintain context efficiency across the monorepo, every distinct functional folder or sub-directory must contain a localized manifest file named `MANIFEST.md` (or `README.md`).

- **Read First**: Before modifying or adding files in a directory, read its manifest to understand the local architecture.
- **Maintain State**: Whenever you create a new file, delete a file, or change a file's core responsibility, you must update the sub-directory's manifest in the same execution loop.
- **Manifest Format**: Keep it markdown-based with a simple table mapping: `| File Name | Purpose | Key Exports/Dependencies |`.

## 4. Thinking & Retrieval Behavior (Anti-Hallucination)

Do not assume internal workspace structures, undocumented dependencies, or business logic.

- **Plan Mode First**: Before generating or refactoring complex code, outline your step-by-step logic and check existing directory manifests.
- **Elicitation Over Assumption**: If a required dependency, utility function, or architectural pattern is missing or ambiguous, **stop execution and ask the user for clarification**.
- **No Silent Fallbacks**: Never mock, stub, or invent undocumented internal libraries to make code compile. Explicitly flag missing requirements to the user.

## 5. The Map (Annotated Tree & Boundaries)

This monorepo houses a React web application, a core Node.js backend, and a specialized AI agent service. Strict dependency and import boundaries must be respected at all times.

```
auto-recruiter/
├── apps/
│   ├── agents/        # AI Service (Prompt templates, LLM routing, agentic tools)
│   ├── backend/       # Node.js core API (Auth, DB, general business logic)
│   └── frontend/      # React web app (UI layer, client state, API consumption)
├── packages/
│   ├── shared-ui/     # Reusable React components (Dumb UI, no business logic)
│   └── utils/         # Universal helpers (Pure functions, framework-agnostic)
├── tools/             # Custom build scripts, generators, and CI/CD helpers
├── configs/           # Shared workspace configs (ESLint, Jest, TypeScript, etc.)
└── package.json       # Root workspace configuration
```

## 6. The Verification Loop (Self-Correction Protocol)

Never claim a task is complete without objective verification. Whenever you create or modify code, you must execute the following validation loop before finalizing your response:

### Step 1: Static Analysis & Type Checking

- Run the localized linter and type-checker for the modified package (e.g., `npm run lint` or `tsc --noEmit` within the specific workspace).
- Ensure zero TypeScript errors or ESLint warnings are introduced.

### Step 2: Targeted Testing

- Run the relevant unit or integration tests for the affected sub-directory or package only (avoid running the entire monorepo test suite to save time/compute).
- If tests do not exist for the newly written logic, write a minimal, targeted unit test to verify your changes.

### Step 3: The 3-Strike Escalation Rule

- If a verification step fails, analyze the error log and attempt a fix.
- You are permitted a **maximum of 3 consecutive self-correction attempts** for the same error.
- If the build or test still fails after 3 attempts, **stop execution immediately**. Do not hallucinate workarounds or disable lint/test rules. Present the exact error logs to the user and ask for guidance.

### What do you think?

Notice how **The 3-Strike Rule** saves your tokens? If the agent gets stuck in a loop trying to fix a complex bug, it won't burn 50,000 tokens guessing—it will stop after 3 tries and ask you.

Do you use a specific workspace runner (like `TurboRepo`, `Nx`, or `pnpm workspaces`)? If so, we can swap out the generic `npm run lint` in Step 1 with your exact terminal commands so the agent doesn't even have to guess how to run tests! 😉
