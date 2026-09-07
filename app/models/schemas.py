from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any

class AskRequest(BaseModel):
    question: str = Field(..., description="The question to ask the Rulebook QA System.")

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Question cannot be empty or contain only whitespace.")
        return v

class AskResponse(BaseModel):
    status: str = Field(..., description="The status of the response: ANSWERED, NOT_COVERED, or CONFLICT")
    answer: str = Field(..., description="The formulated answer or explanation.")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="List of source chunks used or referenced.")
