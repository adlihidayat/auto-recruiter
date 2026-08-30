# Target UI Design System & Component Guidelines (temporary design.md)

> **Note**: This document captures the exact visual style, layout structure, typography, spacing, component anatomy, and color tokens analyzed from the complete set of 10 reference screenshots.

---

## 1. Global Visual Aesthetics & Tokens

### 1.1 Color Palette
- **Backgrounds**:
  - App Canvas Outer Background: `#F4F4F5` / `#F5F5F7` (soft cool off-white/light grey).
  - Main Panel & Card Background: `#FFFFFF` (pure white).
  - Sidebar Background: `#FAFAFA` / `#F9FAFB` (very subtle off-white).
  - Sub-card / Inset Container Background: `#F4F4F6` / `#F5F5F7`.
- **Text & Content**:
  - Primary Text: `#18181B` / `#09090B` (high-contrast deep charcoal/black).
  - Secondary / Muted Text: `#71717A` / `#616161` (medium neutral grey).
  - Subtle / Disabled Text: `#A1A1AA` / `#B8B8B8` (light grey).
- **Accents & Status Colors**:
  - Primary Action / Dark Button: `#18181B` (solid black/dark grey).
  - Active/Success Pill: `bg-[#DCFCE7] text-[#15803D]` / `bg-[#ECFDF5] text-[#047857]`.
  - Draft/Info Pill: `bg-[#DBEAFE] text-[#1D4ED8]`.
  - Paused/Warning Pill: `bg-[#FEF3C7] text-[#D97706]`.
  - Ended/Inactive Pill: `bg-[#F3F4F6] text-[#374151]`.
  - Primary Brand Blue: `#0080FF` / `#0284C7`.
  - Alert / Disconnect Red: `#EA4335` / `#DC2626`.

### 1.2 Typography & Hierarchy
- **Font Family**: Inter, SF Pro Text, or System Sans-Serif (`font-sans`).
- **Font Weights**:
  - Regular: `400` (body descriptions, secondary labels).
  - Medium: `500` (navigation links, subtext, table values).
  - Semibold: `600` (section titles, button labels, key values).
  - Bold: `700` / `800` (page titles, prominent headers).
- **Font Sizes**:
  - Extra Small (`text-xs` / `12px`): Badges, tooltips.
  - Small (`text-sm` / `14px`): Sidebar nav items, table rows, button text.
  - Medium / Base (`text-base` / `16px`): Section titles.
  - Large / Heading (`text-xl` / `20px` to `text-2xl` / `24px`): Main titles.

### 1.3 Radii & Elevation
- **Border Radius**:
  - Outer App Shell Container: `rounded-[24px]` / `rounded-[28px]` or even `rounded-[32px]`.
  - Cards & Modals: `rounded-[20px]` / `rounded-[24px]`.
  - Inner Containers & Insets: `rounded-[14px]` / `rounded-[16px]`.
  - Buttons & Inputs: `rounded-[12px]` / `rounded-[14px]`.
  - Badges & Pills: `rounded-full` or `rounded-[6px]`.
- **Borders & Dividers**:
  - Subtle 1px borders throughout: `border-[#E4E4E7]` / `border-[#F1F1F3]`.
  - Horizontal dividers: `border-b border-[#F1F1F6]`.
- **Shadows**:
  - Soft multi-layered elevation: `shadow-[0_8px_30px_rgb(0,0,0,0.04)]` or `shadow-2xl`.

---

## 2. Layout Structure & Geometry (Refined based on Image 10)

### 2.1 Full-Screen Windowed App Layout
The app takes up the entire browser viewport but creates an inner "windowed" effect.
```
+-----------------------------------------------------------------------------------+
|  Body (bg-[#F4F4F5] p-2 or p-3 h-screen overflow-hidden)                          |
|  +-----------------------------------------------------------------------------+  |
|  | Main App Container (bg-white rounded-[28px] shadow-sm flex h-full border)   |  |
|  | +------------------------+-----------------------------------------------+  |  |
|  | | Sidebar (~240px)       | Main Dashboard Area (Flex-1)                  |  |  |
|  | | bg-[#FAFAFA]           | bg-white p-6 overflow-y-auto                  |  |  |
|  | | border-r               | - Page Header (Title + Actions)               |  |  |
|  | | - Workspace Dropdown   | - Overview Metric Cards                       |  |  |
|  | | - Search / Nav         | - Main Table Card (rounded-2xl, border)       |  |  |
|  | | - Categories & Tools   |                                               |  |  |
|  | | - Sticky Footer        |                                               |  |  |
|  | +------------------------+-----------------------------------------------+  |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

### 2.2 Dashboard Table Component (List of Interviews)
- **Container**: White card, `rounded-[20px]`, `border border-gray-200`.
- **Top Tabs**: Inline tab links inside the top of the card (`Campaigns 12`, `Ad sets 123`). Active tab has a black text color and bottom border indicator.
- **Toolbar**: 
  - `All view` dropdown button, `Search` text input with magnifying glass.
  - Right aligned filters: `Status`, `Metrics`.
- **Table Structure**:
  - Clean `thead` with uppercase, small, muted text (`text-xs text-gray-500 font-medium`).
  - Rows with subtle `border-b border-gray-100`.
  - Interactive cells: Toggle switches, platform icons, bold names, colorful status pills.
  - Hover states on rows: `hover:bg-gray-50`.

---

## 3. UI Redesign Strategy for Auto-Recruiter Dashboard

We will transform `DashboardView.tsx` and `app/page.tsx` into this exact layout:

1. **Remove standard `Navbar`**: Replace with the integrated Left Sidebar layout.
2. **Setup Windowed Shell**: Create the `bg-[#F4F4F5]` full height background and the rounded inner app frame.
3. **Sidebar Details**:
   - Logo: Auto-Recruiter.
   - Quick Search placeholder.
   - Nav items: `Overview`, `Analytics`, `Settings`.
   - Main Tool active: `Interviews`.
4. **Dashboard View**:
   - Header: `Interviews` + `Create Interview` dark button.
   - Metrics Card: Total Interviews, Active Candidates, Evaluated, Pass Rate.
   - **Table View**: Transform the current grid of `InterviewCard` into a sleek data table mimicking the "Campaigns" table from Image 10.
   - Table Columns: `Interview Position`, `Status` (Finished, In-Progress, Not-Started), `Target Seniority`, `Candidates`, `Created At`.
