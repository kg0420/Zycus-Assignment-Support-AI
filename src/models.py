from typing import List, Optional
from pydantic import BaseModel, Field


ALLOWED_CATEGORIES = [
    "Feature Request",
    "How-To",
    "Performance",
    "Billing",
    "Integration",
    "Onboarding",
    "Data Loss",
]


class KBReference(BaseModel):
    source: str
    section: Optional[str] = None
    relevance: float = Field(ge=0.0, le=1.0)


class TriageResult(BaseModel):
    product_area: str

    category: str = Field(
        description=(
            "Must be one of: Feature Request, How-To, Performance, "
            "Billing, Integration, Onboarding, Data Loss"
        )
    )

    urgency: str = Field(
        pattern=r"^P[1-4]$"
    )

    reasoning: str

    known_issue: bool

    knowledge_base_docs: List[KBReference] = []

    recommended_team: str

    first_response: str     