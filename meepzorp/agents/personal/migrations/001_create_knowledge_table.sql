-- Enable the pgvector extension to support vector operations
create extension if not exists vector;

-- Create knowledge table
create table if not exists public.knowledge (
    id uuid default gen_random_uuid() primary key,
    content text not null,
    tags jsonb not null default '[]',
    embedding vector(1536),
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create indexes
create index if not exists idx_knowledge_tags on public.knowledge using gin (tags);
create index if not exists idx_knowledge_embedding on public.knowledge using ivfflat (embedding vector_cosine_ops);

-- Enable Row Level Security
alter table public.knowledge enable row level security;

-- Create policies
create policy "Enable read access for all users" on public.knowledge
    for select
    to authenticated
    using (true);

create policy "Enable insert for authenticated users" on public.knowledge
    for insert
    to authenticated
    with check (true);

create policy "Enable update for authenticated users" on public.knowledge
    for update
    to authenticated
    using (true)
    with check (true);

-- Create function to update updated_at timestamp
create or replace function public.handle_updated_at()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    new.updated_at = timezone('utc'::text, now());
    return new;
end;
$$;

-- Create trigger for updated_at
create trigger handle_knowledge_updated_at
    before update on public.knowledge
    for each row
    execute function public.handle_updated_at(); 