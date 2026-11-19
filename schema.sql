-- Job Application Tracker schema and sample data
-- Tables started from Assignment 2 and updated to match the project spec
-- (JSON columns, ENUM columns). Indexes are from Assignment 3.
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
    notes        TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE jobs (
    job_id          INT AUTO_INCREMENT PRIMARY KEY,
    company_id      INT NOT NULL,
    job_title       VARCHAR(100) NOT NULL,
    job_description TEXT,
    job_type        ENUM('Full-time','Part-time','Contract','Internship'),
    salary_min      INT,
    salary_max      INT,
    job_url         VARCHAR(300),
    date_posted     DATE,
    is_active       BOOLEAN DEFAULT TRUE,
    requirements    JSON,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    response_date     DATE,
    interview_date    DATETIME,
    interview_data    JSON,
    notes             TEXT,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_contacts_company FOREIGN KEY (company_id)
        REFERENCES companies (company_id) ON DELETE CASCADE
);

-- Indexes from Assignment 3 (idx_salary was dropped in that assignment, so it is not here)
CREATE INDEX idx_job_title ON jobs(job_title);
CREATE INDEX idx_company_type ON jobs(company_id, job_type);
CREATE INDEX idx_app_status ON applications(status);
CREATE INDEX idx_company_industry ON companies(industry);

-- Sample data: the Assignment 2 companies, plus New Tech Corp from the
-- Assignment 4 transaction (that one was committed). Websites start with
-- https:// because the web form requires it.
INSERT INTO companies (company_name, industry, website, city, state, notes) VALUES
('Tech Solutions Inc', 'Technology', 'https://www.techsolutions.com', 'Miami', 'Florida', NULL),
('Data Analytics Corp', 'Data Science', 'https://www.dataanalytics.com', 'Austin', 'Texas', NULL),
('Cloud Systems LLC', 'Cloud Computing', 'https://www.cloudsystems.com', 'Seattle', 'Washington', NULL),
('Digital Innovations', 'Software', 'https://www.digitalinnovations.com', 'San Francisco', 'California', 'Applied to Senior Developer position on 2025-01-20'),
('Smart Tech Group', 'AI/ML', 'https://www.smarttech.com', 'Boston', 'Massachusetts', NULL),
('New Tech Corp', 'Technology', NULL, 'Denver', 'Colorado', NULL);

-- Jobs: 7 from Assignment 2, 10 from Assignment 3, and the Software Architect
-- job from Assignment 4. Requirements and descriptions are added for the project.
INSERT INTO jobs (company_id, job_title, job_description, job_type, salary_min, salary_max, job_url, date_posted, requirements) VALUES
(1, 'Software Developer', 'Build and maintain web features for the company product using Python and Flask.', 'Full-time', 70000, 90000, 'https://www.techsolutions.com/careers/1', '2025-01-15', '["Python","SQL","Flask"]'),
(1, 'Database Administrator', 'Maintain MySQL databases, run backups and tune slow queries.', 'Full-time', 75000, 95000, 'https://www.techsolutions.com/careers/2', '2025-01-10', '["MySQL","SQL","Backup and Recovery","Indexing"]'),
(2, 'Data Analyst', 'Turn raw data into weekly reports and dashboards for the business team.', 'Full-time', 65000, 85000, 'https://www.dataanalytics.com/jobs/3', '2025-01-12', '["SQL","Excel","Tableau"]'),
(3, 'Cloud Engineer', 'Deploy and monitor services on the cloud platform.', 'Full-time', 80000, 100000, 'https://www.cloudsystems.com/careers/4', '2025-01-08', '["AWS","Linux","Docker","Networking"]'),
(4, 'Junior Developer', 'Entry level role fixing bugs and building small features with a senior mentor.', 'Full-time', 55000, 70000, 'https://www.digitalinnovations.com/jobs/5', '2025-01-14', '["Python","JavaScript","Git"]'),
(4, 'Senior Developer', 'Lead feature design and review code for the engineering team.', 'Full-time', 95000, 120000, 'https://www.digitalinnovations.com/jobs/6', '2025-01-14', '["Python","SQL","Git","REST APIs","System Design"]'),
(5, 'ML Engineer', 'Train and deploy machine learning models for customer products.', 'Full-time', 90000, 115000, 'https://www.smarttech.com/careers/7', '2025-01-11', '["Python","TensorFlow","SQL","Statistics"]'),
(1, 'QA Engineer', 'Write test plans and automated tests for each release.', 'Full-time', 60000, 80000, 'https://www.techsolutions.com/careers/8', '2025-01-05', '["Selenium","Python","Test Planning"]'),
(2, 'Business Analyst', 'Gather requirements from stakeholders and report on results.', 'Full-time', 65000, 85000, 'https://www.dataanalytics.com/jobs/9', '2025-01-06', '["SQL","Excel","Requirements Gathering"]'),
(2, 'Data Scientist', 'Build predictive models and present findings to clients.', 'Full-time', 85000, 110000, 'https://www.dataanalytics.com/jobs/10', '2025-01-07', '["Python","Pandas","Statistics","Machine Learning"]'),
(3, 'DevOps Engineer', 'Automate builds and deployments for the engineering teams.', 'Full-time', 80000, 105000, 'https://www.cloudsystems.com/careers/11', '2025-01-08', '["Docker","Linux","CI/CD","AWS"]'),
(3, 'Security Analyst', 'Watch for threats, review alerts and respond to incidents.', 'Full-time', 75000, 95000, 'https://www.cloudsystems.com/careers/12', '2025-01-09', '["Networking","Linux","SIEM","Incident Response"]'),
(4, 'UI/UX Designer', 'Design screens and prototypes for the web products.', 'Full-time', 60000, 80000, 'https://www.digitalinnovations.com/jobs/13', '2025-01-10', '["Figma","HTML","CSS"]'),
(5, 'Product Manager', 'Own the product roadmap and work with engineering and customers.', 'Full-time', 90000, 120000, 'https://www.smarttech.com/careers/14', '2025-01-11', '["Roadmapping","Agile","Communication"]'),
(1, 'Technical Writer', 'Write user guides and internal documentation.', 'Contract', 55000, 75000, 'https://www.techsolutions.com/careers/15', '2025-01-12', '["Technical Writing","Markdown","Git"]'),
(2, 'Intern - Data', 'Support the analytics team with data cleaning and simple reports.', 'Internship', 30000, 40000, 'https://www.dataanalytics.com/jobs/16', '2025-01-13', '["SQL","Excel","Python"]'),
(4, 'Intern - Development', 'Help the developers with small tasks and testing.', 'Internship', 32000, 42000, 'https://www.digitalinnovations.com/jobs/17', '2025-01-14', '["Python","Git","HTML"]'),
(6, 'Software Architect', 'Design the overall system structure and guide the technical direction.', 'Full-time', 120000, 150000, NULL, NULL, '["System Design","Python","AWS","SQL"]');

-- Applications: the 5 from Assignment 2 with the status changes made in
-- Assignments 2, 4 and 5 that were committed, plus the one from the Assignment 4
-- workflow (job 6). Status names are mapped to the project's ENUM
-- (Phone Screen -> Screening, Interview Completed -> Interview,
-- Offer Accepted -> Offer). Applications 7, 8 and 9 were added so every status is used.
INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent, response_date, interview_date, interview_data, notes) VALUES
(1, '2025-01-16', 'Offer', 'v2.1', TRUE, '2025-02-03', '2025-01-27 14:00:00',
    '{"rounds":[{"date":"2025-01-21","type":"Phone screen","interviewer":"Sarah Johnson","notes":"Asked about Flask projects."},{"date":"2025-01-27","type":"Technical","interviewer":"Sarah Johnson","notes":"Live SQL and Python exercise."}]}',
    'Offer accepted.'),
(3, '2025-01-13', 'Interview', 'v2.1', TRUE, '2025-01-17', '2025-01-20 10:30:00',
    '{"rounds":[{"date":"2025-01-20","type":"Video interview","interviewer":"Michael Chen","notes":"Talked through a sample dashboard."}]}',
    'Interview completed, waiting to hear back.'),
(4, '2025-01-09', 'Interview', 'v2.0', FALSE, '2025-01-14', '2025-01-16 09:00:00',
    '{"rounds":[{"date":"2025-01-16","type":"Video interview","interviewer":"Emily Williams","notes":"Questions about AWS and Linux basics."}]}',
    NULL),
(5, '2025-01-15', 'Applied', 'v2.1', TRUE, NULL, NULL, NULL, NULL),
(7, '2025-01-12', 'Screening', 'v2.1', TRUE, '2025-01-16', '2025-01-18 15:00:00',
    '{"rounds":[{"date":"2025-01-18","type":"Phone screen","interviewer":"Lisa Garcia","notes":"Short call about Python and machine learning projects."}]}',
    NULL),
(6, '2025-01-20', 'Applied', 'v3.0', TRUE, NULL, NULL, NULL, NULL),
(2, '2025-01-11', 'Rejected', 'v2.0', FALSE, '2025-01-22', NULL, NULL, 'Position filled internally.'),
(8, '2025-01-14', 'Withdrawn', 'v2.1', FALSE, NULL, NULL, NULL, 'Withdrew after accepting the Software Developer offer.'),
(10, '2026-11-12', 'Interview', 'v3.0', TRUE, '2026-11-17', '2026-12-03 13:00:00',
    '{"rounds":[{"date":"2026-11-18","type":"Phone screen","interviewer":"Michael Chen","notes":"Went well."},{"date":"2026-12-03","type":"Technical","interviewer":"Michael Chen","notes":"Prepare a Pandas exercise and statistics review."}]}',
    'Second round scheduled.');

-- Contacts: the 5 from Assignment 2 (first and last name joined into contact_name,
-- job_title stored as title) plus Robert Kim from the Assignment 4 workflow.
-- Jennifer Martinez was rolled back in that assignment, so she is not here.
INSERT INTO contacts (company_id, contact_name, title, email) VALUES
(1, 'Sarah Johnson', 'HR Manager', 'sjohnson@techsolutions.com'),
(2, 'Michael Chen', 'Technical Recruiter', 'mchen@dataanalytics.com'),
(3, 'Emily Williams', 'Hiring Manager', 'ewilliams@cloudsystems.com'),
(4, 'David Brown', 'Senior Developer', NULL),
(5, 'Lisa Garcia', 'Talent Acquisition', 'lgarcia@smarttech.com'),
(4, 'Robert Kim', 'Engineering Manager', 'rkim@digitalinnovations.com');
