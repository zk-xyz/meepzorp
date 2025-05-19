create table if not exists public.agents (
    id uuid primary key,
    name text not null,
    description text,
    endpoint text not null,
    capabilities jsonb not null default '[]'::jsonb,
    metadata jsonb not null default '{}'::jsonb,
    status text not null default 'active',
    registered_at timestamp with time zone not null default now(),
    updated_at timestamp with time zone not null default now()
);

-- Enable RLS
alter table public.agents enable row level security;

-- Create policies
create policy "Agents are viewable by all users"
    on public.agents for select
    using (true);

create policy "Agents are insertable by authenticated users"
    on public.agents for insert
    with check (auth.role() = 'authenticated');

create policy "Agents are updatable by authenticated users"
    on public.agents for update
    using (auth.role() = 'authenticated');

-- Create indexes
create index agents_status_idx on public.agents(status);
create index agents_registered_at_idx on public.agents(registered_at);

-- Create function to automatically update updated_at
create or replace function public.handle_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

-- Create trigger for updated_at
create trigger set_updated_at
    before update on public.agents
    for each row
    execute procedure public.handle_updated_at(); 