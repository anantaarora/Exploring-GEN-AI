import asyncio
from agents.job_search_agent import search_agent
from agents.planner_agent import resume_match_agent
from agents.export import export_matches_to_csv
from agents.summary_agent import summary_agent, RawJobData
from agents.agents_base import Runner
from sheets_logger import log_job_entry
from typing import List
import pdfplumber

class JobSearchManager:
    def run_sync(self, query, resume_text):
        asyncio.run(self._run_pipeline(query, resume_text))

    async def _run_pipeline(self, search_query: str, resume_text: str):
        print(f"\n🔍 Starting job search for: {search_query}")

        # Step 1: Search jobs using query
        job_listings = await self._search_jobs([search_query])

        # Step 2: Summarize listings
        summaries = await self._summarize_jobs(job_listings)
        print("\n📋 Job Summaries:")
        for job in summaries:
            print(job.markdown_summary)
            print("—" * 40)

        # Step 3: Match resume to jobs
        matches = await self._run_resume_match(resume_text, job_listings)

        # Step 4: Export to CSV
        df = export_matches_to_csv(matches, filename="job_matches.csv")
        print("\n✅ Resume match report saved to job_matches.csv")
        # Step 6: Log to Google Sheets (optional)
        # for match in matches:
        #     log_job_entry(
        #         company=match.company,
        #         title=match.title,
        #         referral_name="",
        #         message="",
        #         response="Pending",
        #         applied="No",
        #         passed="Not Yet"
        #     )
        # Save df for use in Streamlit
        self.final_dataframe = df
    
    async def _search_jobs(self, queries: List[str]) -> List[RawJobData]:
        tasks = [asyncio.create_task(self._run_search(q)) for q in queries]
        results = await asyncio.gather(*tasks)
        jobs = []
        for result in results:
            jobs.extend(result.final_output.listings)
        return jobs

    async def _run_search(self, query: str):
        return await Runner.run(search_agent, query)

    async def _summarize_jobs(self, listings) -> List:
        formatted = [
            RawJobData(
                title=j.title,
                company=j.company,
                location=j.location,
                summary=j.summary,
                link=j.link
            ) for j in listings
        ]

        input_text = "\n\n".join(
            f"Title: {j.title}\nCompany: {j.company}\nLocation: {j.location}\nSummary: {j.summary}\nLink: {j.link}"
            for j in formatted
        )

        result = await Runner.run(summary_agent, input_text)
        return result.final_output.jobs

    async def _run_resume_match(self, resume_text: str, job_descriptions: List[RawJobData]):
        job_block = "\n\n".join([
            f"Title: {j.title}\nCompany: {j.company}\nLocation: {j.location}\nLink: {j.link}\nDescription:\n{j.summary}"
            for j in job_descriptions
        ])
        prompt = f"Resume:\n{resume_text}\n\nJobs:\n{job_block}"

        result = await resume_match_agent.run(prompt)
        return result.final_output.results

    def _extract_resume_text(self, path: str) -> str:
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
