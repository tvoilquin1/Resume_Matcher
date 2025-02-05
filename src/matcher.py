from langchain_anthropic import ChatAnthropic
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import ChatPromptTemplate
from typing import Optional
from .models import Job, JobMatch
from .config import settings


class JobMatcher:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-opus-20240229",
            temperature=0,
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
        )

        self.response_schemas = [
            ResponseSchema(
                name="match_score",
                description="Match confidence score between 0 and 1",
            ),
            ResponseSchema(
                name="match_reason",
                description="Brief explanation of why the candidate is or isn't a good fit",
            ),
        ]

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert job recruiter. Analyze the resume and job posting to determine if the candidate is a good fit.
                Consider that candidates might be good fits even without meeting all requirements. Focus on key skills and experience.""",
                ),
                (
                    "human",
                    """
                Resume:
                {resume}
                
                Job Posting:
                {job_content}
                
                Determine if this candidate is a good fit and explain why briefly.
                {format_instructions}
                """,
                ),
            ]
        )

        self.output_parser = StructuredOutputParser.from_response_schemas(
            self.response_schemas
        )

    async def evaluate_match(
        self, resume: str, job_content: str, job: Job
    ) -> Optional[JobMatch]:
        """Evaluate if a job is a good match for the resume"""

        formatted_prompt = self.prompt.format(
            resume=resume,
            job_content=job_content,
            format_instructions=self.output_parser.get_format_instructions(),
        )

        response = await self.llm.ainvoke(formatted_prompt)
        result = self.output_parser.parse(response.content)

        # Only return matches above 0.7 confidence
        if float(result["match_score"]) >= 0.7:
            return JobMatch(
                job=job,
                match_score=float(result["match_score"]),
                match_reason=result["match_reason"],
            )
        return None
