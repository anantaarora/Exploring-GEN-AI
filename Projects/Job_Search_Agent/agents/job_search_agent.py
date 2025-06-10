import requests
from pydantic import BaseModel
from typing import List
from agents.agents_base import Agent
from config.settings import SERP_API_KEY  # Store your SerpAPI key in config
import openai
from config.settings import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

# Define job listing format
class JobListing(BaseModel):
    title: str
    company: str
    location: str
    link: str
    summary: str

class JobSearchResult(BaseModel):
    listings: List[JobListing]

# Web search tool using SerpAPI
class SerpSearchTool:
    def search_jobs(self, query: str) -> List[JobListing]:
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_jobs",
            "q": f"{query} site:linkedin.com/jobs",
            "api_key": SERP_API_KEY,
            "hl": "en",
            "gl": "in",  # Change to your preferred location to india
            "num": 10  # Limit to 10 results
        }

        response = requests.get(url, params=params)
        results = response.json()
        jobs = []

        for item in results.get("jobs_results", [])[:10]:
            jobs.append(JobListing(
                title=item.get("title", "No title"),
                company=item.get("company_name", "Unknown"),
                location=item.get("location", "N/A"),
                link=item.get("via", "N/A"),
                summary=item.get("description", "")[:300]
            ))

        return jobs

# The actual agent definition
search_agent = Agent(
    name="JobSearchAgent",
    instructions=(
       "You are a job discovery bot. Given a  Data Scientist/ Senior Data Scientist job-related search query, return a JSON object with up to 10 job listings from Linkedin , Hirist, or Naukri which are latest and most recent "
        "Each job listing must have the following fields: title, company, location, link, summary. "
        "Return the result in this exact format:\n"
        "{\n"
        '  "listings": [\n'
        "    {\n"
        '      "title": "string",\n'
        '      "company": "string",\n'
        '      "location": "string",\n'
        '      "link": "string",\n'
        '      "summary": "string"\n'
        "    }, ...\n"
        "  ]\n"
        "}\n"
        "Do not include any other fields. Do not wrap the JSON in markdown or code blocks."
    ),
    # tools=[SerpSearchTool()],
    model="gpt-4o",
    output_type=JobSearchResult
)