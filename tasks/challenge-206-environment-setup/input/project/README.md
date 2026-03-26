# Task Tracker API

A simple REST API for managing tasks, built with Express and TypeScript.

## Setup

1. Copy `.env.example` to `.env` and fill in your values
2. Run `npm install`
3. Run `npm run build` to compile TypeScript
4. Run `npm test` to verify everything works
5. Run `npm start` to launch the server

## API Endpoints

- `GET /health` — Health check
- `GET /api/tasks` — List all tasks
- `POST /api/tasks` — Create a task
- `GET /api/tasks/:id` — Get a task
- `PATCH /api/tasks/:id` — Update a task
- `DELETE /api/tasks/:id` — Delete a task

## Environment Variables

- `PORT` — Server port (default: 3000)
- `DATABASE_URL` — Database connection string (required)
- `NODE_ENV` — Environment (development/production/test)
