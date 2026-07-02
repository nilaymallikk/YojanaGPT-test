# YojanaGPT

RAG-based government scheme eligibility assistant for Indian citizens.

This monorepo contains:

- `backend`: FastAPI, PostgreSQL, Qdrant, hybrid retrieval, OpenRouter generation
- `frontend`: Next.js App Router citizen-facing scheme finder
- `docker-compose.yml`: local Postgres, Qdrant, backend, and frontend

## Quick Start

1. Copy environment examples:

   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env.local
   ```

2. Fill `OPENROUTER_API_KEY` in `.env` and `backend/.env`.

3. Start the stack:

   ```bash
   docker compose up --build
   ```

   If another local app already uses ports `3000`, `8000`, `5432`, or `6333`, use the included alternate-port override:

   ```bash
   docker compose -p yojana_gpt_test -f docker-compose.yml -f docker-compose.ports.yml up -d --build
   ```

4. Open:

   - Frontend: http://localhost:3000
   - Backend docs: http://localhost:8000/docs
   - Qdrant dashboard: http://localhost:6333/dashboard

   With the alternate-port override:

   - Frontend: http://localhost:3002
   - Backend docs: http://localhost:8001/docs
   - Qdrant dashboard: http://localhost:16333/dashboard

## Data Sources

Initial source priorities:

- myScheme: https://www.myscheme.gov.in/
- National Scholarship Portal: https://scholarships.gov.in/
- National Portal of India: https://www.india.gov.in/
- States and UTs Directory: https://www.india.gov.in/explore-india/facts-of-india/states-ut-districts
- data.gov.in APIs, if a data.gov.in API key is available
- API Setu, if selected API access is approved

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Notes

The real `.env` files are ignored by git. Keep API keys local.
