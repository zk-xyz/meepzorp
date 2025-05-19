-- Enable the pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop existing objects if they exist
DROP TABLE IF EXISTS summaries CASCADE;
DROP TABLE IF EXISTS document_chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP FUNCTION IF EXISTS match_documents CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;

-- Documents table
CREATE TABLE if not exists public.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    type TEXT NOT NULL,
    chunks INTEGER NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    project_id UUID,
    workflow_id UUID REFERENCES public.workflows(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Document chunks table with vector embeddings
CREATE TABLE if not exists public.document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    page_num INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, chunk_index)
);

-- Summaries table
CREATE TABLE if not exists public.summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE,
    query TEXT,
    summary TEXT NOT NULL,
    source_chunks INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Enable RLS
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.summaries ENABLE ROW LEVEL SECURITY;

-- Create policies for documents
CREATE POLICY "Documents are viewable by all users"
    ON public.documents FOR SELECT
    USING (true);

CREATE POLICY "Documents are insertable by authenticated users"
    ON public.documents FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Documents are updatable by authenticated users"
    ON public.documents FOR UPDATE
    USING (auth.role() = 'authenticated');

-- Create policies for document chunks
CREATE POLICY "Document chunks are viewable by all users"
    ON public.document_chunks FOR SELECT
    USING (true);

CREATE POLICY "Document chunks are insertable by authenticated users"
    ON public.document_chunks FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Create policies for summaries
CREATE POLICY "Summaries are viewable by all users"
    ON public.summaries FOR SELECT
    USING (true);

CREATE POLICY "Summaries are insertable by authenticated users"
    ON public.summaries FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Create indexes
CREATE INDEX IF NOT EXISTS documents_user_id_idx ON public.documents(user_id);
CREATE INDEX IF NOT EXISTS documents_project_id_idx ON public.documents(project_id);
CREATE INDEX IF NOT EXISTS documents_workflow_id_idx ON public.documents(workflow_id);
CREATE INDEX IF NOT EXISTS documents_created_at_idx ON public.documents(created_at);

CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx ON public.document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Function to match similar documents
CREATE OR REPLACE FUNCTION public.match_documents(
    query_embedding vector(1536),
    match_count int DEFAULT 5,
    min_similarity float DEFAULT 0.7
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    document_id UUID,
    chunk_index INTEGER,
    page_num INTEGER,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.content,
        dc.document_id,
        dc.chunk_index,
        dc.page_num,
        1 - (dc.embedding <=> query_embedding) as similarity
    FROM public.document_chunks dc
    WHERE 1 - (dc.embedding <=> query_embedding) > min_similarity
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER set_documents_updated_at
    BEFORE UPDATE ON public.documents
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at(); 