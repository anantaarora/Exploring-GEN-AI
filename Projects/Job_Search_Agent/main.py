import asyncio
import streamlit as st
import tempfile
import fitz  # PyMuPDF
import asyncio
from manager_up import JobSearchManager

# ✅ Helper to extract text from uploaded PDF resume
def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

# ✅ Streamlit UI
st.title("💼 Multi-Agent AI Job Matcher")

search_query = st.text_input("🔎 Enter your job search query:")
resume_file = st.file_uploader("📄 Upload your Resume (PDF only)", type=["pdf"])

if st.button("🚀 Match Jobs"):
    if not search_query or not resume_file:
        st.warning("Please provide both job query and resume.")
    else:
        with st.spinner("🔍 Matching jobs and analyzing resume..."):
            # Save uploaded resume temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(resume_file.read())
                resume_path = tmp.name

            # Extract resume content
            resume_text = extract_text_from_pdf(resume_path)

            # Run job matching
            manager = JobSearchManager()
            manager.run_sync(search_query, resume_text)

            st.success("✅ Matching complete! Download your job matches below:")
            with open("job_matches.csv", "rb") as f:
                st.download_button(
                    label="📥 Download CSV",
                    data=f,
                    file_name="job_matches.csv",
                    mime="text/csv"
                )
            # ✅ Show DataFrame in Streamlit
            st.subheader("📊 Matched Jobs Overview")
            st.dataframe(manager.final_dataframe)
