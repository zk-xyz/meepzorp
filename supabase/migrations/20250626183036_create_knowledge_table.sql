-- +migrate Up
create extension if not exists vector;

create table if not exists public.knowledge (
    id uuid default gen_random_uuid() primary key,
    content text not null,
    tags jsonb not null default '[]'::jsonb,
    embedding vector(1536),
    created_at timestamp with time zone not null default now(),
    updated_at timestamp with time zone not null default now()
);

create index if not exists idx_knowledge_tags on public.knowledge using gin (tags);
create index if not exists idx_knowledge_embedding on public.knowledge using ivfflat (embedding vector_cosine_ops);

alter table public.knowledge enable row level security;

create policy "Enable read access for all users" on public.knowledge
    for select
    using (true);

create policy "Enable insert for authenticated users" on public.knowledge
    for insert
    with check (auth.role() = 'authenticated');

create policy "Enable update for authenticated users" on public.knowledge
    for update
    using (auth.role() = 'authenticated');

create or replace function public.handle_knowledge_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger handle_knowledge_updated_at
    before update on public.knowledge
    for each row
    execute procedure public.handle_knowledge_updated_at();

-- +migrate Down

drop trigger if exists handle_knowledge_updated_at on public.knowledge;
drop function if exists public.handle_knowledge_updated_at;
drop policy if exists "Enable update for authenticated users" on public.knowledge;
drop policy if exists "Enable insert for authenticated users" on public.knowledge;
drop policy if exists "Enable read access for all users" on public.knowledge;
drop table if exists public.knowledge;
