from firecrawl import FirecrawlApp
from .models import Job, JobListings


class JobScraper:
    def __init__(self):
        self.app = FirecrawlApp()

    async def parse_resume(self, pdf_link: str) -> str:
        """Parse a resume from a PDF link."""
        response = self.app.scrape_url(url=pdf_link)
        return response["markdown"]

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

    async def scrape_job_content(self, job_url: str) -> str:
        """Scrape the content of a specific job posting."""
        response = self.app.scrape_url(url=job_url)
        return response["markdown"]
