-- Apply once in the Supabase SQL editor before enabling cloud progress.
create table if not exists public.scamshield_attempts (
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  lesson integer not null check (lesson between 0 and 3),
  decision boolean not null,
  time_ms bigint not null,
  primary key(user_id,time_ms)
);
alter table public.scamshield_attempts enable row level security;
revoke all on public.scamshield_attempts from anon,authenticated;
grant select,insert on public.scamshield_attempts to authenticated;
drop policy if exists own_read on public.scamshield_attempts;
create policy own_read on public.scamshield_attempts for select to authenticated using(auth.uid()=user_id);
drop policy if exists own_insert on public.scamshield_attempts;
create policy own_insert on public.scamshield_attempts for insert to authenticated with check(auth.uid()=user_id);
