-- Job Application Tracker schema and sample data
DROP DATABASE IF EXISTS job_tracker;
CREATE DATABASE job_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE job_tracker;

CREATE TABLE companies (
    company_id   INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    industry     VARCHAR(50),
    website      VARCHAR(200),
    city         VARCHAR(50),
    state        VARCHAR(50),
    notes        TEXT
);

CREATE TABLE jobs (
    job_id       INT AUTO_INCREMENT PRIMARY KEY,
    company_id   INT NOT NULL,
    job_title    VARCHAR(100) NOT NULL,
    job_type     ENUM('Full-time','Part-time','Contract','Internship'),
    salary_min   INT,
    salary_max   INT,
    job_url      VARCHAR(300),
    date_posted  DATE,
    requirements JSON,
    CONSTRAINT fk_jobs_company FOREIGN KEY (company_id)
        REFERENCES companies (company_id) ON DELETE CASCADE,
    CONSTRAINT chk_salary_range CHECK (salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max)
);

CREATE TABLE applications (
    application_id    INT AUTO_INCREMENT PRIMARY KEY,
    job_id            INT NOT NULL,
    application_date  DATE NOT NULL,
    status            ENUM('Applied','Screening','Interview','Offer','Rejected','Withdrawn') DEFAULT 'Applied',
    resume_version    VARCHAR(50),
    cover_letter_sent BOOLEAN DEFAULT FALSE,
    interview_data    JSON,
    CONSTRAINT fk_applications_job FOREIGN KEY (job_id)
        REFERENCES jobs (job_id) ON DELETE CASCADE
);

CREATE TABLE contacts (
    contact_id   INT AUTO_INCREMENT PRIMARY KEY,
    company_id   INT NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    title        VARCHAR(100),
    email        VARCHAR(100),
    phone        VARCHAR(20),
    linkedin_url VARCHAR(200),
    notes        TEXT,
    CONSTRAINT fk_contacts_company FOREIGN KEY (company_id)
        REFERENCES companies (company_id) ON DELETE CASCADE
);

INSERT INTO companies (company_name, industry, website, city, state, notes) VALUES
('TechCorp', 'Software', 'https://www.techcorp.example.com', 'Miami', 'Florida', 'Mid-size product company. Referred by a classmate.'),
('DataCo', 'Data Analytics', 'https://www.dataco.example.com', 'Orlando', 'Florida', 'Analytics consultancy with a hybrid schedule.'),
('CloudNine Systems', 'Cloud Services', 'https://www.cloudnine.example.com', 'Austin', 'Texas', 'Remote-friendly, large engineering team.'),
('Sunshine Health', 'Healthcare IT', 'https://www.sunshinehealth.example.com', 'Tampa', 'Florida', 'Internal tools team, good intern program.'),
('Greenleaf Finance', 'Fintech', 'https://www.greenleaf.example.com', 'Atlanta', 'Georgia', 'Startup, fast hiring process.'),
('PixelForge Studios', 'Media', 'https://www.pixelforge.example.com', 'Denver', 'Colorado', 'Web and design agency.');

INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements) VALUES
(1, 'Software Developer', 'Full-time', 75000, 95000, 'https://www.techcorp.example.com/careers/101', '2026-10-01', '["Python","SQL","Flask"]'),
(1, 'QA Automation Intern', 'Internship', 20000, 26000, 'https://www.techcorp.example.com/careers/102', '2026-10-05', '["Python","Selenium","Git"]'),
(2, 'Data Analyst', 'Full-time', 65000, 80000, 'https://www.dataco.example.com/jobs/21', '2026-09-28', '["SQL","Excel","Tableau"]'),
(2, 'Junior Data Engineer', 'Full-time', 80000, 100000, 'https://www.dataco.example.com/jobs/22', '2026-10-10', '["Python","SQL","Airflow","AWS"]'),
(3, 'Cloud Support Associate', 'Full-time', 60000, 72000, 'https://www.cloudnine.example.com/careers/330', '2026-10-12', '["Linux","AWS","Networking","Bash"]'),
(3, 'DevOps Contractor', 'Contract', 90000, 120000, 'https://www.cloudnine.example.com/careers/331', '2026-10-15', '["Docker","Linux","Git","AWS"]'),
(4, 'IT Help Desk Intern', 'Internship', 18000, 22000, 'https://www.sunshinehealth.example.com/intern/7', '2026-10-03', '["Networking","Windows","Customer Service"]'),
(5, 'Backend Developer', 'Full-time', 85000, 110000, 'https://www.greenleaf.example.com/jobs/55', '2026-10-08', '["Python","Flask","MySQL","REST APIs","Git"]'),
(6, 'Front-End Developer', 'Part-time', 35000, 48000, 'https://www.pixelforge.example.com/jobs/9', '2026-10-14', '["HTML","CSS","JavaScript"]'),
(6, 'Technical Writer', 'Contract', 50000, 62000, 'https://www.pixelforge.example.com/jobs/10', '2026-10-16', '[]');

INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent, interview_data) VALUES
(1, '2026-10-02', 'Interview', 'v3-dev', TRUE, '{"rounds":[{"date":"2026-10-09","type":"Phone screen","interviewer":"Dana Reyes","notes":"Asked about Flask projects."},{"date":"2026-10-20","type":"Technical","interviewer":"Sam Patel","notes":"Live SQL and Python exercise."}]}'),
(2, '2026-10-06', 'Applied', 'v3-dev', FALSE, NULL),
(3, '2026-09-30', 'Rejected', 'v2-data', TRUE, '{"rounds":[{"date":"2026-10-07","type":"Phone screen","interviewer":"Priya Nair","notes":"Position filled internally."}]}'),
(4, '2026-10-11', 'Screening', 'v3-dev', TRUE, '{"rounds":[{"date":"2026-10-22","type":"Recruiter call","interviewer":"Lena Ortiz","notes":"Salary range confirmed."}]}'),
(5, '2026-10-13', 'Applied', 'v1-it', FALSE, NULL),
(6, '2026-10-16', 'Withdrawn', 'v3-dev', FALSE, NULL),
(7, '2026-10-04', 'Offer', 'v1-it', TRUE, '{"rounds":[{"date":"2026-10-12","type":"On-site","interviewer":"Marcus Webb","notes":"Met the help desk team."},{"date":"2026-10-19","type":"Manager interview","interviewer":"Alicia Gomez","notes":"Offer extended verbally."}]}'),
(8, '2026-10-09', 'Interview', 'v3-dev', TRUE, '{"rounds":[{"date":"2026-11-25","type":"Technical","interviewer":"Chris Doyle","notes":"Prepare REST API design questions."}]}'),
(9, '2026-10-15', 'Screening', 'v4-web', TRUE, NULL),
(10, '2026-10-17', 'Applied', 'v2-data', FALSE, NULL);

INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes) VALUES
(1, 'Dana Reyes', 'Technical Recruiter', 'dana.reyes@techcorp.example.com', '305-555-0142', 'https://www.linkedin.com/in/danareyes-example', 'Main recruiting contact.'),
(1, 'Sam Patel', 'Engineering Manager', 'sam.patel@techcorp.example.com', '305-555-0177', 'https://www.linkedin.com/in/sampatel-example', 'Runs the technical round.'),
(2, 'Priya Nair', 'HR Coordinator', 'priya.nair@dataco.example.com', '407-555-0119', NULL, 'Prefers email.'),
(2, 'Lena Ortiz', 'Senior Recruiter', 'lena.ortiz@dataco.example.com', '407-555-0160', 'https://www.linkedin.com/in/lenaortiz-example', NULL),
(3, 'Omar Haddad', 'Hiring Manager', 'omar.haddad@cloudnine.example.com', '512-555-0133', NULL, 'Met at the FIU career fair.'),
(4, 'Marcus Webb', 'IT Director', 'marcus.webb@sunshinehealth.example.com', '813-555-0188', 'https://www.linkedin.com/in/marcuswebb-example', 'Gave the verbal offer.'),
(5, 'Chris Doyle', 'Lead Engineer', 'chris.doyle@greenleaf.example.com', '404-555-0101', NULL, NULL),
(6, 'Jules Martin', 'Creative Producer', 'jules.martin@pixelforge.example.com', '303-555-0155', NULL, 'Posted the technical writer role.');
