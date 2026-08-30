# Auto-Recruiter: Product Requirements Document (PRD)

---

## 1. Executive Summary & Application Goal

### 1.1 Overview
**Auto-Recruiter** is an end-to-end, AI-powered automated recruitment and candidate screening platform. It empowers HR recruiters and hiring managers to create customized job interview campaigns, invite candidates, conduct real-time AI voice interviews, and inspect detailed candidate evaluation reports.

### 1.2 Core Value Proposition
- **Automated Voice Screening**: Replaces initial phone screeners with a real-time conversational AI interviewer capable of conducting goal-driven technical and behavioral assessments.
- **Data-Driven Candidate Evaluation**: Automatically grades candidates on Knowledge, Communication, and Job Alignment, generating actionable hiring recommendations (*Advance*, *Advance with follow-up*, or *Hold*).
- **Recruiter Efficiency**: Provides recruiters with a central dashboard to monitor active campaigns, inspect candidate transcripts turn-by-turn, and manage hiring pipelines effortlessly.

---

## 2. Sitemap & Application Architecture

The application consists of two main user-facing domains:
1. **Recruiter Portal (Dashboard & Reports)**: Requires authentication (`Bearer` JWT token).
2. **Candidate Portal (Live Voice Interview)**: Accessible via unique interview room tokens (`/interview/[token]`).

```
Auto-Recruiter Workspace
├── Recruiter Portal
│   ├── Login / Sign-In Page (/login)
│   ├── Campaign Dashboard (/ or /interviews)
│   │   ├── Create Interview Position Modal (Popup)
│   │   └── Interview Campaign Detail Drawer (Popup via ?interview=[id])
│   └── Candidate Evaluation & Grading Report (/interviews/[interviewId]/candidates/[candidateId])
│
└── Candidate Portal
    └── Live AI Voice Interview Flow (/interview/[token])
        ├── Phase 1: Pre-Room Lobby & Audio Device Test
        ├── Phase 2: Live AI Voice Conversation Stage
        └── Phase 3: Post-Interview Completion Screen
```

---

## 3. Detailed Page-by-Page Specifications

### Page 1: Authentication / Sign-In (`/login`)
- **Target Audience**: HR Recruiters & System Administrators.
- **Purpose**: Authenticate recruiters via OAuth2 password flow to generate a JWT access token stored in secure cookies (`access_token`).

#### Key Features & UI Components:
1. **Branding Header**: Logo, application title, and welcoming subtext.
2. **Login Form**:
   - `Email` input (type text/email).
   - `Password` input (type password).
   - `Submit Button` with loading spinner state.
   - Inline error message banner for invalid credentials.
3. **Redesign / Stitch UI Goals**:
   - Clean, modern layout with subtle background gradients or glassmorphism card.
   - Smooth focus states and micro-interactions on button hover/click.

---

### Page 2: Recruiter Campaign Dashboard (`/` or `/interviews`)
- **Target Audience**: HR Recruiters.
- **Purpose**: Primary workspace showing high-level recruitment metrics, active campaigns grid, and quick actions to launch new interviews.

#### Key Features & UI Components:
1. **Top Header & Greeting**:
   - Current date badge (e.g., `Tuesday, 12 April 2026`).
   - Page title (`Overview`) and subtitle.
2. **Global Progress & Quick Actions**:
   - **Progress Visualizer**: A 17-bar visual indicator showing the overall completion percentage of interviews across all campaigns.
   - **Metrics Summary**: Finished vs total interview count (e.g., `8/12 Interviews`).
   - **Create Interview Button**: Opens the *Create Interview Position Modal*.
3. **Tab Filters**:
   - Filter campaigns by status: `All (Count)`, `Finished (Count)`, `In-progressed (Count)`, `Not started (Count)`.
4. **Campaign Cards Grid**:
   - 4-column responsive grid displaying individual interview campaign cards.
   - Each `InterviewCard` displays:
     - Job Title (e.g., *Marketing Lead Officer*, *Product Manager*, *CTO Officer*).
     - Department & Target Seniority badges (e.g., *Core*, *Senior*).
     - Candidate pipeline metrics (Active candidates, Evaluated candidates).
     - Creation date timestamp.
     - Agent short summary preview.
     - Click action: Opens the *Interview Campaign Detail Drawer* via URL query param `?interview=[id]`.

---

### Page 3: Create Interview Position Modal (Modal Popup)
- **Target Audience**: HR Recruiters.
- **Purpose**: A multi-step setup wizard to configure a new interview position and invite candidate emails.

#### Key Features & UI Components:
1. **Step 1: Job Configuration**:
   - `Job Position Title` (Required).
   - `Job Description` (Textarea, required).
   - `Target Seniority / Difficulty` dropdown (*Junior*, *Mid*, *Senior*).
   - `Domain Hint` (e.g., *React, TypeScript, Fintech*).
   - `Target Duration` slider or input (Minutes).
2. **Step 2: Candidate Invitations**:
   - Add single or batch candidate email inputs (First Name, Last Name, Email).
3. **Actions**:
   - `Cancel` and `Create Campaign` buttons.
   - Loading indicator while calling POST `/api/interviews`.
   - On success: Closes modal and refreshes dashboard list.

---

### Page 4: Interview Campaign Detail Drawer (`/?interview=[interviewId]`)
- **Target Audience**: HR Recruiters.
- **Purpose**: Right-hand slide-over drawer showing detailed metrics, full job description, management actions, and candidate roster for a specific campaign.

#### Key Features & UI Components:
1. **Header Action Controls**:
   - Close button (`X`), Share Link button (copies URL to clipboard), Edit Campaign button, Delete Campaign button.
2. **Campaign Overview**:
   - Job Title, creation date, department badge.
3. **Analytics Cards (Dual Cards)**:
   - **Card A: Interview Status**:
     - Completed / Total candidates count.
     - Progress bar with 3-color status distribution (Finished, In-progress, Not started).
     - Info hover tooltip: *"Shows candidate progress through the interview pipeline."*
   - **Card B: Passing Rate**:
     - Advance / Total candidates count & Advance rate percentage.
     - 3-color recommendation distribution bar (Green: Advance, Gray: Follow-up, Red: Hold).
     - Info hover tooltip: *"Shows the distribution of candidate scores and recommendations."*
4. **Expandable Job Description**:
   - Toggle button to expand/collapse full job summary text with smooth gradient overlay.
5. **Candidate Roster & Management**:
   - Candidate search / filter button (`SlidersHorizontal`) with dropdown filter by candidate status (`All`, `Not-started`, `On-Interview`, `Done`).
   - Scrollable candidate list:
     - Avatar, Full Name, Email.
     - Status badges (*finished*, *in-progress*, *Not-started*) or Recommendation badges (*Advance*, *Advance w/ follow-up*, *Hold*).
     - 3-Dot Options Menu (`MoreVertical`): Popover with `Open` (navigates to report) and `Delete` (removes candidate).

---

### Page 5: Candidate Evaluation & Grading Report (`/interviews/[interviewId]/candidates/[candidateId]`)
- **Target Audience**: HR Recruiters & Hiring Managers.
- **Purpose**: Deep-dive analytics report evaluating a single candidate's performance, strengths/weaknesses breakdown, and full conversation transcripts.

#### Key Features & UI Components:
1. **Top Grid (2 Cards Layout)**:
   - **Left Card: Candidate Profile & Executive Summary**:
     - Candidate Avatar, Name, Email.
     - AI-generated Short Summary paragraphs.
     - Highlight Bars (Green vertical bars for key strengths/passed criteria, Red vertical bars for concerns/failed criteria).
   - **Right Card: Verdict & Score Matrix**:
     - **Status Badge**: Decision pill (*Advance* [Green], *Advance with follow-up* [Grey], *Hold* [Red]) with concise rationale.
     - **Overall Score**: Numerical composite score (0-10 or 0-100) and percentile label (*Under average*, *Average*, *Pretty high*).
     - **Dual Score Breakdown Columns**:
       - *Knowledge Score*: Percentage, goal-by-goal breakdown matrix (Pass/Failed pills per evaluation goal), evaluation note, and "See Detail" link.
       - *Communication Score*: Pass/Fail rating, communication trait matrix (Clarity, Structure, Professionalism, Conciseness), evaluation note, and "See Detail" link.
2. **Bottom Card: Turn-by-Turn Interview Transcript**:
   - Sequential vertical timeline displaying exact conversational turns (`[T1]`, `[T2]`, ...).
   - Speaker tags (`Candidate` vs `Interviewer`) with color-coded bullet indicators.
   - Full transcript text for each turn.

---

### Page 6: Candidate Live Voice Interview Portal (`/interview/[token]`)
- **Target Audience**: Job Candidates undergoing an automated interview.
- **Purpose**: Provide a frictionless, browser-based real-time voice call environment with an AI interviewer.

#### Phase 1: Pre-Room Lobby & Device Test
- **Header**: Company logo and job position title.
- **Device Test Widget**:
  - Microphone selector dropdown & status label (e.g., *Default Microphone - Realtek Audio*).
  - Mute / Unmute test button.
  - **Real Microphone Volume Bar**: Dynamic Web Audio API volume bar showing live input level (`Listening...` vs `Receiving Sound` vs `Muted`).
  - Permission check notice if microphone access is blocked.
- **Guidelines**: Key rules (quiet environment, estimated 30 min duration).
- **Enter Interview Room Button**: Starts LiveKit room connection.

#### Phase 2: Live AI Voice Conversation Stage
- **LiveKit Room Integration**: WebSockets connection to LiveKit server and realtime voice worker.
- **Main Stage Display**:
  - Dark-mode stage with central AI Interviewer avatar.
  - Animated pulsing glow ring around avatar when AI is speaking.
  - Current AI State label (`speaking`, `listening`, `thinking`).
  - Real-time spoken transcript display bubble.
  - Audio Bar Visualizer showing agent voice output.
- **Bottom Control Bar**:
  - Candidate Mute / Unmute toggle button.
  - **Candidate Mic Level Indicator Bar**: Live volume meter showing candidate sound input.
  - **Leave Interview Button**: Gracefully disconnects from the room.

#### Phase 3: Post-Interview Completion Screen
- Confirmation checkmark icon.
- Thank you message explaining that responses have been saved and sent to the recruiting team for processing.

---

## 4. Key Data Entities & API Schemas

### Interview Campaign Object (`BackendInterviewResponse`)
```json
{
  "id": "uuid-string",
  "job_name": "Senior Backend Engineer",
  "job_description": "Job requirements...",
  "difficulty": "senior",
  "num_goals": 3,
  "total_duration_minutes": 30,
  "domain_hint": "Python & FastAPI",
  "status": "COMPLETED",
  "scheduled_at": "2026-09-01T09:00:00Z",
  "created_at": "2026-08-25T10:00:00Z"
}
```

### Candidate Object (`BackendCandidateResponse`)
```json
{
  "id": "uuid-string",
  "interview_id": "uuid-string",
  "email": "candidate@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "status": "EVALUATED",
  "composite_score": 8.5,
  "recommendation": "Advance",
  "room_token": "jwt-room-token"
}
```

### Candidate Report Object (`BackendCandidateReportResponse`)
```json
{
  "id": "uuid-string",
  "candidate_id": "uuid-string",
  "overall_confidence": "HIGH",
  "reasoning": "Candidate demonstrated strong backend skills...",
  "raw_report": {
    "overall_score": 8.5,
    "recommendation": "Advance",
    "goals": [
      { "topic": "System Design", "score": 9.0, "rationale": "Clear understanding of distributed systems" },
      { "topic": "Python Concurrency", "score": 8.0, "rationale": "Good grasp of asyncio" }
    ],
    "communication": {
      "overall": { "is_passed": true, "rationale": "Clear and articulate" },
      "traits": {
        "clarity": 9.0,
        "conciseness": 8.5
      }
    }
  }
}
```

---

## 5. UI/UX & Design Guidelines for Stitch Redesign

When designing the new UI layout in **Stitch**, adhere to these design principles:

1. **Aesthetic Tone & Vibe**:
   - **Professional yet Cutting-Edge**: Modern SaaS platform aesthetic (similar to Linear, Vercel, or Stripe).
   - **Color Palette**:
     - Primary Accent: Warm vibrant orange (`#FE6100` / `#E05600`).
     - Pass / Success: Emerald green (`#16A34A` / `#00C835`).
     - Warning / Follow-Up: Warm gray / Amber (`#828282` / `#F59E0B`).
     - Reject / Alert: Crimson red (`#DC2626`).
     - Backgrounds: Pristine white (`#FFFFFF`) with off-white containers (`#F8F9FA`, `#FBFBFB`) and subtle borders (`#F1F1F1`, `#E9E9E9`).
   - **Typography**: Clean sans-serif fonts (e.g. Inter, Outfit, or Roboto). High contrast for readability.
2. **Interactive Micro-Animations**:
   - Smooth slide-in animations for the detail drawer.
   - Pulsing glow rings for active voice states in the live interview.
   - Real-time smooth transitions for volume bars and visualizers.
3. **Card & Layout Geometry**:
   - Generous border radiuses (`rounded-2xl`, `rounded-[28px]`, `rounded-[36px]`).
   - Clean elevation and soft 2XS shadows (`shadow-2xs`, `shadow-xl`).
4. **No Placeholder Artifacts**:
   - All components must feel complete, with realistic sample data, micro-copy, clear status badges, and working empty states.

---
*Document Version: 1.0.0*  
*Last Updated: August 2026*  
