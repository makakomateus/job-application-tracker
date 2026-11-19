"""Flask application for the Job Application Tracker."""
import os
import re
from datetime import date, datetime

from flask import Flask, abort, flash, redirect, render_template, request, url_for

import database as db

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
URL_RE = re.compile(r"^https?://[^\s/$.?#][^\s]*$", re.IGNORECASE)
PHONE_RE = re.compile(r"^[0-9+()\-.\s]{7,20}$")


# ------------------------------------------------------------ form helpers

def get_text(form, name, label, max_len, errors, required=False):
    """Read a stripped text field, enforcing required and max length."""
    value = (form.get(name) or "").strip()
    if not value:
        if required:
            errors.append(f"{label} is required.")
        return None
    if max_len and len(value) > max_len:
        errors.append(f"{label} must be {max_len} characters or fewer.")
    return value


def get_url(form, name, label, max_len, errors):
    value = get_text(form, name, label, max_len, errors)
    if value and not URL_RE.match(value):
        errors.append(f"{label} must start with http:// or https://.")
    return value


def get_email(form, name, label, max_len, errors):
    value = get_text(form, name, label, max_len, errors)
    if value and not EMAIL_RE.match(value):
        errors.append(f"{label} is not a valid email address.")
    return value


def get_date(form, name, label, errors, required=False):
    """Parse a YYYY-MM-DD date field and return a date or None."""
    raw = (form.get(name) or "").strip()
    if not raw:
        if required:
            errors.append(f"{label} is required.")
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        errors.append(f"{label} must be a valid date (YYYY-MM-DD).")
        return None


def get_int(form, name, label, errors, minimum=0):
    """Parse an optional non-negative integer field."""
    raw = (form.get(name) or "").strip()
    if not raw:
        return None
    try:
        number = int(raw)
    except ValueError:
        errors.append(f"{label} must be a whole number.")
        return None
    if number < minimum:
        errors.append(f"{label} cannot be negative.")
        return None
    if number > 2_000_000_000:
        errors.append(f"{label} is too large.")
        return None
    return number


def get_choice(form, name, label, allowed, errors, required=False):
    value = (form.get(name) or "").strip()
    if not value:
        if required:
            errors.append(f"{label} is required.")
        return None
    if value not in allowed:
        errors.append(f"{label} must be one of: {', '.join(allowed)}.")
        return None
    return value


def flash_errors(errors):
    for message in errors:
        flash(message, "error")


def or_404(record):
    if record is None:
        abort(404)
    return record


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html", section=None), 404


# --------------------------------------------------------------- dashboard

@app.route("/")
def dashboard():
    return redirect(url_for("companies"))


# --------------------------------------------------------------- companies

def parse_company_form(form):
    """Validate the company form; returns (data, errors)."""
    errors = []
    data = {
        "company_name": get_text(form, "company_name", "Company name", 100, errors, required=True),
        "industry": get_text(form, "industry", "Industry", 50, errors),
        "website": get_url(form, "website", "Website", 200, errors),
        "city": get_text(form, "city", "City", 50, errors),
        "state": get_text(form, "state", "State", 50, errors),
        "notes": get_text(form, "notes", "Notes", 5000, errors),
    }
    return data, errors


@app.route("/companies")
def companies():
    return render_template("companies.html", section="companies", companies=db.get_companies())


@app.route("/companies/<int:company_id>")
def company_detail(company_id):
    company = or_404(db.get_company(company_id))
    return render_template("company_detail.html", section="companies", company=company,
                           jobs=db.get_jobs_for_company(company_id))


@app.route("/companies/new", methods=["GET", "POST"])
def company_new():
    if request.method == "POST":
        data, errors = parse_company_form(request.form)
        if errors:
            flash_errors(errors)
            return render_template("company_form.html", section="companies", company=request.form, mode="new")
        db.create_company(data)
        flash(f"Company '{data['company_name']}' was added.", "success")
        return redirect(url_for("companies"))
    return render_template("company_form.html", section="companies", company={}, mode="new")


@app.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
def company_edit(company_id):
    company = or_404(db.get_company(company_id))
    if request.method == "POST":
        data, errors = parse_company_form(request.form)
        if errors:
            flash_errors(errors)
            return render_template("company_form.html", section="companies",
                                   company=request.form, mode="edit", company_id=company_id)
        db.update_company(company_id, data)
        flash(f"Company '{data['company_name']}' was updated.", "success")
        return redirect(url_for("companies"))
    return render_template("company_form.html", section="companies",
                           company=company, mode="edit", company_id=company_id)


@app.route("/companies/<int:company_id>/delete", methods=["POST"])
def company_delete(company_id):
    company = or_404(db.get_company(company_id))
    db.delete_company(company_id)
    flash(f"Company '{company['company_name']}' and its jobs, applications and contacts were deleted.", "success")
    return redirect(url_for("companies"))


# -------------------------------------------------------------------- jobs

JOB_TYPES = ["Full-time", "Part-time", "Contract", "Internship"]


def split_skills(text):
    """Turn comma-separated text into a de-duplicated list of skills."""
    seen, skills = set(), []
    for part in (text or "").split(","):
        skill = part.strip()
        if skill and skill.lower() not in seen:
            seen.add(skill.lower())
            skills.append(skill)
    return skills


def get_company_id(form, errors):
    """Read the company dropdown and make sure the company exists."""
    raw = (form.get("company_id") or "").strip()
    if not raw.isdigit():
        errors.append("Company is required.")
        return None
    company_id = int(raw)
    if db.get_company(company_id) is None:
        errors.append("The selected company does not exist.")
        return None
    return company_id


def parse_job_form(form):
    errors = []
    data = {
        "company_id": get_company_id(form, errors),
        "job_title": get_text(form, "job_title", "Job title", 100, errors, required=True),
        "job_type": get_choice(form, "job_type", "Job type", JOB_TYPES, errors),
        "salary_min": get_int(form, "salary_min", "Minimum salary", errors),
        "salary_max": get_int(form, "salary_max", "Maximum salary", errors),
        "job_url": get_url(form, "job_url", "Job URL", 300, errors),
        "date_posted": get_date(form, "date_posted", "Date posted", errors),
        "requirements": split_skills(form.get("requirements")),
    }
    low, high = data["salary_min"], data["salary_max"]
    if low is not None and high is not None and low > high:
        errors.append("Minimum salary cannot be greater than maximum salary.")
    if len(data["requirements"]) > 40:
        errors.append("Please list 40 requirements or fewer.")
    if any(len(skill) > 60 for skill in data["requirements"]):
        errors.append("Each requirement must be 60 characters or fewer.")
    return data, errors


def job_form_context(job, mode, job_id=None):
    return dict(section="jobs", job=job, mode=mode, job_id=job_id,
                companies=db.company_choices(), job_types=JOB_TYPES)


@app.route("/jobs")
def jobs():
    return render_template("jobs.html", section="jobs", jobs=db.get_jobs())


@app.route("/jobs/<int:job_id>")
def job_detail(job_id):
    job = or_404(db.get_job(job_id))
    return render_template("job_detail.html", section="jobs", job=job)


@app.route("/jobs/new", methods=["GET", "POST"])
def job_new():
    if request.method == "POST":
        data, errors = parse_job_form(request.form)
        if errors:
            flash_errors(errors)
            return render_template("job_form.html", **job_form_context(request.form, "new"))
        db.create_job(data)
        flash(f"Job '{data['job_title']}' was added.", "success")
        return redirect(url_for("jobs"))
    preset = {"company_id": request.args.get("company_id", type=int)}
    return render_template("job_form.html", **job_form_context(preset, "new"))


@app.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def job_edit(job_id):
    job = or_404(db.get_job(job_id))
    if request.method == "POST":
        data, errors = parse_job_form(request.form)
        if errors:
            flash_errors(errors)
            return render_template("job_form.html", **job_form_context(request.form, "edit", job_id))
        db.update_job(job_id, data)
        flash(f"Job '{data['job_title']}' was updated.", "success")
        return redirect(url_for("jobs"))
    job["requirements"] = ", ".join(job["requirements"])
    return render_template("job_form.html", **job_form_context(job, "edit", job_id))


@app.route("/jobs/<int:job_id>/delete", methods=["POST"])
def job_delete(job_id):
    job = or_404(db.get_job(job_id))
    db.delete_job(job_id)
    flash(f"Job '{job['job_title']}' and its applications were deleted.", "success")
    return redirect(url_for("jobs"))


if __name__ == "__main__":
    app.run(debug=True)
