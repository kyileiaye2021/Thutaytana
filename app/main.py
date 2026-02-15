import os
from datetime import date
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from supabase import Client, create_client


def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)


app = FastAPI(title="ConferPilotAI Search Engine", version="0.1.0")


class UserProfile(BaseModel):
    interests: list[str] = Field(default_factory=list)
    preferred_regions: list[str] = Field(default_factory=list)
    max_budget_usd: float | None = None
    career_stage: Literal["student", "early", "mid", "senior"] = "early"


class ConferenceCreate(BaseModel):
    name: str
    acronym: str | None = None
    cfp_url: str
    submission_deadline: date
    start_date: date
    end_date: date
    location_city: str | None = None
    location_country: str | None = None
    region: str | None = None
    hybrid_mode: Literal["in_person", "online", "hybrid"] = "in_person"
    topics: list[str] = Field(default_factory=list)
    description: str
    estimated_cost_usd: float | None = None
    source: str = "manual"


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    profile: UserProfile = Field(default_factory=UserProfile)


class RankedConference(BaseModel):
    conference_id: int
    name: str
    acronym: str | None = None
    cfp_url: str
    final_score: float
    semantic_score: float
    symbolic_score: float
    profile_score: float
    reasons: list[str]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/conferences")
def add_conference(payload: ConferenceCreate) -> dict[str, Any]:
    supabase = get_supabase_client()
    response = (
        supabase.table("conferences")
        .insert(payload.model_dump())
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=500, detail="Insert failed")
    return {"conference": response.data[0]}


@app.post("/search", response_model=list[RankedConference])
def search_conferences(request: SearchRequest) -> list[RankedConference]:
    supabase = get_supabase_client()

    # Embedding generation should be replaced with your preferred model endpoint.
    # This deterministic placeholder keeps the service runnable.
    pseudo_embedding = [float((ord(c) % 10) / 10.0) for c in request.query[:64]]
    pseudo_embedding = (pseudo_embedding + [0.0] * 64)[:64]

    result = supabase.rpc(
        "search_conferences_hybrid",
        {
            "query_text": request.query,
            "query_embedding": pseudo_embedding,
            "profile_interests": request.profile.interests,
            "profile_regions": request.profile.preferred_regions,
            "profile_budget": request.profile.max_budget_usd,
            "career_stage": request.profile.career_stage,
            "top_k": request.top_k,
        },
    ).execute()

    if result.data is None:
        raise HTTPException(status_code=500, detail="Search failed")

    return [RankedConference(**row) for row in result.data]
