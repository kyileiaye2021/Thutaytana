create extension if not exists vector;
create extension if not exists pg_trgm;

create table if not exists conferences (
  conference_id bigserial primary key,
  name text not null,
  acronym text,
  cfp_url text not null,
  submission_deadline date not null,
  start_date date not null,
  end_date date not null,
  location_city text,
  location_country text,
  region text,
  hybrid_mode text not null check (hybrid_mode in ('in_person','online','hybrid')),
  topics text[] not null default '{}',
  description text not null,
  estimated_cost_usd numeric,
  source text not null default 'manual',
  embedding vector(64),
  created_at timestamptz not null default now()
);

create index if not exists conferences_embedding_idx
  on conferences using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

create index if not exists conferences_topics_gin_idx on conferences using gin (topics);
create index if not exists conferences_name_trgm_idx on conferences using gin (name gin_trgm_ops);
create index if not exists conferences_description_trgm_idx on conferences using gin (description gin_trgm_ops);

create or replace function search_conferences_hybrid(
  query_text text,
  query_embedding vector(64),
  profile_interests text[] default '{}',
  profile_regions text[] default '{}',
  profile_budget numeric default null,
  career_stage text default 'early',
  top_k int default 10
)
returns table (
  conference_id bigint,
  name text,
  acronym text,
  cfp_url text,
  final_score numeric,
  semantic_score numeric,
  symbolic_score numeric,
  profile_score numeric,
  reasons text[]
)
language sql
as $$
with base as (
  select
    c.*,
    coalesce(1 - (c.embedding <=> query_embedding), 0) as semantic_score,
    greatest(similarity(c.name, query_text), similarity(c.description, query_text)) as symbolic_score,
    (
      (case
         when array_length(profile_interests, 1) is null then 0
         else cardinality(array(select unnest(c.topics) intersect select unnest(profile_interests)))::numeric
              / greatest(cardinality(profile_interests), 1)
       end) * 0.5
      + (case when array_length(profile_regions, 1) is null or c.region is null then 0
              when c.region = any(profile_regions) then 0.3 else 0 end)
      + (case when profile_budget is null or c.estimated_cost_usd is null then 0
              when c.estimated_cost_usd <= profile_budget then 0.2 else -0.1 end)
    ) as profile_score,
    array_remove(array[
      case when c.region = any(profile_regions) then 'Region matches preference' end,
      case when c.estimated_cost_usd is not null and profile_budget is not null and c.estimated_cost_usd <= profile_budget
        then 'Within budget' end,
      case when cardinality(array(select unnest(c.topics) intersect select unnest(profile_interests))) > 0
        then 'Aligned topics' end,
      case when career_stage = 'student' and c.hybrid_mode in ('online','hybrid')
        then 'Student-friendly attendance mode' end
    ], null) as reasons
  from conferences c
)
select
  conference_id,
  name,
  acronym,
  cfp_url,
  round((semantic_score * 0.55 + symbolic_score * 0.25 + profile_score * 0.20)::numeric, 6) as final_score,
  round(semantic_score::numeric, 6),
  round(symbolic_score::numeric, 6),
  round(profile_score::numeric, 6),
  reasons
from base
order by final_score desc
limit top_k;
$$;
