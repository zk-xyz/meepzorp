# === intelligent_pdf_pipeline.py ===
"""
Intelligent PDF Processing & Agent Orchestration Pipeline
- Upload, embed, summarize, deep research, and create concepts
- Built with FastAPI factory pattern for testability
"""
import os
import uuid
import tempfile
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from pydantic import BaseModel
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from langchain.vectorstores.supabase import SupabaseVectorStoreRetriever
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from supabase import create_client, Client
import httpx

# === App factory ===
def create_app():
    # --- Config & clients ---
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    API_KEY = os.getenv("PIPELINE_API_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Missing Supabase credentials")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    app = FastAPI()

    # --- Middleware for Auth ---
    @app.middleware("http")
    async def verify_api_key(request: Request, call_next):
        if request.url.path.startswith("/health"):
            return await call_next(request)
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            raise HTTPException(401, "Missing or invalid Authorization header")
        token = auth.split("Bearer ")[1]
        if token != API_KEY:
            raise HTTPException(403, "Invalid API key")
        return await call_next(request)

    # --- Pydantic schemas ---
    class UploadContext(BaseModel):
        user_id: str
        project_id: str

    # --- Helper: RAG retriever ---
    def get_retriever(top_k: int = 5):
        return SupabaseVectorStoreRetriever(
            client=supabase,
            embedding=OpenAIEmbeddings(),
            table_name="document_chunks",
            query_name="match_documents",
            top_k=top_k
        )

    # --- Endpoints ---
    @app.post("/upload")
    async def upload_pdf(file: UploadFile = File(...)):
        try:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            tmp.write(await file.read()); tmp_path = tmp.name; tmp.close()
            pages = PyPDFLoader(tmp_path).load()
            chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(pages)
        except Exception as e:
            raise HTTPException(422, f"PDF error: {e}")

        doc_id = str(uuid.uuid4())
        texts = [c.page_content for c in chunks]
        supabase.table("documents").insert({
            "id": doc_id,
            "title": file.filename,
            "source": "uploaded",
            "author": "unknown",
            "date": "unknown",
            "doc_url": tmp_path
        }).execute()
        SupabaseVectorStore(
            client=supabase,
            embedding=OpenAIEmbeddings(),
            table_name="document_chunks",
            query_name="match_documents"
        ).add_texts(texts, metadatas=[{"document_id": doc_id}] * len(texts))
        os.remove(tmp_path)
        return {"document_id": doc_id}

    @app.post("/upload_with_context")
    async def upload_with_context(file: UploadFile = File(...), context: UploadContext = None):
        result = await upload_pdf(file)
        if context:
            supabase.table("documents").update({
                "user_id": context.user_id,
                "project_id": context.project_id
            }).eq("id", result["document_id"]).execute()
        return result

    @app.get("/retrieve")
    async def retrieve_docs(query: str):
        if len(query) < 3:
            raise HTTPException(400, "Query too short")
        docs = get_retriever().get_relevant_documents(query)
        return {"results": [d.page_content for d in docs]}

    @app.get("/summarize_and_chain")
    async def summarize_and_chain(query: str):
        docs = get_retriever().get_relevant_documents(query)
        context = "\n\n".join([d.page_content for d in docs])

        prompt = PromptTemplate(
            input_variables=["context", "query"],
            template="""
You are a strategic research analyst.\nContext:\n{context}\nQuery:\n{query}\nStructured Summary:"""
        )
        summary = LLMChain(
            llm=ChatOpenAI(model_name="gpt-4-turbo", temperature=0.3),
            prompt=prompt
        ).run({"context": context, "query": query})

        meta = supabase.table("summaries").insert({
            "query": query,
            "summary": summary,
            "source_count": len(docs)
        }).execute()
        summary_id = meta.data[0]["id"] if meta.data else None

        insights = None
        if summary_id:
            insights = ChatOpenAI(model_name="gpt-4-turbo", temperature=0.4).predict(
                f"Given Summary: {summary}\nGenerate 3 deeper insights."
            )
        return {"summary_id": summary_id, "summary": summary, "insights": insights}

    @app.post("/creative_concepts")
    async def creative_concepts(summary_id: str):
        rec = supabase.table("summaries").select("summary,project_id,user_id").eq("id", summary_id).execute()
        if not rec.data:
            raise HTTPException(404, "Summary not found")
        summ = rec.data[0]
        prompt = f"Based on this summary, craft 3 campaign concepts:\n{summ['summary']}"
        concepts = ChatOpenAI(model_name="gpt-4-turbo", temperature=0.7).predict(prompt)
        supabase.table("creative_concepts").insert({
            "summary_id": summary_id,
            "project_id": summ["project_id"],
            "user_id": summ["user_id"],
            "concepts": concepts
        }).execute()
        return {"concepts": concepts}

    @app.get("/summaries")
    async def list_summaries():
        data = supabase.table("summaries").select("id,query,summary,created_at,source_count").order("created_at", desc=True).limit(20).execute()
        return {"summaries": data.data}

    @app.get("/summary/{summary_id}")
    async def get_summary(summary_id: str):
        rec = supabase.table("summaries").select("summary").eq("id", summary_id).execute()
        if not rec.data:
            raise HTTPException(404, "Not found")
        return {"summary": rec.data[0]}

    @app.get("/health")
    async def health_check():
        try:
            supabase.table("documents").select("id").limit(1).execute()
        except Exception:
            return {"status": "error"}
        return {"status": "ok"}

    return app

# Instantiate the app
app = create_app()

# === Creative Concepts Retrieval ===
@app.get("/creative_concepts")
async def list_creative_concepts(project_id: str = None, limit: int = 20):
    """
    List creative campaign concepts, optionally filtered by project_id.
    """
    query = supabase.table("creative_concepts").select("id, summary_id, concepts, created_at, project_id, user_id")
    if project_id:
        query = query.eq("project_id", project_id)
    data = query.order("created_at", desc=True).limit(limit).execute().data
    return {"creative_concepts": data}

@app.get("/creative_concepts/{concept_id}")
async def get_creative_concept(concept_id: str):
    """
    Retrieve a single creative concept by its ID, including linked summary and deep insights if needed.
    """
    rec = supabase.table("creative_concepts").select("*, summaries(summary)").eq("id", concept_id).execute()
    if not rec.data:
        raise HTTPException(404, "Creative concept not found")
    return rec.data[0]

# === Campaign Builder Endpoint ===
@app.post("/build_campaign")
async def build_campaign(concept_id: str, tone: str = "bold and engaging"):  # customizable tone
    """
    Assemble a full campaign pitch by combining research summary, deep insights, and creative concepts.
    """
    # Fetch creative concept and linked summary
    concept_rec = supabase.table("creative_concepts").select("concepts, summary_id, project_id, user_id").eq("id", concept_id).execute()
    if not concept_rec.data:
        raise HTTPException(404, "Concept not found")
    concept = concept_rec.data[0]["concepts"]
    summary_id = concept_rec.data[0]["summary_id"]

    summary_rec = supabase.table("summaries").select("summary, query").eq("id", summary_id).execute()
    summary_data = summary_rec.data[0]

    prompt = f"""
You are a senior campaign strategist. Using the research summary and creative concepts below, craft a comprehensive campaign pitch document.

Summary:
{summary_data['summary']}

Creative Concepts:
{concept}

Tone and Style: {tone}

Output: A structured pitch with executive summary, objectives, key messages, channels, and next steps.
"""
    pitch = ChatOpenAI(model_name="gpt-4-turbo", temperature=0.7).predict(prompt)

    # Optionally store the built campaign
    supabase.table("campaign_pitches").insert({
        "concept_id": concept_id,
        "project_id": concept_rec.data[0]["project_id"],
        "user_id": concept_rec.data[0]["user_id"],
        "pitch": pitch
    }).execute()

    return {"pitch": pitch}

# === Campaign Pitches Retrieval Endpoints ===
@app.get("/campaign_pitches")
async def list_campaign_pitches(project_id: str = None, limit: int = 20):
    """
    List campaign pitches, optionally filtered by project_id.
    """
    query = supabase.table("campaign_pitches").select("id, concept_id, pitch, created_at, project_id, user_id")
    if project_id:
        query = query.eq("project_id", project_id)
    data = query.order("created_at", desc=True).limit(limit).execute().data
    return {"campaign_pitches": data}

@app.get("/campaign_pitches/{pitch_id}")
async def get_campaign_pitch(pitch_id: str):
    """
    Retrieve a single campaign pitch by its ID.
    """
    rec = supabase.table("campaign_pitches").select("*").eq("id", pitch_id).execute()
    if not rec.data:
        raise HTTPException(404, "Campaign pitch not found")
    return rec.data[0]

# === Suggested Supabase migration for campaign_pitches ===
"""
create table campaign_pitches (
  id uuid primary key default gen_random_uuid(),
  concept_id uuid references creative_concepts(id),
  user_id text,
  project_id text,
  pitch text,
  created_at timestamp with time zone default now()
);
"""

# === ASGI Entrypoint ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "intelligent_pdf_pipeline:create_app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info",
        reload=bool(os.getenv("RELOAD", False))
    )

# === Testing Scaffold (pytest) ===
# Create a file tests/test_pipeline.py with the following content:
"""
import os
import pytest
from fastapi.testclient import TestClient

# Load test env vars or set dummy credentials
os.environ["SUPABASE_URL"] = "http://localhost:8000"
os.environ["SUPABASE_KEY"] = "testkey"
os.environ["PIPELINE_API_KEY"] = "testtoken"

from intelligent_pdf_pipeline import create_app

@pytest.fixture
 def client():
    app = create_app()
    return TestClient(app)

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["ok", "error"]

def test_unauthorized(client):
    response = client.get("/summaries")
    assert response.status_code == 401

def test_bad_query_retrieve(client):
    headers = {"Authorization": "Bearer testtoken"}
    response = client.get("/retrieve?query=hi", headers=headers)
    assert response.status_code == 400
"""
"""
create table campaign_pitches (
  id uuid primary key default gen_random_uuid(),
  concept_id uuid references creative_concepts(id),
  user_id text,
  project_id text,
  pitch text,
  created_at timestamp with time zone default now()
);
"""

# === CORS Middleware ===
from fastapi.middleware.cors import CORSMiddleware

origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Logging & Exception Handling ===
import logging
from fastapi.responses import JSONResponse

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("intelligent_pdf_pipeline")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."}
    )

# === Rate Limiting Stub ===
# For production, integrate a rate-limiter like 'slowapi' or 'redis-rate-limit'.
# Example:
# from slowapi import Limiter
# limiter = Limiter(key_func=get_remote_address)
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

# === OpenAPI Tags ===
# You can tag endpoints for better API docs:
# @app.get("/summaries", tags=["Summaries"])
# async def list_summaries(): ...

# === End of pipeline ===
