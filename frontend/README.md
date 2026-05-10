# Tool-21 Frontend

React 18 + Vite + Tailwind CSS frontend for Audit Planning & Scheduling

## Features

- JWT-based authentication
- Dashboard with KPI cards and analytics
- Audit list with search, filter, and export
- Create/Edit audits
- AI-powered analysis integration
- Responsive design (mobile, tablet, desktop)
- Error boundaries and loading states

## Tech Stack

- React 18
- Vite (fast build tool)
- Tailwind CSS (styling)
- Axios (HTTP client)
- React Router (routing)
- Recharts (analytics)
- Lucide React (icons)

## Setup

```bash
cd frontend
npm install
```

## Environment Variables

Create `.env` file:

```
VITE_API_URL=http://localhost:8080
```

## Development

```bash
npm run dev
```

App runs on http://localhost:5173

## Build

```bash
npm run build
npm run preview
```

## Pages

- **Login** (`/login`) - JWT authentication
- **Dashboard** (`/`) - KPI cards and charts
- **Audits** (`/audits`) - List, search, filter, export
- **Audit Detail** (`/audits/:id`) - View single audit with AI analysis
- **Create/Edit** (`/audits/new`, `/audits/:id/edit`) - Form with validation

## API Integration

All endpoints integrated via `src/services/api.js`:

- Authentication (login, register, refresh)
- Audit CRUD (create, read, update, delete, search)
- Export (CSV)
- Stats (dashboard data)
- AI service (describe, categorize, recommend, analyze)

## Security

- JWT tokens stored in localStorage
- Protected routes redirect to login
- Axios interceptor adds auth header automatically
- Input validation on forms

## Responsive Design

- Mobile-first Tailwind CSS
- 375px, 768px, 1280px breakpoints tested
- Responsive tables and charts
- Mobile navigation menu ready
