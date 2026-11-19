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


if __name__ == "__main__":
    app.run(debug=True)
