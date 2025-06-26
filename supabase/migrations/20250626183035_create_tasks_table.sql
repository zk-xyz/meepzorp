-- +migrate Up
create table if not exists public.tasks (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    description text,
    status text not null default 'todo',
    priority text not null default 'medium',
    due_date timestamp with time zone,
    assignee text,
    project_id uuid,
    tags jsonb not null default '[]'::jsonb,
    created_at timestamp with time zone not null default now(),
    updated_at timestamp with time zone not null default now(),
    created_by uuid references auth.users(id),
    updated_by uuid references auth.users(id)
);

alter table public.tasks enable row level security;

create policy "Tasks are viewable by all users"
    on public.tasks for select
    using (true);

create policy "Tasks are insertable by authenticated users"
    on public.tasks for insert
    with check (auth.role() = 'authenticated');

create policy "Tasks are updatable by authenticated users"
    on public.tasks for update
    using (auth.role() = 'authenticated');

create index tasks_status_idx on public.tasks(status);
create index tasks_priority_idx on public.tasks(priority);
create index tasks_project_id_idx on public.tasks(project_id);
create index tasks_assignee_idx on public.tasks(assignee);
create index tasks_created_at_idx on public.tasks(created_at);

create or replace function public.handle_task_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger set_task_updated_at
    before update on public.tasks
    for each row
    execute procedure public.handle_task_updated_at();

-- +migrate Down

drop trigger if exists set_task_updated_at on public.tasks;
drop function if exists public.handle_task_updated_at;
drop policy if exists "Tasks are updatable by authenticated users" on public.tasks;
drop policy if exists "Tasks are insertable by authenticated users" on public.tasks;
drop policy if exists "Tasks are viewable by all users" on public.tasks;
drop table if exists public.tasks;
