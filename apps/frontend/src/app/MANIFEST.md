# src/app Manifest

This directory manages Next.js 15 App Router pages, layouts, and global styles.

| File Name | Purpose | Key Exports/Dependencies |
| --- | --- | --- |
| `layout.tsx` | Root HTML layout wrapper with Geist font providers | `RootLayout` |
| `page.tsx` | Main dashboard page composing Navbar and DashboardView | `DashboardPage` (`Navbar`, `DashboardView`) |
| `globals.css` | Tailwind v4 entrypoint with custom dark theme & glassmorphism | CSS variables and rules |
