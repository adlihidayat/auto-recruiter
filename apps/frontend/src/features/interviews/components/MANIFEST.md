# Interviews Components Mini Manifest

| File Name | Purpose | Key Exports/Dependencies |
| --- | --- | --- |
| `CreateInterviewModal.tsx` | Top-level container modal component orchestrating state & step switching. | `default export CreateInterviewModal` |
| `DashboardView.tsx` | Main interview dashboard page view with analytics chart, campaign tables & filter bar. | `default export DashboardView` |
| `InterviewMetricsHeader.tsx` | Metric summary cards for campaigns, candidates & completion rates. | `default export InterviewMetricsHeader` |
| `InterviewStatusBadge.tsx` | Visual status badge for interview states (`active`, `draft`, `completed`). | `default export InterviewStatusBadge` |
| `create-modal/types.ts` | Shared TypeScript data models (`InterviewFormData`, `CandidateInput`, `ModalStep`). | `ModalStep`, `CandidateInput`, `InterviewFormData` |
| `create-modal/constants.tsx` | Constants for agent pipeline steps, mock log entries, and Notion emoji list. | `AGENT_STEPS`, `MOCK_LOGS`, `EMOJIS` |
| `create-modal/EmojiPickerPopover.tsx` | Notion-style emoji selection popover grid. | `EmojiPickerPopover` |
| `create-modal/CanvasConfettiOverlay.tsx` | 60fps HTML5 Canvas particle confetti burst animation component. | `CanvasConfettiOverlay` |
| `create-modal/GoldenRosetteMedal.tsx` | Golden star award rosette medal graphic component (1.60x scaled). | `GoldenRosetteMedal` |
| `create-modal/CreateInterviewFormStep.tsx` | Step 1 Form view for role parameters, orange track slider, & candidates list. | `CreateInterviewFormStep` |
| `create-modal/CreateInterviewLoadingStep.tsx` | Step 2 Agent Handoff multi-agent progress, timer, and handoff log list. | `CreateInterviewLoadingStep` |
| `create-modal/CreateInterviewSuccessStep.tsx` | Step 3 Publish view displaying hero card, candidate links, & completion buttons. | `CreateInterviewSuccessStep` |
| `dashboard-popups/RowActionPopover.tsx` | Clean 3-dots action menu popover (View Details, Copy Link, Archive, Delete). | `RowActionPopover` |
| `dashboard-popups/StatusFilterPopover.tsx` | Radio button status selection popover (All, Finished, In-progress, Not started). | `StatusFilterPopover` |
| `dashboard-popups/ViewFilterPopover.tsx` | View preset selection popover (All campaigns, Active only, Archived). | `ViewFilterPopover` |
| `dashboard-popups/DepartmentFilterPopover.tsx` | Department filter popover list. | `DepartmentFilterPopover` |
| `dashboard-popups/CompareFilterPopover.tsx` | Date comparison range preset popover. | `CompareFilterPopover` |
| `dashboard-popups/MetricsFilterPopover.tsx` | Toggle switch popover for chart and stats cards display settings. | `MetricsFilterPopover` |
