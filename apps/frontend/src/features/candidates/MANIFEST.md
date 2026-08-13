# src/features/candidates Manifest

This directory owns the detailed candidate report view, which displays the AI-evaluated interview metrics, passing criteria, and detailed goal-by-goal breakdowns.

| File Name | Purpose | Key Exports/Dependencies |
| --- | --- | --- |
| `types.ts` | Defines the rich data model for the AI candidate report. | N/A |
| `components/CandidateReportView.tsx` | The monolithic Client Component responsible for rendering the detailed report. | Depends on `types.ts`, `lucide-react`. |
