-- Create workflows table
create table if not exists public.workflows (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    description text,
    steps jsonb not null default '[]'::jsonb,
    variables jsonb not null default '{}'::jsonb,
    created_at timestamp with time zone not null default now(),
    updated_at timestamp with time zone not null default now(),
    created_by uuid references auth.users(id),
    version integer not null default 1,
    status text not null default 'active'
);

-- Create workflow_executions table
create table if not exists public.workflow_executions (
    id uuid primary key default gen_random_uuid(),
    workflow_id uuid references public.workflows(id),
    status text not null default 'pending',
    input_variables jsonb not null default '{}'::jsonb,
    step_results jsonb not null default '{}'::jsonb,
    output jsonb,
    started_at timestamp with time zone not null default now(),
    completed_at timestamp with time zone,
    error text,
    created_by uuid references auth.users(id)
);

-- Enable RLS
alter table public.workflows enable row level security;
alter table public.workflow_executions enable row level security;

-- Create policies for workflows
create policy "Workflows are viewable by all users"
    on public.workflows for select
    using (true);

create policy "Workflows are insertable by authenticated users"
    on public.workflows for insert
    with check (auth.role() = 'authenticated');

create policy "Workflows are updatable by authenticated users"
    on public.workflows for update
    using (auth.role() = 'authenticated');

-- Create policies for workflow executions
create policy "Workflow executions are viewable by all users"
    on public.workflow_executions for select
    using (true);

create policy "Workflow executions are insertable by authenticated users"
    on public.workflow_executions for insert
    with check (auth.role() = 'authenticated');

create policy "Workflow executions are updatable by authenticated users"
    on public.workflow_executions for update
    using (auth.role() = 'authenticated');

-- Create indexes
create index workflows_status_idx on public.workflows(status);
create index workflows_created_at_idx on public.workflows(created_at);
create index workflow_executions_status_idx on public.workflow_executions(status);
create index workflow_executions_started_at_idx on public.workflow_executions(started_at);
create index workflow_executions_workflow_id_idx on public.workflow_executions(workflow_id);

-- Create function to automatically update updated_at
create or replace function public.handle_workflow_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

-- Create trigger for updated_at
create trigger set_workflow_updated_at
    before update on public.workflows
    for each row
    execute procedure public.handle_workflow_updated_at(); 