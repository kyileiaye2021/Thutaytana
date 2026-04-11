# Thutaytana

Thutaytana is an AI-assisted research communication system that turns unstructured research notes + figures into editable poster drafts and exportable conference-ready PowerPoint posters.

It is designed for researchers who need to move quickly from raw project context to polished presentation artifacts.

---

## 1) Problem Statement

Researchers and students often face a repeated bottleneck before conferences:

- Research updates are scattered across lab notes, partial drafts, and figure folders.
- Converting long-form technical content into concise poster sections is time-consuming.
- Figures need contextual explanations and correct placement on the poster.
- Conference formatting constraints (e.g., 48x36 layout) are easy to miss under deadlines.

In short, the *research itself may be done*, but packaging it into a high-quality poster still costs significant manual effort.

---

## 2) Solution Approach

Thutaytana uses a multi-agent + deterministic rendering pipeline.

### High-level workflow

1. **User input**
   - User submits raw research text.
   - Optional figures are uploaded from the browser UI.

2. **Vision parsing (optional, image-aware mode)**
   - Uploaded images are encoded as data URIs.
   - A vision-capable LLM extracts:
     - detailed figure analysis,
     - quantitative metrics,
     - suggested poster section,
     - short figure caption.

3. **Research context structuring**
   - A parser LLM converts raw text + figure metadata into a strongly-typed research schema:
     - title,
     - introduction,
     - problem gap,
     - research goal,
     - methodology,
     - key results,
     - conclusion,
     - abstract.

4. **Poster bullet synthesis**
   - A dedicated formatter LLM rewrites paragraphs into concise, poster-friendly bullet points while preserving quantitative findings.

5. **Conference compliance parsing**
   - Conference rules are parsed into structured constraints (width, height, required sections, etc.).

6. **Deterministic poster generation**
   - A python-pptx layout engine renders:
     - title,
     - three-column section content,
     - routed figures,
     - conference-compliant dimensions.

7. **Editable review + export**
   - User can edit generated content in the draft editor.
   - Poster is exported as `.pptx` through `/api/download-pptx`.

---

## 3) System Architecture

### Backend API (FastAPI)

- `GET /`
  - Serves the main UI.
- `POST /api/draft`
  - Accepts raw text + optional image files.
  - Runs figure parser (if images), research parser, and bullet formatter.
  - Returns populated editor HTML.
- `POST /api/download-pptx`
  - Accepts edited sections + optional serialized vision metadata.
  - Generates downloadable poster PowerPoint.

### Agent and model layers

- **Research context parser**: structured extraction from raw research narrative.
- **Figure parser**: multimodal interpretation + section routing metadata.
- **Poster formatter**: compresses research prose to concise bullets.
- **Conference parser**: extracts formal conference constraints.

### Rendering layer

A deterministic Python generator handles layout and export so final file construction is predictable and reproducible.

---

## 4) Tech Stack

### Core backend

- **Python 3**
- **FastAPI** for web/API endpoints
- **Jinja2 Templates** for server-rendered UI responses

### LLM and agent orchestration

- **LangChain** prompt chains + structured outputs
- **Groq models** (via `langchain_groq`) for parsing and formatting agents
- Optional/legacy OpenAI integration present in parser code paths

### Data validation / contracts

- **Pydantic models** for strict output schemas and typed payloads

### Poster generation

- **python-pptx** for `.pptx` authoring

### Frontend

- **HTML + vanilla JavaScript**
- **Tailwind CSS (CDN)** for styling
- **HTMX included** with custom JS form upload flow

### Crawling / research utilities

- **Scrapy** spider in `mycrawler/` for conference-related data collection experiments

---

## 5) Repository Structure

```text
.
├── app.py                          # FastAPI app and endpoints
├── models.py                       # Pydantic schemas for context, figures, rules, bullets
├── research_parser.py              # Research + figure parsing agents
├── generate_poster.py              # Poster formatter agent + deterministic pptx builder
├── conference_parser.py            # Conference rule parser
├── templates/
│   ├── index.html                  # Input UI
│   └── draft_editor.html           # Editable AI-generated poster draft
└── mycrawler/                      # Scrapy crawler experiments
```

---

## 6) Running the Project

> The project currently assumes API credentials are available through environment variables loaded via `.env`.

### Quick start

1. Install dependencies (project-specific; add your preferred environment manager).
2. Configure model API keys in `.env`.
3. Start server:

```bash
uvicorn app:app --reload
```

4. Open:

```text
http://127.0.0.1:8000
```

---

## 7) Current Strengths

- End-to-end flow from raw notes to downloadable poster.
- Supports both text-only and text+figure workflows.
- Strong schema discipline using Pydantic structured outputs.
- Human-in-the-loop editing before final export.
- Deterministic rendering layer for layout reproducibility.

---

## 8) Known Gaps / Limitations

- No persistent storage yet (uploads/output are local filesystem-based).
- Authentication / multi-user session isolation not implemented.
- Limited conference rule coverage in default flow (currently seeded with a default guideline string in export path).
- No automated test suite/check pipeline is currently defined in repo.
- Output quality depends on model availability + prompt adherence.

---

## 9) Future Direction (Roadmap)

### Near-term (product hardening)

- Add dependency lockfile + reproducible setup instructions.
- Add automated tests for:
  - Pydantic contracts,
  - API endpoints,
  - deterministic PPTX generation sanity checks.
- Introduce robust file naming and collision-safe upload handling.
- Improve validation and graceful error handling for malformed user inputs.

### Mid-term (feature depth)

- Conference-specific template profiles (different layouts, branding, font constraints).
- Slide deck generation pipeline parallel to poster flow.
- Rich figure handling:
  - automatic captions on slides,
  - smarter section-image balancing,
  - optional image resizing/cropping.
- Editable section ordering and layout presets in the UI.

### Long-term (platform evolution)

- Multi-tenant architecture with user accounts and saved projects.
- Retrieval-backed personalization (lab style guide, conference history, institutional templates).
- Quality control layer for citation checks, metric consistency checks, and policy/compliance warnings.
- Collaborative editing + version history.
- Export targets beyond PPTX (PDF-first workflows, journal visual abstract templates).

---

## 10) Contribution Notes

If you plan to contribute, prioritize:

1. test coverage,
2. environment setup reproducibility,
3. clearer separation between agent logic and deterministic rendering,
4. API stability contracts for frontend integration.

---

## 11) Vision

Thutaytana’s long-term vision is to become a *research communication copilot* that helps researchers spend less time formatting and more time doing science.

