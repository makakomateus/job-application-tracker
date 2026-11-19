"""Job matching logic. Pure functions, no database or Flask needed."""


def parse_skills(text):
    """Split comma-separated text into a list of trimmed, non-empty skills."""
    return [part.strip() for part in (text or "").split(",") if part.strip()]


def normalize(skill):
    return skill.strip().lower()


def match_job(user_skills, requirements):
    """Compare a user's skills with one job's requirements.

    Matching ignores case and surrounding spaces. Returns a dict with the
    matched and missing requirements (in the job's own spelling), the
    counts, and the percentage rounded to a whole number. The percentage
    is None when the job lists no requirements.
    """
    have = {normalize(s) for s in user_skills}
    requirements = [r for r in (requirements or []) if isinstance(r, str) and r.strip()]
    matched = [r for r in requirements if normalize(r) in have]
    missing = [r for r in requirements if normalize(r) not in have]
    total = len(requirements)
    percent = round(len(matched) * 100 / total) if total else None
    return {
        "matched": matched,
        "missing": missing,
        "matched_count": len(matched),
        "total": total,
        "percent": percent,
    }


def rank_jobs(user_skills, jobs):
    """Score every job and sort best match first.

    Each job is a dict with at least job_title and requirements. Jobs with no
    requirements go to the bottom of the list.
    """
    results = []
    for job in jobs:
        result = match_job(user_skills, job.get("requirements"))
        result["job"] = job
        results.append(result)
    results.sort(key=lambda r: (
        r["percent"] is None,
        -(r["percent"] or 0),
        -r["matched_count"],
        r["job"]["job_title"].lower(),
    ))
    return results
