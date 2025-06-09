from pydantic import BaseModel
from typing import List
from agents.agents_base import Agent
import openai
from config.settings import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

# Define the structure of a job listing (from search agent)
class RawJobData(BaseModel):
    title: str
    company: str
    location: str
    summary: str
    link: str

# Output structure from summary agent
class SummarizedJob(BaseModel):
    markdown_summary: str  # well-formatted job summary

class SummarizedJobs(BaseModel):
    jobs: List[SummarizedJob]

# Define the Summary Agent
summary_agent = Agent(
    name="SummaryAgent",
    instructions=(
        "You are a job summary bot. Given raw job listings, return a JSON object with this format ONLY:\n"
        "{\n"
        '  "jobs": [\n'
        "    {\n"
        '      "markdown_summary": "string"\n'
        "    }, ...\n"
        "  ]\n"
        "}\n"
        "Each summary should be a markdown string that includes job title, company, location, and a 2–3 sentence description. "
        "Do not include any explanations, markdown, or code blocks. Return only valid JSON."
    ),
    model="gpt-4o",
    output_type=SummarizedJobs,
)
