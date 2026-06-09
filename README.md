# DocChat — AI-Powered Document Q&A

Hujjatlaringiz bilan AI orqali suhbatlashing. PDF / DOCX / TXT yuklang, savol bering — AI manbalar bilan javob beradi.

## Xususiyatlar

- Multi-format hujjat yuklash (PDF, DOCX, TXT, MD)
- RAG-ga asoslangan Q&A — manba ko'rsatishlar bilan
- Real-time streaming javoblar (WebSocket, token-by-token)
- Hybrid search (vector + BM25 + RRF)
- JWT autentifikatsiya + role-based access (admin)
- Background hujjat indekslash (arq + Redis)
- Embedding & LLM response cache (Redis)
- Sliding-window rate limiting
- Connection pooling (PostgreSQL, Redis, HTTP)

## Tech Stack

**Backend**: FastAPI · SQLAlchemy 2.0 (async) · PostgreSQL + pgvector · Redis · arq · Alembic
**Frontend**: Next.js 14 (App Router) · TypeScript · TailwindCSS · shadcn/ui · react-markdown
**AI**: OpenAI / Ollama · RAG pipeline · HNSW vector search · BM25 full-text

## Tezkor boshlash (Docker)

```bash
git clone <repo>
cd docchat
cp .env.example .env   # OPENAI_API_KEY ni o'z key bilan to'ldiring
docker compose up --build
```

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

## Loyiha tuzilishi

```
docchat/
├── backend/
│   ├── app/
│   │   ├── core/                 # config, db, security, cache, llm, redis, http
│   │   │   └── llm/              # OpenAI / Ollama providers
│   │   ├── features/
│   │   │   ├── auth/             # JWT, register/login, roles
│   │   │   ├── chat/             # WebSocket streaming chat
│   │   │   ├── documents/        # Upload, list, status
│   │   │   └── rag/              # Parser, chunker, ingestion, retrieval, generation
│   │   ├── worker.py             # arq background worker
│   │   └── main.py               # FastAPI entrypoint
│   ├── alembic/                  # Migrations (5 jadval + pgvector + HNSW + BM25)
│   ├── scripts/create_admin.py
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── (auth)/login,register
│   │   ├── chat/                 # Streaming chat UI
│   │   └── documents/            # Upload + list (status polling)
│   ├── components/               # AuthGuard, Header, FileUpload + shadcn/ui
│   ├── lib/                      # api, auth, useChat, upload, types
│   └── Dockerfile
└── docker-compose.yml            # postgres + redis + backend + worker + frontend
```

## RAG pipeline

```
INGESTION (upload da, background):
  PDF → parse → chunk (500 char, 50 overlap) → embed → pgvector ga saqlash

RETRIEVAL + GENERATION (har savolda):
  Savol → embed → vector search (HNSW) yoki hybrid (vector + BM25 + RRF)
        → top-k chunks → prompt → LLM → streaming javob (manbalar bilan)
```

## Mahalliy development

```bash
# Postgres + Redis
docker compose up -d postgres redis

# Backend
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload

# Worker (alohida terminalda)
uv run arq app.worker.WorkerSettings

# Frontend (alohida terminalda)
cd frontend
npm install
npm run dev
```

## Admin yaratish

```bash
cd backend
uv run python scripts/create_admin.py
```

## Asosiy endpointlar

| Method | Path | Tavsif |
|--------|------|--------|
| POST | `/api/v1/auth/register` | Ro'yxatdan o'tish |
| POST | `/api/v1/auth/login/json` | Login (JSON) |
| POST | `/api/v1/auth/login` | Login (OAuth2 form, Swagger uchun) |
| GET | `/api/v1/auth/me` | Joriy user |
| GET | `/api/v1/auth/users` | Hammasi (admin only) |
| POST | `/api/v1/documents/upload` | Hujjat yuklash (+ background indexing) |
| GET | `/api/v1/documents/` | Foydalanuvchi hujjatlari |
| GET | `/api/v1/documents/{id}` | Bitta hujjat statusi |
| GET | `/api/v1/rag/search?q=...&hybrid=true` | Semantic / hybrid search |
| WS | `/api/v1/chat/ws?token=...` | Real-time streaming chat |

## Environment

`.env.example` ni nusxalang va to'ldiring:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:55432/docchat
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=<min 32 belgi>
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
EMBEDDING_DIMENSION=1536
```

Ollama uchun: `LLM_PROVIDER=ollama`, `OLLAMA_BASE_URL=http://localhost:11434`, `EMBEDDING_DIMENSION=768` (nomic-embed-text).

## 14 kunlik sayohat

| Kun | Mavzu |
|-----|-------|
| 1 | Loyiha skeleton + Docker (PostgreSQL + Redis + pgvector) |
| 2 | Async Python (event loop, coroutines, cancellation) |
| 3 | FastAPI app, Pydantic v2, mock endpointlar |
| 4 | SQLAlchemy 2.0 async + Alembic + 5 model + repositoriylar |
| 5 | JWT, bcrypt, OAuth2 scheme, role-based access |
| 6 | WebSocket streaming + arq background worker |
| 7 | Redis client, caching, rate limiting, connection pooling |
| 8 | LLM provider (OpenAI/Ollama), embeddings, vector search |
| 9 | To'liq RAG pipeline: parser + chunker + ingestion + retrieval + generation |
| 10 | BM25 full-text + hybrid search (RRF) |
| 11 | Next.js 14 setup, auth sahifalari |
| 12 | WebSocket chat UI + file upload (drag-drop, polling) |
| 13 | Docker integration (3 ta Dockerfile, to'liq compose) |
| 14 | Polish + README + demo |

## Litsenziya

MIT
