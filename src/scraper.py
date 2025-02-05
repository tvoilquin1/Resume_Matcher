from firecrawl import FirecrawlApp
from typing import List, Optional
from datetime import datetime
from .models import Job, JobSource, JobMatch
from .config import settings
import asyncio
import logging

logger = logging.getLogger(__name__)


class JobScraper:
    def __init__(self):
        self.app = FirecrawlApp()

    async def parse_resume(self, pdf_url: str) -> Optional[str]:
        """Parse resume from PDF URL"""
        try:
            response = self.app.scrape_url(
                url=pdf_url, params={"formats": ["markdown"]}
            )
            return response["markdown"]
        except Exception as e:
            logger.error(f"Failed to parse resume: {str(e)}")
            raise ValueError(
                "Could not parse resume. Please check if the URL is accessible and is a PDF file."
            )

    async def scrape_job_source(self, source: JobSource) -> List[Job]:
        """Scrape jobs from a single source"""
        try:
            response = self.app.scrape_url(
                url=source.url,
                params={
                    "formats": ["extract"],
                    "extract": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "jobs": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "title": {
                                                "type": "string",
                                                "description": "Job title",
                                            },
                                            "company": {
                                                "type": "string",
                                                "description": "Company name",
                                            },
                                            "posted_date": {
                                                "type": "string",
                                                "description": "When the job was posted",
                                            },
                                        },
                                        "required": ["title", "company"],
                                    },
                                }
                            },
                        },
                        "prompt": "Extract job listings from the page",
                    },
                },
            )

            jobs = []
            for job_data in response["extract"]["jobs"]:
                # Convert posted_date string to datetime if present
                if "posted_date" in job_data:
                    try:
                        job_data["posted_date"] = datetime.fromisoformat(
                            job_data["posted_date"]
                        )
                    except (ValueError, TypeError):
                        job_data["posted_date"] = None

                jobs.append(Job(**job_data))

            logger.info(f"Scraped {len(jobs)} jobs from {source.url}")
            return jobs

        except Exception as e:
            logger.error(f"Failed to scrape jobs from {source.url}: {str(e)}")
            raise ValueError(
                f"Could not scrape jobs from {source.url}. Please verify the URL is accessible."
            )

    async def scrape_job_details(self, job_url: str) -> str:
        """Scrape detailed job description"""
        try:
            response = self.app.scrape_url(
                url=job_url, params={"formats": ["markdown"]}
            )
            return response["markdown"]
        except Exception as e:
            logger.error(f"Failed to scrape job details from {job_url}: {str(e)}")
            return "Job description unavailable"
