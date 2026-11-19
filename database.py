"""Database access layer for the Job Application Tracker.

Every SQL statement in the project lives in this module and uses
parameterized queries. JSON columns are serialized with json.dumps on
write and decoded with json.loads on read.
"""
import json
import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Open a new MySQL connection using settings from the environment."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "job_tracker"),
    )


def query_all(sql, params=()):
    """Run a SELECT and return all rows as a list of dicts."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        conn.close()


def query_one(sql, params=()):
    """Run a SELECT and return the first row as a dict, or None."""
    rows = query_all(sql, params)
    return rows[0] if rows else None


def execute(sql, params=()):
    """Run an INSERT/UPDATE/DELETE, commit, and return (lastrowid, rowcount)."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.lastrowid, cur.rowcount
    finally:
        conn.close()


def decode_json(value, default=None):
    """Decode a JSON column value that may arrive as str, bytes, or None."""
    if value is None:
        return default
    if isinstance(value, (bytes, bytearray)):
        value = value.decode("utf-8")
    if isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError:
            return default
    return value


def encode_json(value):
    """Serialize a Python value for a JSON column (None stays NULL)."""
    return None if value is None else json.dumps(value)


# ---------------------------------------------------------------- companies

def get_companies():
    return query_all(
        """SELECT c.*,
                  (SELECT COUNT(*) FROM jobs j WHERE j.company_id = c.company_id) AS job_count,
                  (SELECT COUNT(*) FROM contacts t WHERE t.company_id = c.company_id) AS contact_count
           FROM companies c ORDER BY c.company_name"""
    )


def get_company(company_id):
    return query_one("SELECT * FROM companies WHERE company_id = %s", (company_id,))


def company_choices():
    """Minimal company list for dropdowns."""
    return query_all("SELECT company_id, company_name FROM companies ORDER BY company_name")


def create_company(data):
    new_id, _ = execute(
        """INSERT INTO companies (company_name, industry, website, city, state, notes)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (data["company_name"], data["industry"], data["website"],
         data["city"], data["state"], data["notes"]),
    )
    return new_id


def update_company(company_id, data):
    execute(
        """UPDATE companies SET company_name = %s, industry = %s, website = %s,
                  city = %s, state = %s, notes = %s
           WHERE company_id = %s""",
        (data["company_name"], data["industry"], data["website"],
         data["city"], data["state"], data["notes"], company_id),
    )


def delete_company(company_id):
    """Delete a company; jobs, applications and contacts cascade."""
    _, count = execute("DELETE FROM companies WHERE company_id = %s", (company_id,))
    return count > 0


# --------------------------------------------------------------------- jobs

def _decode_job(row):
    row["requirements"] = decode_json(row.get("requirements"), [])
    return row


def get_jobs():
    rows = query_all(
        """SELECT j.*, c.company_name,
                  (SELECT COUNT(*) FROM applications a WHERE a.job_id = j.job_id) AS application_count
           FROM jobs j JOIN companies c ON c.company_id = j.company_id
           ORDER BY j.date_posted DESC, j.job_id DESC"""
    )
    return [_decode_job(r) for r in rows]


def get_jobs_for_company(company_id):
    rows = query_all(
        "SELECT * FROM jobs WHERE company_id = %s ORDER BY date_posted DESC, job_id DESC",
        (company_id,),
    )
    return [_decode_job(r) for r in rows]


def get_job(job_id):
    row = query_one(
        """SELECT j.*, c.company_name
           FROM jobs j JOIN companies c ON c.company_id = j.company_id
           WHERE j.job_id = %s""",
        (job_id,),
    )
    return _decode_job(row) if row else None


def job_choices():
    """Job list for dropdowns, labelled with the company name."""
    return query_all(
        """SELECT j.job_id, j.job_title, c.company_name
           FROM jobs j JOIN companies c ON c.company_id = j.company_id
           ORDER BY c.company_name, j.job_title"""
    )


def create_job(data):
    new_id, _ = execute(
        """INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
                             job_url, date_posted, requirements)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (data["company_id"], data["job_title"], data["job_type"], data["salary_min"],
         data["salary_max"], data["job_url"], data["date_posted"],
         encode_json(data["requirements"])),
    )
    return new_id


def update_job(job_id, data):
    execute(
        """UPDATE jobs SET company_id = %s, job_title = %s, job_type = %s, salary_min = %s,
                  salary_max = %s, job_url = %s, date_posted = %s, requirements = %s
           WHERE job_id = %s""",
        (data["company_id"], data["job_title"], data["job_type"], data["salary_min"],
         data["salary_max"], data["job_url"], data["date_posted"],
         encode_json(data["requirements"]), job_id),
    )


def delete_job(job_id):
    """Delete a job; its applications cascade."""
    _, count = execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))
    return count > 0
