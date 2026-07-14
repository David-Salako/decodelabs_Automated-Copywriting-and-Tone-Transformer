"""
Pydantic models that define the strict output shape we force Gemini to return.
Using response_schema with these means we never have to regex-parse the model's
text -- Gemini returns valid JSON matching this structure every time.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class MarketingCopy(BaseModel):
    """Structured marketing copy for a single platform."""

    headline: str = Field(description="A short, attention-grabbing headline or hook.")
    body: str = Field(description="The main marketing copy, respecting platform length rules.")
    call_to_action: str = Field(description="A single, clear call to action.")
    hashtags: Optional[List[str]] = Field(
        default=None, description="Relevant hashtags, only for platforms that use them."
    )


class BatchResult(BaseModel):
    """One row's worth of generated copy, used when running in CSV batch mode."""

    product_name: str
    platform: str
    tone: str
    result: Optional[MarketingCopy] = None
    error: Optional[str] = None