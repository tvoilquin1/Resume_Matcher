import streamlit as st
from ..models import JobMatch


def render_job_match(match: JobMatch) -> None:
    """Render a single job match in the UI"""
    with st.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader(match.job.title)
            st.caption(f"{match.job.company}")
            if match.job.posted_date:
                st.caption(f"Posted: {match.job.posted_date.strftime('%Y-%m-%d')}")

        with col2:
            st.metric("Match Score", f"{match.match_score * 100:.0f}%")

        st.markdown(f"**Why this matches your profile:**\n{match.match_reason}")
        st.divider()


def render_setup_instructions() -> None:
    """Show initial setup instructions"""
    st.markdown(
        """
    ### 🚀 How it works
    1. Enter your resume URL (PDF format)
    2. Add job board URLs where you want to search
    3. Set how often to check each source (minimum 15 minutes)
    4. Click "Start Matching" to begin
    
    The app will:
    - Immediately scan for matching jobs
    - Continue checking sources at your specified intervals
    - Send new matches to your Discord channel
    - Display matches here in the UI
    
    ### 🔗 Supported Job Boards
    - LinkedIn Jobs
    - Indeed
    - Glassdoor
    - Monster
    - Company career pages
    """
    )
