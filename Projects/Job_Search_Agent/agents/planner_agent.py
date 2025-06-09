from pydantic import BaseModel
from typing import List
import openai
from config.settings import OPENAI_API_KEY
from agents.agents_base import Agent

openai.api_key = OPENAI_API_KEY

# Define schema for job matching and skill gap analysis
class JobFitItem(BaseModel):
    title: str
    company: str
    location: str
    match_score: float
    match_status: str
    missing_skills: List[str]
    recommended_resources: List[str]
    link: str

class ResumeMatchPlan(BaseModel):
    results: List[JobFitItem]

resume_match_agent = Agent(
    name="ResumeMatchAgent",
    instructions=(
        "You are an AI resume evaluator and job match advisor. Given a resume in plain text and a list of job descriptions "
        "with metadata (title, company, location, description, and link), analyze how well the resume matches each job. "
        "Provide a match score (0.0 to 1.0), match status ('Good Fit', 'Partial Fit', 'Not a Fit'), and list of missing skills. "
        "Then, for any missing skills, suggest up to 3 relevant learning resources such as YouTube videos, Medium/TDS articles, or courses.\n\n"
        "Return your answer in the following JSON schema:\n"
        "`{ results: [ { title: str, company: str, location: str, match_score: float, match_status: str, missing_skills: list[str], recommended_resources: list[str], link: str } ] }`"
    ),
    model="gpt-4o",
    output_type=ResumeMatchPlan,
)
