# Frontend documentation

## Project Overview

Cloud Content Hub AI is a Next.js workspace UI for content, upload, AI-studio, scheduling, analytics, account, and settings workflows. The current frontend is a mock-backed implementation: constants feed repositories, services, and client feature hooks. It does not call a backend.

## Technology Stack

- Next.js 15 App Router, React 19, strict TypeScript
- Tailwind CSS v4; Radix-based New York-style primitives
- Framer Motion, Recharts, react-day-picker, and react-dropzone
- Node.js 22.22.1 or newer

`package.json` records compatible dependency ranges; the lockfile pins the exact installation.

## How to Run

```sh
npm install
npm run dev
```

Open the URL printed by Next.js (normally `http://localhost:3000`).

## How to Build

```sh
npm run typecheck
npm run build
npm run start
```

`npm run lint` is declared, but verify it against the installed Next.js version before relying on it in automation.

## Project Structure

Routes and route-local feature implementations live in `app/`, with feature UI colocated under each route's `_components/` directory. Reusable UI lives in `components/`; mock data access is separated across `constants/`, `lib/adapters/`, and `lib/services/`. Shared hooks, styles, domain types, configuration, and utilities live in `hooks/`, `styles/`, and `lib/`.

## Development Workflow

1. Start from the route and its feature view.
2. Reuse category exports from `components/`.
3. Keep browser state in client components/hooks and data access behind services.
4. Run type-check and a production build before review.

## Documentation

- [Frontend overview](FRONTEND_OVERVIEW.md)
- [Developer guide](DEVELOPER_GUIDE.md)
- [Component guide](COMPONENT_GUIDE.md)
- [Folder structure](FOLDER_STRUCTURE.md)
- [State management](STATE_MANAGEMENT.md)
- [Routing](ROUTING_GUIDE.md)
- [Theming](THEMING_GUIDE.md)
- [Responsive design](RESPONSIVE_GUIDE.md)
- [Animation](ANIMATION_GUIDE.md)
- [Performance](PERFORMANCE_GUIDE.md)
- [Accessibility](ACCESSIBILITY_GUIDE.md)
- [Deployment](DEPLOYMENT_GUIDE.md)
- [Environment setup](ENVIRONMENT_SETUP.md)
