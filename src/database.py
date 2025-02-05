from supabase import create_client, Client
from datetime import datetime
from .config import settings
from .models import JobSource, Job, JobMatch
from typing import List


class Database:
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY
        )

    async def save_job_source(self, source: JobSource) -> None:
        """Save or update a job source"""
        await self.client.table("job_sources").upsert(
            {
                "url": source.url,
                "frequency": source.frequency,
                "last_checked": (
                    source.last_checked.isoformat() if source.last_checked else None
                ),
            }
        ).execute()

    async def get_job_sources(self) -> List[JobSource]:
        """Get all job sources that need checking"""
        response = await self.client.table("job_sources").select("*").execute()
        return [JobSource(**source) for source in response.data]

    async def save_job_match(self, match: JobMatch) -> None:
        """Save a new job match"""
        await self.client.table("job_matches").insert(
            {
                "job_title": match.job.title,
                "company": match.job.company,
                "match_score": match.match_score,
                "match_reason": match.match_reason,
                "created_at": datetime.utcnow().isoformat(),
            }
        ).execute()

    async def get_recent_matches(self) -> List[JobMatch]:
        """Get recent job matches"""
        response = (
            await self.client.table("job_matches")
            .select("*")
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )
        return [JobMatch(**match) for match in response.data]
