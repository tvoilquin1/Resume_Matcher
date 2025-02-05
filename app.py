import streamlit as st
import asyncio
from dotenv import load_dotenv
from src.scraper import JobScraper
from src.matcher import JobMatcher

load_dotenv()


async def main():
    """Main function to run the resume parser application."""
    st.title("Resume Parser and Job Matcher")
    st.markdown(
        """
    This app helps you find matching jobs by:
    - Analyzing your resume from a PDF URL
    - Scraping job postings from provided job board URLs 
    - Using AI to evaluate if you're a good fit for each position
    
    Simply paste your resume URL and job board URLs below to get started!
    """
    )

    scraper = JobScraper()
    matcher = JobMatcher()

    # Resume PDF URL input
    resume_url = st.text_input(
        "**Enter Resume PDF URL**",
        placeholder="https://www.website.com/resume.pdf",
    )

    # Job board URL input
    job_sources = st.text_area(
        "**Enter job board URLs (one per line)**",
        placeholder="https://www.company.com/jobs\nhttps://www.company.com/careers",
    )

    if st.button("Analyze") and resume_url and job_sources:
        with st.spinner("Analyzing..."):
            # Process resume
            resume_content = await scraper.parse_resume(resume_url)

            # Process job postings
            job_sources_list = [
                url.strip() for url in job_sources.split("\n") if url.strip()
            ]
            jobs = await scraper.scrape_job_postings(job_sources_list)

            # Analyze each job posting
            for job in jobs:
                job_content = await scraper.scrape_job_content(job.url)
                result = await matcher.evaluate_match(resume_content, job_content)

                st.subheader(f"Job: {job.title}")
                st.write(f"URL: {job.url}")
                st.write(f"Match: {'✅' if result['is_match'] else '❌'}")
                st.write(f"Reason: {result['reason']}")
                st.divider()


if __name__ == "__main__":
    asyncio.run(main())
