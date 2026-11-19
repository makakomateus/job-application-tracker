# AI Usage

The course allows GenAI and asks us to say how we used it, so this is what I did. I used it a lot on this project. Most of the code was written by AI agents, and my part was giving direction, deciding things, testing, and reading through what it made.

## Tools Used

I used Claude Code (Anthropic's coding agent) inside the Claude desktop app. The main session ran Claude Opus. It planned the work and split it between sub-agents running Claude Sonnet: one built the app, one reviewed and tested it, and one helped with the docs. I didn't use any other AI tools.

## Key Prompts

These are roughly what I typed, shortened a bit.

1. I gave it the professor's Project_Specification.docx and the Canvas assignment text and said: build the whole Job Application Tracker with Flask and MySQL, use agents to do the work, and set up a GitHub repo.
2. I pasted what classmates said in the group chat about the demo video (3 to 7 minutes, show the command line, database, browser and GitHub, and watch out for browser autofill leaking personal info) and asked it to plan the video around that.
3. I sent a screenshot of Docker Desktop crashing ("An unexpected error occurred ... initializing Inference manager ... The file cannot be accessed by the system") and asked it to fix it, since it happened every time Docker started.
4. "Don't over-engineer this. Keep it simple, hit everything in the rubric, no extra features."
5. I asked for the README and docs to be written in plain, normal language and not sound like AI.
6. I asked it to record the demo video with OBS, since narration was optional.
7. I sent it my Assignment 1-5 instruction docs and asked it to check the project against them, since the assignment says to use the tables from those.
8. "Go back through every assignment again, line by line, and make sure the data is exactly what the assignments had. Nothing made up unless the spec needs it. I need to be 10000% sure."

## What Worked Well

Giving it the full spec and assignment text at the start saved a lot of time. It built the app in the same order as the rubric: database first, then each table's pages, then the dashboard, then Job Match.

Some design choices came from the AI and I kept them:

- All SQL lives in `database.py` and uses parameterized queries, so `app.py` only has routes and validation.
- JSON columns (job requirements and interview rounds) are written with `json.dumps` and read back through one helper.
- Forms validate on the server, show flash messages, and keep what you typed after an error.
- Job Match is a plain function in `matching.py` that doesn't touch the database, so it has unit tests in `tests/test_job_match.py`. It ranks by percentage, then by number of matched skills, and puts jobs with no requirements last.
- Every delete button shows a `confirm()` warning first. The foreign keys are plain like in Assignment 2, so the app catches MySQL's "row is still referenced" error and shows a message instead of crashing.
- `salary_min <= salary_max` is checked in the app before saving.
- The agent recorded a first demo video with OBS. After the database was changed to match my earlier assignments, that video was out of date, so I recorded the final video myself, following a step-by-step script the agent wrote.

It also tested its own work with an end-to-end script that created, edited and deleted rows in all 4 tables, triggered the validation errors, checked that a company or job that is still in use can't be deleted, and checked Job Match. For example "python, SQL, FLASK" gave Software Developer 100% (3/3), and the next result was Data Analyst 67% (2/3) with Tableau missing. It also cloned the repo fresh and followed the README to make sure the setup steps work.

When git had no name or email set, the agent stopped and asked me instead of guessing. I chose my GitHub noreply email and it set that for this repo only.

## What I Modified

- Scope. The first plan already had a few extras built in: an average salary stat, upcoming interviews, and a status filter. I kept them since they were done, and told it not to add anything more after that.
- MySQL. It wasn't installed on my computer, so for development the project runs MySQL 8.4 in a Docker container. The README still works with a normal MySQL install.
- Docker crash. Docker Desktop kept crashing on startup because the Claude app runs in a Windows app sandbox with a virtualized AppData folder, which broke Docker's socket file. The fix was starting Docker Desktop outside the sandbox (through a WMI process create), and then it worked.
- Wrong package version. The AI pinned `mysql-connector-python` to 9.4.0 from memory, but the version actually installed was 26.10.0. This was caught before the commit and `requirements.txt` was fixed using `pip freeze`.
- Windows path bug. A helper script used a Git Bash style `/c/...` path that Windows Python couldn't read, so one route silently didn't get added. It got caught because the nav link threw a `url_for` BuildError. It was fixed with a normal Windows path.
- Review pass. A second agent went through every page and the code. It didn't find logic or security bugs, but it fixed the Edit/Delete buttons breaking the table row lines and made the "n/a" on jobs with no requirements grey instead of red so it doesn't look like a 0% score.
- Schema. The first version only followed the project spec. After comparing it with Assignments 1-5, the schema got the missing columns (`job_description`, `is_active`, `response_date`, `interview_date`, `notes`, `created_at`), the Assignment 3 indexes, and the assignments' sample data. Where the two documents disagreed on a name or type, I kept the spec's version. The job and application forms and the detail pages got the new fields, and failed writes in `database.py` now roll back like in Assignments 4 and 5.
- Second audit. That first pass still had things the AI made up: job descriptions and posting URLs, `https://` added to the websites, response dates and interview names, three extra applications to cover every status, a note on Digital Innovations, `ON DELETE CASCADE` and a salary CHECK. I asked it to go back through every assignment line by line. It replayed every statement from Assignments 1-5 in order on a scratch database (skipping the rolled back ones) and rebuilt `schema.sql` from the result. It caught that the Assignment 4 company notes UPDATE actually fails in MySQL, so that note was never saved, and that ids like New Tech Corp's 7 come from the deleted and rolled back rows. The only invented values left are the job `requirements` lists and a little `interview_data`, because the spec needs them and the assignments have none. It also relaxed the web address check so `www.techsolutions.com` is accepted, and removed the cascade so the foreign keys match Assignment 2.
- Docs. I had the README and this file rewritten in plainer wording, and the setup steps were tested on a fresh clone.

## Lessons Learned

- Giving the AI the whole spec up front worked better than describing it piece by piece.
- Give the AI all the context up front, including the earlier assignments. It only knows what you give it, and it built the first version without Assignments 2 to 5, so the schema had to be fixed afterwards, and even the first fix added things I never had.
- When I need the data to match something exact, say so and tell it not to invent anything. It filled gaps with realistic looking data until I asked for the audit.
- You still have to test what it writes. Some things only showed up when the app actually ran, like the missing route and the wrong package version.
- The AI can be confidently wrong about versions and file paths. Check with `pip freeze` and by running things instead of trusting what it says from memory.
- If you don't tell it the scope, it adds extras. Saying "keep it simple" made a real difference.
- Knowing your own setup matters. The Docker problem made no sense until it was clear the Claude app runs in a sandbox.
- Splitting the work into a build agent and a review agent caught mistakes the builder missed.
- I read through the code to understand how it fits together: routes and validation in `app.py`, all queries in `database.py`, and the matching logic in `matching.py`. I'm comfortable explaining those parts, though I didn't write most of the lines myself.
