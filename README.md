# DocChat

AI-powered document Q&A platform with streaming chat, hybrid search, and multi-source RAG.

## Stack
- **Backend**: FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL/pgvector + Redis
- **Frontend**: Next.js 14 (App Router) + TailwindCSS + shadcn/ui
- **AI**: OpenAI / Ollama (local LLM), RAG pipeline with hybrid search

## Status
Under construction — 14-day learning project.

## Quick start
```bash
cp .env.example .env
docker compose up -d
cd backend && uv sync
```
