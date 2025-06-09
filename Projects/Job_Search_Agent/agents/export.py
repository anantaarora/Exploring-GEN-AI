import pandas as pd

def export_matches_to_csv(matches, filename="job_match_report.csv"):
    rows = []
    for match in matches:
        rows.append({
            "Job Title": match.title,
            "Company": match.company,
            "Location": match.location,
            "Match Score": match.match_score,
            "Match Status": match.match_status,
            "Missing Skills": ", ".join(match.missing_skills),
            "Resources": " | ".join(match.recommended_resources),
            "Job Link": match.link
        })

    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    print(f"✅ Exported job match results to {filename}")
    return df