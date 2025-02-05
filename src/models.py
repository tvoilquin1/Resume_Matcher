from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Job(BaseModel):
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    posted_date: Optional[datetime] = Field(description="When the job was posted")


class JobSource(BaseModel):
    url: str = Field(description="URL of the job board")
    frequency: int = Field(description="Check frequency in minutes")
    last_checked: Optional[datetime] = Field(description="Last time source was checked")


class JobMatch(BaseModel):
    job: Job
    match_score: float = Field(description="Match confidence score")
    match_reason: str = Field(description="Explanation of why this is a good match")
