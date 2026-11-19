# Job Application Tracker

A web app for keeping track of a job search. You can save companies, the jobs they post, the applications you send, and the people you talk to. There is also a Job Match page that compares your skills to the saved jobs' requirements.

I made this for my database course. It uses MySQL for storage, Python with Flask for the backend, and HTML and CSS for the pages. I built it with AI help, and AI_USAGE.md explains how.

## Features

- Dashboard with totals for each table, applications by status, upcoming interviews, recent applications and the average salary range
- Companies, Jobs, Applications and Contacts pages, each with list, add, edit and delete
- Delete buttons ask for confirmation. Deleting a company also deletes its jobs, applications and contacts, and the warning says so
- Server-side validation with error messages: required fields, max lengths, valid dates, valid email and URL, salary min not above salary max, no negative salaries, and dropdown values and foreign keys must exist
- Jobs have a description and an active/inactive flag. Job requirements are stored as a JSON list in the `jobs` table
- Applications also have a response date, an interview date and time, and notes. Interview rounds (date, type, interviewer, notes) are stored as JSON in the `applications` table and are entered with a small add/remove form
- Company page that shows that company's jobs and contacts
- Job Match: type your skills and every job is ranked by match percentage, showing the skills you matched and the ones you are missing

## Tech stack

- Python 3 and Flask
- MySQL 8 (using the `mysql-connector-python` driver)
- python-dotenv for settings
- HTML, Jinja templates and one custom CSS file

## Prerequisites

- Python 3.10 or newer (built and tested with 3.12)
- MySQL 8 installed and running, with a user that can create databases (for example `root`). If you don't have MySQL, see the Docker option below.
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

### Using Docker for MySQL (optional)

If you don't have MySQL installed, you can run it in a container instead. I used this while developing. Pick any password and use the same one in `.env`:

```
docker run --name jobtracker-mysql -e MYSQL_ROOT_PASSWORD=your_password -p 3306:3306 -d mysql:8.4
```

Give it about 30 seconds to start, then load the schema:

```
docker exec -i jobtracker-mysql mysql -uroot -pyour_password < schema.sql
```

After that, follow the same steps as above, skipping the `mysql -u root -p < schema.sql` line.

### Open the app

Go to http://127.0.0.1:5000 in your browser.

`schema.sql` drops and recreates the `job_tracker` database, so running it again resets the sample data. The sample data is 6 companies, 18 jobs, 9 applications and 6 contacts (see Database notes below).

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

- `companies` (company_id, company_name, industry, website, city, state, notes, created_at)
- `jobs` (job_id, company_id, job_title, job_description, job_type, salary_min, salary_max, job_url, date_posted, is_active, requirements JSON, created_at)
- `applications` (application_id, job_id, application_date, status, resume_version, cover_letter_sent, response_date, interview_date, interview_data JSON, notes, created_at)
- `contacts` (contact_id, company_id, contact_name, title, email, phone, linkedin_url, notes, created_at)

`jobs` and `contacts` point to `companies`, and `applications` points to `jobs`. All three foreign keys use `ON DELETE CASCADE`. The jobs table also has a CHECK that `salary_min <= salary_max`.

### Database notes

- The tables started from the ones in Assignment 2. I updated them to match the project specification, which wins when the two disagree. That means `job_url` instead of `posting_url`, whole-number salaries, `contact_name` and `title` on contacts, a `job_type` ENUM, a `status` ENUM (Applied, Screening, Interview, Offer, Rejected, Withdrawn), and two JSON columns: `requirements` on jobs and `interview_data` on applications.
- The extra columns from Assignment 2 are kept: `job_description`, `is_active`, `response_date`, `interview_date`, `notes` and `created_at`.
- Indexes are the ones from Assignment 3: `idx_job_title` on jobs(job_title), `idx_company_type` on jobs(company_id, job_type), `idx_app_status` on applications(status) and `idx_company_industry` on companies(industry). `idx_salary` is not included because that assignment dropped it.
- The sample data comes from the assignments: the 5 companies, 7 jobs, 5 applications and 5 contacts from Assignment 2, the 10 extra jobs from Assignment 3, and what Assignment 4 and 5 left committed (New Tech Corp with its Software Architect job, one more application for Senior Developer, the contact Robert Kim, and the status changes). The Jennifer Martinez contact was rolled back in Assignment 4, so she is not in the data.
- Old status names were mapped to the project's ENUM: Phone Screen became Screening, Interview Scheduled and Interview Completed became Interview, and Offer Received and Offer Accepted became Offer. Contact first and last names were joined into `contact_name`.
- I added a `requirements` list to every job, interview details to the applications that reached interviews, and three more applications (Rejected, Withdrawn and one more Interview) so every status shows up at least once.
- Website values start with `https://` because the form checks for it.

## How Job Match works

1. Type skills separated by commas, like `Python, SQL, Flask`. With the sample data that gives Software Developer 100% (3 of 3). `SQL, Excel` gives Data Analyst 67% with Tableau listed as missing.
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
  AI_USAGE.md       How AI was used
  templates/        Jinja HTML templates (base, dashboard, lists, forms, details, job match)
  static/style.css  Styles
  tests/            Unit tests for the matching function
  demo/             Demo video (demo_video.mp4)
```

## Demo video

The demo video is in the repo at `demo/demo_video.mp4`.

## AI usage

I used Claude Code for most of the code. What I used it for, my prompts, and what I had to fix are in [AI_USAGE.md](AI_USAGE.md).
