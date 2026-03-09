"""
Response schemas for API endpoints.
"""
from pydantic import BaseModel, Field


class AnswerResponse(BaseModel):
    """Response model for question answers."""
    answer: str = Field(..., description="The AI-generated answer")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Based on the provided materials, here are some helpful strategies..."
            }
        }

