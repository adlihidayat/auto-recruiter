# src/features/interviews Manifest

This directory manages interview campaigns, status badges, metrics, campaign creation forms, and modal detail views.

| File Name | Purpose | Key Exports/Dependencies |
| --- | --- | --- |
| `types.ts` | TypeScript domain shapes for campaign, suite, candidate models | `PipelineStage`, `InterviewCampaign`, `QuestionItem`, `CandidateRecord` |
| `components/InterviewStatusBadge.tsx` | Visual badge for 3-agent pipeline execution stages | `InterviewStatusBadge` (`lucide-react`) |
| `components/InterviewMetricsHeader.tsx` | Dashboard metric overview cards component | `InterviewMetricsHeader` (`lucide-react`) |
| `components/InterviewCard.tsx` | Individual campaign card with trigger for popup modal | `InterviewCard` (`lucide-react`) |
| `components/InterviewDetailDialog.tsx` | Modal dialog popup driven by `?interview=<id>` search params | `InterviewDetailDialog` (`lucide-react`, `next/navigation`) |
| `components/CreateInterviewModal.tsx` | Modal form to initialize new campaign and trigger Agent 1 | `CreateInterviewModal` (`lucide-react`) |
| `components/DashboardView.tsx` | Main dashboard container orchestrating campaigns & modals | `DashboardView` |
