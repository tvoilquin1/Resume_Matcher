import streamlit as st
import asyncio
from typing import Optional
from .config import settings
from .database import Database
from .discord import DiscordNotifier
from .scheduler import JobScheduler
from .models import JobSource
from .ui.components import render_job_match, render_setup_instructions
import logging

logger = logging.getLogger(__name__)


async def main():
    st.set_page_config(page_title="AI Job Matcher", page_icon="🎯", layout="wide")

    st.title("🎯 AI Job Matcher")

    # Initialize components
    db = Database()
    notifier = DiscordNotifier(st.secrets["DISCORD_WEBHOOK_URL"])
    scheduler = JobScheduler(db, notifier)

    # Session state for tracking setup status
    if "setup_complete" not in st.session_state:
        st.session_state.setup_complete = False

    if not st.session_state.setup_complete:
        render_setup_instructions()

        with st.form("setup_form"):
            resume_url = st.text_input(
                "Resume URL (PDF)", placeholder="https://example.com/resume.pdf"
            )

            job_sources = st.text_area(
                "Job Board URLs (one per line)",
                placeholder="https://jobs.example.com\nhttps://careers.company.com",
            )

            frequency = st.slider(
                "Check frequency (minutes)",
                min_value=settings.MIN_CHECK_FREQUENCY,
                max_value=120,
                value=30,
                step=15,
            )

            if st.form_submit_button("Start Matching"):
                try:
                    # Validate and parse resume
                    await scheduler.set_resume(resume_url)

                    # Save job sources
                    sources = []
                    for url in job_sources.strip().split("\n"):
                        if url:
                            source = JobSource(url=url.strip(), frequency=frequency)
                            await db.save_job_source(source)
                            sources.append(source)

                    if not sources:
                        st.error("Please add at least one job source URL")
                        return

                    st.session_state.setup_complete = True
                    st.success("Setup complete! Starting initial job search...")
                    st.rerun()

                except Exception as e:
                    st.error(f"Setup failed: {str(e)}")
                    logger.error(f"Setup error: {str(e)}")

    else:
        # Show matches
        matches = await db.get_recent_matches()

        if not matches:
            st.info(
                "Searching for matching jobs... Check back soon or wait for Discord notifications!"
            )

        for match in matches:
            render_job_match(match)


if __name__ == "__main__":
    asyncio.run(main())
