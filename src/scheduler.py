import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from .models import JobSource, JobMatch
from .database import Database
from .scraper import JobScraper
from .discord import DiscordNotifier
from .matcher import JobMatcher
import logging

logger = logging.getLogger(__name__)


class JobScheduler:
    def __init__(self, db: Database, notifier: DiscordNotifier):
        self.db = db
        self.scraper = JobScraper()
        self.matcher = JobMatcher()
        self.notifier = notifier
        self.resume_content: Optional[str] = None

    async def set_resume(self, resume_url: str) -> None:
        """Set or update the resume to match against"""
        self.resume_content = await self.scraper.parse_resume(resume_url)

    async def check_source(self, source: JobSource) -> List[JobMatch]:
        """Check a single source for matching jobs"""
        try:
            # Scrape jobs from source
            jobs = await self.scraper.scrape_job_source(source)

            matches = []
            for job in jobs:
                # Get detailed job description
                job_content = await self.scraper.scrape_job_details(job.url)

                # Check if job matches resume
                match = await self.matcher.evaluate_match(
                    resume=self.resume_content, job_content=job_content, job=job
                )

                if match:
                    matches.append(match)
                    await self.db.save_job_match(match)

            # Update last checked timestamp
            source.last_checked = datetime.utcnow()
            await self.db.save_job_source(source)

            return matches

        except Exception as e:
            logger.error(f"Error checking source {source.url}: {str(e)}")
            return []

    async def run_schedule(self) -> None:
        """Main scheduling loop"""
        while True:
            try:
                sources = await self.db.get_job_sources()

                for source in sources:
                    # Check if source needs to be processed
                    if (
                        not source.last_checked
                        or datetime.utcnow() - source.last_checked
                        > timedelta(minutes=source.frequency)
                    ):

                        matches = await self.check_source(source)

                        if matches:
                            await self.notifier.send_matches(matches)

                # Sleep for a minute before next check
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                await asyncio.sleep(60)  # Sleep and retry on error
