# Project Custom Rules & Preferences

## 1. Typography & Colors
- **Primary Dark Text (`gray-900`)**: Always map dark primary text to `#191919`.
- **Secondary Text (`gray-600`)**: Always map secondary gray text to `#646464`.
- Tailwind theme variables in `globals.css` map `--color-gray-900: #191919` and `--color-gray-600: #646464`. Keep all components aligned with `text-gray-900` and `text-gray-600`.

## 2. Git Staging Protocol
- **Strict Frontend Scoping**: NEVER run `git add .` from the monorepo root. Always explicitly scope git staging commands to `apps/frontend` (e.g., `git add apps/frontend`).

