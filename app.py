"""Flask application for the Job Application Tracker."""
import os
import re
from datetime import date, datetime

from flask import Flask, abort, flash, redirect, render_template, request, url_for

import database as db
from matching import parse_skills, rank_jobs

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


def get_datetime(form, name, label, errors):
    """Parse an optional datetime-local field (YYYY-MM-DDTHH:MM) and return a datetime or None."""
    raw = (form.get(name) or "").strip()
    if not raw:
        return None
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    errors.append(f"{label} must be a valid date and time.")
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
    return render_template(
        "dashboard.html", section="dashboard",
        counts=db.get_counts(), status_counts=db.get_status_counts(), statuses=STATUSES,
        recent=db.get_recent_applications(), salary=db.get_salary_stats(),
        upcoming=db.get_upcoming_interviews(date.today().isoformat()),
    )


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
                           jobs=db.get_jobs_for_company(company_id),
                           contacts=db.get_contacts_for_company(company_id))


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
        "job_description": get_text(form, "job_description", "Job description", 5000, errors),
        "job_type": get_choice(form, "job_type", "Job type", JOB_TYPES, errors),
        "salary_min": get_int(form, "salary_min", "Minimum salary", errors),
        "salary_max": get_int(form, "salary_max", "Maximum salary", errors),
        "job_url": get_url(form, "job_url", "Job URL", 300, errors),
        "date_posted": get_date(form, "date_posted", "Date posted", errors),
        "is_active": form.get("is_active") == "on",
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
    preset = {"company_id": request.args.get("company_id", type=int), "is_active": True}
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


# ------------------------------------------------------------ applications

STATUSES = ["Applied", "Screening", "Interview", "Offer", "Rejected", "Withdrawn"]


def get_job_id(form, errors):
    raw = (form.get("job_id") or "").strip()
    if not raw.isdigit():
        errors.append("Job is required.")
        return None
    job_id = int(raw)
    if db.get_job(job_id) is None:
        errors.append("The selected job does not exist.")
        return None
    return job_id


def read_rounds(form):
    """Collect the repeated interview round fields into a list of dicts."""
    dates = form.getlist("round_date")
    types = form.getlist("round_type")
    people = form.getlist("round_interviewer")
    notes = form.getlist("round_notes")
    rounds = []
    for i in range(len(dates)):
        rounds.append({
            "date": dates[i].strip(),
            "type": types[i].strip() if i < len(types) else "",
            "interviewer": people[i].strip() if i < len(people) else "",
            "notes": notes[i].strip() if i < len(notes) else "",
        })
    return rounds


def validate_rounds(rounds, errors):
    """Drop empty rounds and check the rest; returns the cleaned list."""
    cleaned = []
    for number, rnd in enumerate(rounds, start=1):
        if not any(rnd.values()):
            continue
        if rnd["date"]:
            try:
                datetime.strptime(rnd["date"], "%Y-%m-%d")
            except ValueError:
                errors.append(f"Interview round {number}: date is not valid.")
        if len(rnd["type"]) > 50:
            errors.append(f"Interview round {number}: type must be 50 characters or fewer.")
        if len(rnd["interviewer"]) > 100:
            errors.append(f"Interview round {number}: interviewer must be 100 characters or fewer.")
        if len(rnd["notes"]) > 1000:
            errors.append(f"Interview round {number}: notes must be 1000 characters or fewer.")
        cleaned.append(rnd)
    return cleaned


def parse_application_form(form):
    errors = []
    rounds = validate_rounds(read_rounds(form), errors)
    data = {
        "job_id": get_job_id(form, errors),
        "application_date": get_date(form, "application_date", "Application date", errors, required=True),
        "status": get_choice(form, "status", "Status", STATUSES, errors, required=True),
        "resume_version": get_text(form, "resume_version", "Resume version", 50, errors),
        "cover_letter_sent": form.get("cover_letter_sent") == "on",
        "response_date": get_date(form, "response_date", "Response date", errors),
        "interview_date": get_datetime(form, "interview_date", "Interview date", errors),
        "interview_data": {"rounds": rounds} if rounds else None,
        "notes": get_text(form, "notes", "Notes", 5000, errors),
    }
    return data, errors


def application_form_context(application, rounds, mode, application_id=None):
    return dict(section="applications", application=application, rounds=rounds, mode=mode,
                application_id=application_id, jobs=db.job_choices(), statuses=STATUSES)


@app.route("/applications")
def applications():
    status = request.args.get("status", "")
    if status not in STATUSES:
        status = ""
    return render_template("applications.html", section="applications",
                           applications=db.get_applications(status or None),
                           statuses=STATUSES, current_status=status)


@app.route("/applications/<int:application_id>")
def application_detail(application_id):
    application = or_404(db.get_application(application_id))
    return render_template("application_detail.html", section="applications", application=application)


@app.route("/applications/new", methods=["GET", "POST"])
def application_new():
    if request.method == "POST":
        data, errors = parse_application_form(request.form)
        if errors:
            flash_errors(errors)
            return render_template("application_form.html", **application_form_context(
                request.form, read_rounds(request.form), "new"))
        db.create_application(data)
        flash("Application was added.", "success")
        return redirect(url_for("applications"))
    preset = {"application_date": date.today().isoformat(), "status": "Applied",
              "job_id": request.args.get("job_id", type=int)}
    return render_template("application_form.html", **application_form_context(preset, [], "new"))


@app.route("/applications/<int:application_id>/edit", methods=["GET", "POST"])
def application_edit(application_id):
    application = or_404(db.get_application(application_id))
    if request.method == "POST":
        data, errors = parse_application_form(request.form)
        if errors:
            flash_errors(errors)
            return render_template("application_form.html", **application_form_context(
                request.form, read_rounds(request.form), "edit", application_id))
        db.update_application(application_id, data)
        flash("Application was updated.", "success")
        return redirect(url_for("applications"))
    rounds = (application["interview_data"] or {}).get("rounds", [])
    if application["interview_date"]:
        # datetime-local inputs want YYYY-MM-DDTHH:MM
        application["interview_date"] = application["interview_date"].strftime("%Y-%m-%dT%H:%M")
    return render_template("application_form.html", **application_form_context(
        application, rounds, "edit", application_id))


@app.route("/applications/<int:application_id>/delete", methods=["POST"])
def application_delete(application_id):
    or_404(db.get_application(application_id))
    db.delete_application(application_id)
    flash("Application was deleted.", "success")
    return redirect(url_for("applications"))


# ---------------------------------------------------------------- contacts

def parse_contact_form(form):
    errors = []
    data = {
        "company_id": get_company_id(form, errors),
        "contact_name": get_text(form, "contact_name", "Contact name", 100, errors, required=True),
        "title": get_text(form, "title", "Title", 100, errors),
        "email": get_email(form, "email", "Email", 100, errors),
        "phone": get_text(form, "phone", "Phone", 20, errors),
        "linkedin_url": get_url(form, "linkedin_url", "LinkedIn URL", 200, errors),
        "notes": get_text(form, "notes", "Notes", 5000, errors),
    }
    if data["phone"] and not PHONE_RE.match(data["phone"]):
        errors.append("Phone may only contain digits, spaces, + ( ) - and . (7 to 20 characters).")
    return data, errors


def contact_form_context(contact, mode, contact_id=None):
    return dict(section="contacts", contact=contact, mode=mode, contact_id=contact_id,
                companies=db.company_choices())


@app.route("/contacts")
def contacts():
    return render_template("contacts.html", section="contacts", contacts=db.get_contacts())


@app.route("/contacts/new", methods=["GET", "POST"])
def contact_new():
    if request.method == "POST":
        data, errors = parse_contact_form(request.form)
        if errors:
            flash_errors(errors)
            return render_template("contact_form.html", **contact_form_context(request.form, "new"))
        db.create_contact(data)
        flash(f"Contact '{data['contact_name']}' was added.", "success")
        return redirect(url_for("contacts"))
    preset = {"company_id": request.args.get("company_id", type=int)}
    return render_template("contact_form.html", **contact_form_context(preset, "new"))


@app.route("/contacts/<int:contact_id>/edit", methods=["GET", "POST"])
def contact_edit(contact_id):
    contact = or_404(db.get_contact(contact_id))
    if request.method == "POST":
        data, errors = parse_contact_form(request.form)
        if errors:
            flash_errors(errors)
            return render_template("contact_form.html", **contact_form_context(request.form, "edit", contact_id))
        db.update_contact(contact_id, data)
        flash(f"Contact '{data['contact_name']}' was updated.", "success")
        return redirect(url_for("contacts"))
    return render_template("contact_form.html", **contact_form_context(contact, "edit", contact_id))


@app.route("/contacts/<int:contact_id>/delete", methods=["POST"])
def contact_delete(contact_id):
    contact = or_404(db.get_contact(contact_id))
    db.delete_contact(contact_id)
    flash(f"Contact '{contact['contact_name']}' was deleted.", "success")
    return redirect(url_for("contacts"))


# --------------------------------------------------------------- job match

@app.route("/job-match")
def job_match():
    skills_text = (request.args.get("skills") or "").strip()
    user_skills = parse_skills(skills_text)
    results = None
    if "skills" in request.args:
        if not user_skills:
            flash("Enter at least one skill, separated by commas.", "error")
        elif len(skills_text) > 500:
            flash("Skills list is too long (500 characters max).", "error")
        else:
            results = rank_jobs(user_skills, db.get_jobs())
    return render_template("job_match.html", section="job_match", skills_text=skills_text,
                           user_skills=user_skills, results=results)


if __name__ == "__main__":
    app.run(debug=True)
