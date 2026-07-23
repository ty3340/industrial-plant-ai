"""Pydantic schemas shared by the API layer and the agents."""
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    """A natural-language question about the plant."""
    question: str = Field(..., min_length=1,
                          description="e.g. 'Can we produce 3 batches of Product A?'")


class QueryResponse(BaseModel):
    """The orchestrator's answer."""
    answer: str


