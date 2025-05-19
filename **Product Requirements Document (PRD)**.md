**Product Requirements Document (PRD)**

**Product Name:** Intelligent PDF Processing & Agent Orchestration Pipeline

---

## 1. Purpose & Scope

**Objective:** Enable users to upload any PDF, automatically extract and store structured metadata, index content for semantic retrieval (RAG), generate strategic summaries, deep research insights, creative concepts, and full campaign pitches—all behind secured, testable, and extensible FastAPI endpoints.

**Scope:**
- Ingest and parse PDFs
- Chunking, embedding, and storing content in Supabase + pgvector
- Semantic retrieval via RAG
- Summarization and deep research chaining
- Creative concept generation and campaign assembly
- Authentication, CORS, logging, exception handling, and testing scaffolds

---

## 2. User Personas & Use Cases

**Personas:**
- **Marketing Strategist:** Rapidly surface key insights from long-form reports.
- **Content Marketer:** Build data-driven creative briefs and campaigns.
- **Developer/Integrator:** Embed AI-driven research pipelines into custom apps.

**Key Use Cases:**
1. **One‑click PDF analysis:** Upload a corporate whitepaper and receive a strategic summary.
2. **On‑demand RAG lookup:** Query deep into uploaded files for precise sections.
3. **Automated insight chaining:** Summaries trigger deeper research automatically.
4. **Creative ideation:** Generate campaign concepts from research summaries.
5. **Campaign pitch builder:** Assemble research + concepts into a cohesive pitch.

---

## 3. Functional Requirements

| Feature                        | Endpoint                 | Description                                                                                 |
|--------------------------------|--------------------------|---------------------------------------------------------------------------------------------|
| Upload PDF                     | `POST /upload`           | Accept PDF, extract metadata, split & embed text, store in Supabase & vector store.       |
| Contextual Upload              | `POST /upload_with_context` | Attach `user_id` & `project_id` metadata to ingested documents.                          |
| Semantic Retrieval             | `GET /retrieve`          | Return top‑k relevant text chunks for a query.                                             |
| Summary & Deep‑Research Chain  | `GET /summarize_and_chain` | Retrieve chunks → generate summary → store & trigger deeper insights.                   |
| Creative Concepts Generation   | `POST /creative_concepts` | Produce 3 campaign concepts from a summary, store in Supabase.                           |
| Campaign Builder               | `POST /build_campaign`    | Combine summary + concepts + tone into a full campaign pitch, store result.               |
| List Summaries                 | `GET /summaries`         | Paginated list of recent summaries.                                                       |
| Get Summary                    | `GET /summary/{id}`      | Fetch a single summary.                                                                    |
| List Creative Concepts         | `GET /creative_concepts` | List concepts, filterable by project.                                                      |
| Get Creative Concept           | `GET /creative_concepts/{id}` | Fetch an individual concept with source summary.                                        |
| List Campaign Pitches          | `GET /campaign_pitches`  | List pitches, filterable by project.                                                       |
| Get Campaign Pitch             | `GET /campaign_pitches/{id}` | Fetch a specific campaign pitch.                                                        |
| Health Check                   | `GET /health`            | Verify service and external dependency availability.                                       |

---

## 4. Non‑Functional Requirements

- **Security:** API‑key authentication middleware; optional CORS origin restriction; prepared for rate‑limiting.
- **Scalability:** Factory‑pattern FastAPI; containerized (MCP_Docker) deployment; pgvector pagination.
- **Testability:** App factory (`create_app()`); pytest scaffold; CI‑ready.
- **Observability:** Structured logging; global exception handler; health endpoint.
- **Extensibility:** Modular helper functions (e.g., `get_retriever()`); clear separation of concerns; roll‑your‑own webhook support.

---

## 5. Architecture & Technology

- **Backend Framework:** FastAPI (factory pattern)
- **Vector Store:** Supabase pgvector via LangChain
- **LLM:** OpenAI GPT‑4‑turbo via LangChain chains & prompt templates
- **Database:** Supabase Postgres for metadata, summaries, concepts, pitches
- **Deployment:** Docker (MCP_Docker); Uvicorn ASGI server
- **CI/Test:** Pytest + FastAPI TestClient

---

## 6. Success Metrics

- **Time to Insight:** < 60 seconds from upload to summary.
- **Retrieval Accuracy:** > 80% user‑rated relevance for /retrieve.
- **Pipeline Reliability:** 99.9% uptime; zero unhandled exceptions.
- **Adoption:** 50+ PDF analyses per week within first month.

---

## 7. Timeline & Milestones

| Phase               | Deliverables                                    | ETA       |
|---------------------|-------------------------------------------------|-----------|
| MVP Setup           | Core `/upload`, `/retrieve`, `/summarize_and_chain` | Week 1    |
| Insight & Concepts  | `/creative_concepts`, `/build_campaign`          | Week 2    |
| Security & Testing  | Auth, CORS, logging, pytest scaffold            | Week 3    |
| Refinement & Docs   | OpenAPI tags, rate‑limiting, DevDocs             | Week 4    |

---

## 8. Risks & Mitigations

- **Large PDF Handling:** Use chunked loading; monitor memory; queue long jobs.  
- **Embedding Cost/Latency:** Tune chunk sizes; batch embeds; cache embeddings.  
- **LLM Hallucination:** Guardrail via citation return; manual spot‑checks; fallback to human.    

---

**End of PRD**

