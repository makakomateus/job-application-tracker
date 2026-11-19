# Job Application Tracker

A web app for keeping track of a job search. You can save companies, the jobs they post, the applications you send, and the people you talk to. There is also a Job Match page that compares your skills to the requirements of each saved job.

I built this for my database course. It uses MySQL for storage, Python with Flask for the backend, and HTML and CSS for the pages.

## Features

- Dashboard with totals for each table, applications by status, upcoming interviews, recent applications and the average salary range
- Companies, Jobs, Applications and Contacts pages, each with list, add, edit and delete
- Delete buttons ask for confirmation. Deleting a company also deletes its jobs, applications and contacts, and the warning says so
- Server-side validation with error messages (required fields, max lengths, valid dates, valid email and URL, salary min not above salary max, no negative salaries, dropdown values and foreign keys must exist)
- Job requirements are stored as a JSON list in the `jobs` table
- Interview rounds (date, type, interviewer, notes) are stored as JSON in the `applications` table and are entered with a small add/remove form
- Company page that shows that company's jobs and contacts
- Job Match: type your skills and see every job ranked by match percentage, with the skills you matched and the ones you are missing

## Tech stack

- Python 3 and Flask
- MySQL 8 (using the `mysql-connector-python` driver)
- python-dotenv for settings
- HTML, Jinja templates and one custom CSS file

## Prerequisites

- Python 3.10 or newer (built and tested with 3.12)
- MySQL 8 installed and running, with a user that can create databases (for example `root`)
- Git

## Setup

### Windows (PowerShell or Command Prompt)

```
git clone https://github.com/makakomateus/job-application-tracker.git
cd job-application-tracker
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
mysql -u root -p < schema.sql
copy .env.example .env
```

If `mysql` is not recognized, use the full path to `mysql.exe` (for example `"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"`) or run the file from MySQL Workbench.

Open `.env` and set `DB_PASSWORD` to your MySQL password. Then run:

```
python app.py
```

### Mac / Linux

```
git clone https://github.com/makakomateus/job-application-tracker.git
cd job-application-tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mysql -u root -p < schema.sql
cp .env.example .env
```

Open `.env` and set `DB_PASSWORD` to your MySQL password. Then run:

```
python app.py
```

### Open the app

Go to http://127.0.0.1:5000 in your browser.

`schema.sql` drops and recreates the `job_tracker` database, so running it again resets the sample data. It comes with 6 companies, 10 jobs, 10 applications and 8 contacts.

### Settings (.env)

| Variable | Default | Meaning |
| --- | --- | --- |
| DB_HOST | 127.0.0.1 | MySQL host |
| DB_PORT | 3306 | MySQL port |
| DB_USER | root | MySQL user |
| DB_PASSWORD | (your password) | MySQL password |
| DB_NAME | job_tracker | Database name |
| SECRET_KEY | dev key | Used by Flask for flash messages |

## Database

Four tables in the `job_tracker` database:

- `companies` (company_id, company_name, industry, website, city, state, notes)
- `jobs` (job_id, company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements JSON)
- `applications` (application_id, job_id, application_date, status, resume_version, cover_letter_sent, interview_data JSON)
- `contacts` (contact_id, company_id, contact_name, title, email, phone, linkedin_url, notes)

`jobs` and `contacts` point to `companies`, and `applications` points to `jobs`. All three foreign keys use `ON DELETE CASCADE`. The jobs table also has a CHECK that `salary_min <= salary_max`.

## How Job Match works

1. Type skills separated by commas, like `Python, SQL, Flask`.
2. Each skill is trimmed and compared in lowercase against the `requirements` list of every job.
3. The percentage is matched requirements divided by total requirements for that job, rounded to a whole number.
4. Jobs are sorted from highest to lowest. Jobs with no requirements are listed last and marked as not scored.

The matching code is in `matching.py` and does not touch the database. Run its tests with:

```
python -m unittest discover tests
```

## Project structure

```
job_tracker/
  app.py            Flask routes and form validation
  database.py       Database connection and all SQL queries
  matching.py       Job match logic
  schema.sql        Creates the database, tables and sample data
  requirements.txt  Python packages
  .env.example      Example settings file
  AI_USAGE.md       Notes on how AI was used
  templates/        Jinja HTML templates (base, dashboard, lists, forms, details, job match)
  static/style.css  Styles
  tests/            Unit tests for the matching function
  demo/             Demo video (demo_video.mp4)
```

## Screenshots

Screenshots are not added yet.

## Demo video

The demo video is at `demo/demo_video.mp4`.

## AI usage

See [AI_USAGE.md](AI_USAGE.md).
