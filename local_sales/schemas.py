from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class BusinessProfile(StrictModel):
    summary: str = Field(min_length=10, max_length=1500)
    sells: list[str] = Field(min_length=1, max_length=8)
    customers: list[str] = Field(min_length=1, max_length=8)
    value_propositions: list[str] = Field(min_length=1, max_length=8)

class ICP(StrictModel):
    summary: str = Field(min_length=10, max_length=1500)
    industries: list[str] = Field(min_length=1, max_length=8)
    company_sizes: list[str] = Field(min_length=1, max_length=6)
    decision_makers: list[str] = Field(min_length=1, max_length=8)
    pain_points: list[str] = Field(min_length=1, max_length=8)
    disqualifiers: list[str] = Field(max_length=8)

class Research(StrictModel):
    summary: str = Field(min_length=10, max_length=1800)
    icp_match_reason: str = Field(min_length=5, max_length=1000)
    evidence: list[str] = Field(min_length=1, max_length=6)

class Signal(StrictModel):
    type: Literal["hiring", "funding", "expansion", "tech_change", "operational_pain", "none"]
    confidence: float = Field(ge=0, le=1)
    evidence: str = Field(min_length=3, max_length=800)

class Signals(StrictModel):
    signals: list[Signal] = Field(min_length=1, max_length=4)

class Problem(StrictModel):
    statement: str = Field(min_length=10, max_length=900)
    supporting_evidence: str = Field(min_length=5, max_length=900)

class Score(StrictModel):
    score: int = Field(ge=0, le=100)
    reason: str = Field(min_length=10, max_length=1200)
    priority: Literal["high", "medium", "low"]

class Email(StrictModel):
    subject: str = Field(min_length=3, max_length=160)
    body: str = Field(min_length=20, max_length=3000)

class ReplyClassification(StrictModel):
    category: Literal["Interested", "Not interested", "Later", "Unsubscribe", "Other"]
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(min_length=5, max_length=900)

SCHEMAS = {"business_profile":BusinessProfile,"icp":ICP,"research":Research,"signals":Signals,"problem":Problem,"scoring":Score,"email":Email,"reply":ReplyClassification}

class ProductInput(StrictModel):
    name: str = Field(min_length=2, max_length=120)
    company_name: str = Field(min_length=2, max_length=160)
    company_info: str = Field(min_length=10, max_length=6000)
    description: str = Field(min_length=10, max_length=6000)
    target_market: str = Field(min_length=3, max_length=2000)
    value_proposition: str = Field(min_length=3, max_length=2000)
    color: Literal["green", "blue", "violet", "orange"] = "green"

class ProspectInput(StrictModel):
    company: str = Field(min_length=2, max_length=160)
    contact_name: str = Field(min_length=2, max_length=120)
    title: str = Field(min_length=2, max_length=160)
    industry: str = Field(min_length=2, max_length=120)
    employees: int = Field(ge=1, le=10000000)
    location: str = Field(min_length=2, max_length=160)
    notes: str = Field(min_length=10, max_length=8000)

class ReplyInput(StrictModel):
    prospect_id: int
    thread: str = Field(min_length=5, max_length=8000)

class RunInput(StrictModel):
    workflow: Literal["pipeline", "business_profile", "icp", "research", "signals", "problem", "scoring", "email", "reply"]
    prospect_ids: list[int] | None = Field(default=None, max_length=200)
    reply_ids: list[int] | None = Field(default=None, max_length=200)

class ModelInput(StrictModel):
    model: Literal["qwen3:0.6b", "qwen3:1.7b", "qwen3:4b", "qwen3:8b"]
