from firecrawl import FirecrawlApp
from .models import Job, JobListings
import streamlit as st
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
import requests
import logging
import re


@st.cache_data(show_spinner=False)
def _cached_parse_resume(pdf_link: str) -> str:
    """Cached version of resume parsing"""
    app = FirecrawlApp()
    response = app.scrape_url(url=pdf_link)
    return response["markdown"]


class JobScraper:
    def __init__(self):
        self.app = FirecrawlApp()

    async def parse_resume(self, pdf_link: str) -> str:
        """Parse a resume from a PDF link."""
        return _cached_parse_resume(pdf_link)

    async def scrape_job_postings(self, source_urls: list[str]) -> list[Job]:
        """Scrape job postings from source URLs."""
        response = self.app.batch_scrape_urls(
            urls=source_urls,
            params={
                "formats": ["extract"],
                "extract": {
                    "schema": JobListings.model_json_schema(),
                    "prompt": "Extract information based on the schema provided",
                },
            },
        )

        jobs = []
        for job in response["data"]:
            jobs.extend(job["extract"]["jobs"])

        return [Job(**job) for job in jobs]

    def _get_retry_time(self, error: requests.exceptions.HTTPError) -> int:
        """Extract retry time from rate limit error message."""
        if error.response is not None and error.response.status_code == 429:
            # Try to extract retry time from error message
            match = re.search(r'please retry after (\d+)s', str(error))
            if match:
                return int(match.group(1))
        return 30  # Default to 30s if we can't parse the wait time

    @retry(
        retry=retry_if_exception_type(requests.exceptions.HTTPError),
        wait=wait_exponential(multiplier=1, min=30, max=60),
        stop=stop_after_attempt(3),
        before_sleep=before_sleep_log(logging.getLogger(), logging.INFO)
    )
    async def scrape_job_content(self, job_url: str) -> str:
        """Scrape the content of a specific job posting.
        
        Retries up to 3 times with exponential backoff on rate limit errors.
        Initial wait is 30s, then 45s, then 60s (max).
        """
        try:
            response = self.app.scrape_url(url=job_url)
            return response["markdown"]
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                # Get retry time from error message
                wait_time = self._get_retry_time(e)
                # Update exponential wait parameters
                self.scrape_job_content.retry.wait = wait_exponential(
                    multiplier=1, 
                    min=wait_time,
                    max=max(wait_time * 2, 60)
                )
                # Re-raise to trigger retry
                raise
            # Re-raise other HTTP errors without retry
            raise
