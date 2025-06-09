import asyncio
from agents.planner_agent import resume_match_agent
from agents.job_search_agent import search_agent
from agents.export import export_matches_to_csv
from agents.summary_agent import summary_agent, RawJobData
from agents.referral_agent import generate_referral_messages  # Optional
from agents.agents_base import Runner  # Your utility wrapper
from typing import List
from sheets_logger import log_job_entry # Utility to log job entries in a sheet

class JobSearchManager:
    async def run(self, job_goal: str):
        print(f"🔍 Starting job search for: {job_goal}\n")

        # Step 1: Generate search queries using the planner
        plan = await self._generate_plan(job_goal)

        # Step 2: Search for jobs using those queries
        job_listings = await self._search_jobs(plan)

        # Step 3: Summarize jobs for user readability
        summaries = await self._summarize_jobs(job_listings)

        # Step 4 (Optional): Suggest referrals
        # Uncomment if you want to also generate referrals
        # referrals = await generate_referral_messages("Data Scientist", "Google")

        # Step 5: Display results
        print("\n📋 Job Summaries:\n")
        for job in summaries:
            print(job.markdown_summary)
            print("—" * 40)

        # Optional: Print referral suggestions
        # for r in referrals:
        #     print(f"{r.name} ({r.company}):\n{r.message}\nLink: {r.profile_link}\n")

    async def _search_jobs(self, searches) -> List[RawJobData]:
        tasks = [asyncio.create_task(self._run_search(search.query)) for search in searches]
        results = await asyncio.gather(*tasks)
        jobs = []
        for result in results:
            jobs.extend(result.final_output.listings)
        return jobs
    

    async def check_resume_fit(resume_text: str, job_descriptions: List[dict]):
        job_info_block = "\n\n".join([
            f"Title: {j['title']}\nCompany: {j['company']}\nLocation: {j['location']}\nLink: {j['link']}\nDescription:\n{j['summary']}"
            for j in job_descriptions
        ])

        prompt = f"Resume:\n{resume_text}\n\nJobs:\n{job_info_block}"
        result = await resume_match_agent.run(prompt)
        return result.final_output.results



    async def _run_search(self, query: str):
        return await Runner.run(search_agent, query)
    
    async def run_resume_match(resume_text, job_descriptions):
        job_block = "\n\n".join([
            f"Title: {j['title']}\nCompany: {j['company']}\nLocation: {j['location']}\nLink: {j['link']}\nDescription:\n{j['summary']}"
            for j in job_descriptions
        ])

        prompt = f"Resume:\n{resume_text}\n\nJobs:\n{job_block}"

        result = await resume_match_agent.run(prompt)
        matches = result.final_output.results

        export_matches_to_csv(matches, filename="job_matches.csv")

        return matches
    
    # async def _summarize_jobs(self, listings) -> List:
 

    #     formatted = [
    #         RawJobData(
    #         title=j.title,
    #         company=j.company,
    #         location=j.location,
    #         summary=j.summary,
    #         link=j.link
    #         ) for j in listings
    #     ]

    #     input_text = "\n\n".join(
    #         f"Title: {j.title}\nCompany: {j.company}\nLocation: {j.location}\nSummary: {j.summary}\nLink: {j.link}"
    #         for j in formatted
    #     )

    #     result = await Runner.run(summary_agent, input_text)
    #     summarized_jobs = result.final_output.jobs

    #     # ✅ Add sheet logging
    #     for job, raw in zip(summarized_jobs, formatted):
    #         log_job_entry(
    #             company=raw.company,
    #             title=raw.title,
    #             referral_name="",         # Fill from referral agent if available
    #             message="",               # Can be generated later
    #             response="Pending",       # Default
    #             applied="No",             # User updates
    #             passed="Not Yet"          # To be updated
    #         )

    #     return summarized_jobs


    # async def _summarize_jobs(self, listings) -> List:
    #     formatted = [
    #         RawJobData(
    #             title=j.title,
    #             company=j.company,
    #             location=j.location,
    #             summary=j.summary,
    #             link=j.link
    #         ) for j in listings
    #     ]

    #     input_text = "\n\n".join(
    #         f"Title: {j.title}\nCompany: {j.company}\nLocation: {j.location}\nSummary: {j.summary}\nLink: {j.link}"
    #         for j in formatted
    #     )

    #     result = await Runner.run(summary_agent, input_text)
    #     return result.final_output.jobs
