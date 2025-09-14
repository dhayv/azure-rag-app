from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    query: str
    top: Optional[int] = 3
    max_tokens: Optional[int] = 300


class QueryResponse(BaseModel):
    answer: str
