from pydantic import BaseModel
from typing import List
from agents.agents_base import Agent
import pandas as pd
import openai
from config.settings import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

# Expected format: LinkedIn CSV with at least 'Name', 'Company', 'Profile Link'
CONNECTIONS_CSV = "data/connections.csv"

# Input schema for referral suggestion
class ReferralQuery(BaseModel):
    company_name: str
    job_title: str

# Output schema
class ReferralSuggestion(BaseModel):
    name: str
    company: str
    profile_link: str
    message: str

class ReferralResult(BaseModel):
    referrals: List[ReferralSuggestion]

# Utility: filter potential referrals from uploaded CSV
def find_referrals(company: str) -> List[ReferralSuggestion]:
    df = pd.read_csv(CONNECTIONS_CSV)
    matches = df[df["Company"].str.contains(company, case=False, na=False)]
    
    suggestions = []
    for _, row in matches.iterrows():
        suggestions.append(ReferralSuggestion(
            name=row["Name"],
            company=row["Company"],
            profile_link=row.get("Profile Link", "#"),
            message=""  # To be filled by LLM
        ))
    return suggestions

# Agent that generates custom referral messages
referral_agent = Agent(
    name="ReferralAgent",
    instructions=(
        "You are a networking strategist. Given a job title and company, generate a short and polite LinkedIn message "
        "asking for a referral. Be warm, professional, and to the point."
    ),
    model="gpt-4o",
    output_type=str  # Just returning message
)

# Main runner function
async def generate_referral_messages(job_title: str, company_name: str) -> List[ReferralSuggestion]:
    referrals = find_referrals(company_name)

    for r in referrals:
        prompt = f"Write a LinkedIn referral message for a {job_title} position at {company_name}. Person: {r.name}."
        response = await referral_agent.run(prompt)
        r.message = response.final_output

    return referrals
