# Job Application Tracker

A web app for keeping track of a job search. You can save companies, the jobs they post, the applications you send, and the people you talk to. There is also a Job Match page that compares your skills to the saved jobs' requirements.

I made this for my database course. It uses MySQL for storage, Python with Flask for the backend, and HTML and CSS for the pages. I built it with AI help, and AI_USAGE.md explains how.

## Features

- Dashboard with totals for each table, applications by status, upcoming interviews, recent applications and the average salary range
- Companies, Jobs, Applications and Contacts pages, each with list, add, edit and delete
- Delete buttons ask for confirmation. The foreign keys have no cascade (same as the assignments), so a company can only be deleted once its jobs and contacts are gone, and a job once its applications are gone. The app shows a message if you try earlier
- Server-side validation with error messages: required fields, max lengths, valid dates, valid email and web address, salary min not above salary max, no negative salaries, and dropdown values and foreign keys must exist
- Jobs have a description and an active/inactive flag. Job requirements are stored as a JSON list in the `jobs` table
- Applications also have a response date, an interview date and time, and notes. Interview rounds (date, type, interviewer, notes) are stored as JSON in the `applications` table and are entered with a small add/remove form
- Company page that shows that company's jobs and contacts
- Job Match: type your skills and every job is ranked by match percentage, showing the skills you matched and the ones you are missing

## Technologies

- MySQL Database (8, using the `mysql-connector-python` driver)
- Python with Flask (and python-dotenv for settings)
- HTML/CSS for the web interface (Jinja templates and one CSS file)

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

`schema.sql` drops and recreates the `job_tracker` database, so running it again resets the sample data. The sample data is 6 companies, 18 jobs, 6 applications and 6 contacts (see Database notes below).

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

`jobs` and `contacts` point to `companies`, and `applications` points to `jobs`. The foreign keys are plain `FOREIGN KEY ... REFERENCES` like in Assignment 2, with no `ON DELETE` action.

### Database notes

The database is the one I ended up with after Assignments 1 to 5, plus what the project specification adds. `schema.sql` has a comment for each part of the sample data saying which assignment it came from.

- Tables and columns come from Assignment 2. The specification wins where the two differ, so: `job_url` (not `posting_url`), `salary_min` and `salary_max` are `INT` (not `DECIMAL(10,2)`), `job_type` is the specification's ENUM (not `VARCHAR(20)`), `status` is the specification's ENUM (not `VARCHAR(30)`), and contacts have `contact_name` and `title` (not `first_name`, `last_name` and `job_title`).
- Specification columns the assignments did not have: `requirements` (JSON) on jobs and `interview_data` (JSON) on applications.
- Assignment 2 columns the specification does not list are kept, because the Canvas page says to use the tables from the assignments: `job_description`, `is_active`, `response_date`, `interview_date`, `notes` and `created_at`. So are the `NOT NULL` foreign key columns and the `DEFAULT` values from Assignment 2.
- Indexes are the ones I had at the end of Assignment 3: `idx_job_title`, `idx_company_type`, `idx_app_status` and `idx_company_industry`. `idx_salary` was dropped in that assignment, so it is not there. Assignments 4 and 5 did not add any.
- Sample data is what the assignments left committed: the 5 companies, 7 jobs, 5 applications and 5 contacts from Assignment 2, the 10 jobs from Assignment 3, New Tech Corp and its Software Architect job from Assignment 4, the Assignment 4 application for Senior Developer and the contact Robert Kim, and the status changes. Rolled back changes (the Offer Received update and Jennifer Martinez) are not there, and neither are the Test Company and Python Solutions LLC rows, which those assignments deleted.
- Because of the deleted and rolled back rows, New Tech Corp has company_id 7 and Robert Kim has contact_id 7, which is what running the assignment statements gives.
- Status names from the assignments were mapped to the specification's ENUM: Phone Screen became Screening, Interview Scheduled and Interview Completed became Interview, and Offer Accepted became Offer.
- Websites are kept exactly as typed in Assignment 2 (for example `www.techsolutions.com`, no `https://`), so the web address check accepts them with or without `https://`. The page adds `https://` to the link when it is missing.
- The assignments never gave job descriptions, posting URLs, response dates, interview dates or application notes, so those are empty in the sample data.
- The Assignment 4 workflow application used `CURDATE()`, so that application is dated the day `schema.sql` is run. The company notes UPDATE in that workflow gives an error in MySQL (a text plus a date), so those notes stay empty.
- The only values I made up are the ones the specification needs and no assignment had: a `requirements` list for each job (written to fit the job title) and `interview_data` for the three applications whose status says an interview or phone screen happened (it just repeats that status, with no dates or names).

## How Job Match works

1. Type skills separated by commas, like `Python, SQL, Flask`. With the sample data that gives Software Developer 100% (3 of 3). With the same skills, Data Analyst is second with 67% (2 of 3) and Tableau listed as missing. `SQL, Excel` gives Business Analyst 67% with Communication missing.
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
  tests/            Unit tests for the matching function and the web address check
  demo/             Demo video (demo_video.mp4)
```

## Demo video

The demo video is in the repo at `demo/demo_video.mp4`.

## AI usage

I used Claude Code for most of the code. What I used it for, my prompts, and what I had to fix are in [AI_USAGE.md](AI_USAGE.md).
