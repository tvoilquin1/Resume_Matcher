from pydantic import BaseModel, Field
from typing import List


class Job(BaseModel):
    title: str = Field(description="Job title")
    url: str = Field(description="URL of the job posting")


class JobListings(BaseModel):
    jobs: List[Job] = Field(description="List of job postings")
