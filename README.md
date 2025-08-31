
# NHL26 League — Deployable Project

This repo contains a backend (FastAPI) and frontend (Vite + React) for an NHL26-style online league.
It includes endpoints for detailed player/goalie/team stats, leaderboards, standings, awards, and screenshot upload per game.

## Quick local run (Docker)
1. Install Docker & Docker Compose.
2. From project root run:
   ```bash
   docker-compose up --build
   ```
3. Frontend available at http://localhost:3000 and API at http://localhost:8000

## Deploy (free hosting)
- **API**: Use Render or Railway. Connect the `backend` folder as a Python service. Set env `ADMIN_API_KEY` and enable persistent Postgres if desired.
- **Frontend**: Use Vercel or Netlify. Connect the `frontend` folder and set `VITE_API_BASE` to your deployed API URL.

## Notes
- Default API key is `changeme`. Change this for production.
- For production use Postgres; update `DATABASE_URL` accordingly.
- The admin UI is included in the frontend. You can extend it with authentication (recommended).
