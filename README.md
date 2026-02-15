# ConferPilotAI

ConferPilot helps researchers through the entire conference submission journey from searching conferences to validated submission.

## What this MVP includes

- **FastAPI web engine** to ingest and search conferences.
- **Supabase/PostgreSQL storage** with indexes for semantic + symbolic retrieval.
- **Hybrid ranking strategy** that combines:
  - semantic relevance (`pgvector` cosine similarity),
  - symbolic relevance (trigram text similarity),
  - user profile constraints (interests, region, budget, career stage).

## Architecture

1. Client sends a search query and user profile to `POST /search`.
2. API computes an embedding placeholder (replace with your embedding model).
3. API calls a PostgreSQL RPC function (`search_conferences_hybrid`).
4. SQL function ranks conferences using weighted score:

```text
final = semantic*0.55 + symbolic*0.25 + profile*0.20
```

## Project structure

- `app/main.py`: FastAPI API with ingest and search endpoints.
- `db/schema.sql`: Supabase SQL schema + hybrid search function.
- `.env.example`: required environment variables.

## Setup

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Copy env file and fill credentials:

```bash
cp .env.example .env
```

3. In Supabase SQL editor, run:

```sql
-- paste db/schema.sql
```

4. Run the API:

```bash
uvicorn app.main:app --reload
```

## API examples

### Add conference

```bash
curl -X POST http://localhost:8000/conferences \
  -H "Content-Type: application/json" \
  -d '{
    "name": "NeurIPS",
    "acronym": "NeurIPS",
    "cfp_url": "https://neurips.cc",
    "submission_deadline": "2026-05-10",
    "start_date": "2026-12-01",
    "end_date": "2026-12-07",
    "location_city": "Vancouver",
    "location_country": "Canada",
    "region": "North America",
    "hybrid_mode": "hybrid",
    "topics": ["machine learning", "deep learning"],
    "description": "Top-tier machine learning conference",
    "estimated_cost_usd": 1200
  }'
```

### Search conferences

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "efficient transformers for NLP",
    "top_k": 5,
    "profile": {
      "interests": ["nlp", "transformers", "machine learning"],
      "preferred_regions": ["Europe", "North America"],
      "max_budget_usd": 1500,
      "career_stage": "student"
    }
  }'
```

## Next improvements

- Replace placeholder embedding generation with OpenAI/SentenceTransformers model API.
- Add crawler workers for conference sources (WikiCFP, conference websites).
- Add auth + saved profiles + feedback loops.
- Add a frontend dashboard for personalized recommendations.
