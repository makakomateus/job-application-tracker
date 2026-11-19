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


# ------------------------------------------------------------- applications

APPLICATION_SELECT = """SELECT a.*, j.job_title, j.company_id, c.company_name
    FROM applications a
    JOIN jobs j ON j.job_id = a.job_id
    JOIN companies c ON c.company_id = j.company_id"""


def _decode_application(row):
    row["interview_data"] = decode_json(row.get("interview_data"), None)
    return row


def get_applications(status=None):
    """All applications, newest first, optionally filtered by status."""
    if status:
        rows = query_all(
            APPLICATION_SELECT + " WHERE a.status = %s ORDER BY a.application_date DESC, a.application_id DESC",
            (status,),
        )
    else:
        rows = query_all(APPLICATION_SELECT + " ORDER BY a.application_date DESC, a.application_id DESC")
    return [_decode_application(r) for r in rows]


def get_application(application_id):
    row = query_one(APPLICATION_SELECT + " WHERE a.application_id = %s", (application_id,))
    return _decode_application(row) if row else None


def create_application(data):
    new_id, _ = execute(
        """INSERT INTO applications (job_id, application_date, status, resume_version,
                                     cover_letter_sent, interview_data)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (data["job_id"], data["application_date"], data["status"], data["resume_version"],
         data["cover_letter_sent"], encode_json(data["interview_data"])),
    )
    return new_id


def update_application(application_id, data):
    execute(
        """UPDATE applications SET job_id = %s, application_date = %s, status = %s,
                  resume_version = %s, cover_letter_sent = %s, interview_data = %s
           WHERE application_id = %s""",
        (data["job_id"], data["application_date"], data["status"], data["resume_version"],
         data["cover_letter_sent"], encode_json(data["interview_data"]), application_id),
    )


def delete_application(application_id):
    _, count = execute("DELETE FROM applications WHERE application_id = %s", (application_id,))
    return count > 0


# ----------------------------------------------------------------- contacts

CONTACT_SELECT = """SELECT t.*, c.company_name
    FROM contacts t JOIN companies c ON c.company_id = t.company_id"""


def get_contacts():
    return query_all(CONTACT_SELECT + " ORDER BY t.contact_name")


def get_contacts_for_company(company_id):
    return query_all(
        CONTACT_SELECT + " WHERE t.company_id = %s ORDER BY t.contact_name", (company_id,)
    )


def get_contact(contact_id):
    return query_one(CONTACT_SELECT + " WHERE t.contact_id = %s", (contact_id,))


def create_contact(data):
    new_id, _ = execute(
        """INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (data["company_id"], data["contact_name"], data["title"], data["email"],
         data["phone"], data["linkedin_url"], data["notes"]),
    )
    return new_id


def update_contact(contact_id, data):
    execute(
        """UPDATE contacts SET company_id = %s, contact_name = %s, title = %s, email = %s,
                  phone = %s, linkedin_url = %s, notes = %s
           WHERE contact_id = %s""",
        (data["company_id"], data["contact_name"], data["title"], data["email"],
         data["phone"], data["linkedin_url"], data["notes"], contact_id),
    )


def delete_contact(contact_id):
    _, count = execute("DELETE FROM contacts WHERE contact_id = %s", (contact_id,))
    return count > 0
