-- Job Application Tracker: database creation script
--
-- The tables and sample data come from Assignments 1 to 5, in order.
-- Where the Project Specification names or types something differently, the
-- specification wins (job_url, salary INT, ENUM columns, contact_name and
-- title). Columns the specification adds that no assignment had are
-- jobs.requirements and applications.interview_data (JSON).
-- Running this file drops and recreates the job_tracker database.

DROP DATABASE IF EXISTS job_tracker;
CREATE DATABASE job_tracker;
USE job_tracker;

-- Assignment 2, Part 3 (with the specification's names and types)
CREATE TABLE companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    industry VARCHAR(50),
    website VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    job_title VARCHAR(100) NOT NULL,
    job_description TEXT,
    salary_min INT,
    salary_max INT,
    job_type ENUM('Full-time','Part-time','Contract','Internship'),
    job_url VARCHAR(300),
    date_posted DATE,
    is_active BOOLEAN DEFAULT TRUE,
    requirements JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    application_date DATE NOT NULL,
    status ENUM('Applied','Screening','Interview','Offer','Rejected','Withdrawn') DEFAULT 'Applied',
    resume_version VARCHAR(50),
    cover_letter_sent BOOLEAN DEFAULT FALSE,
    response_date DATE,
    interview_date DATETIME,
    interview_data JSON,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);

CREATE TABLE contacts (
    contact_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    title VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    linkedin_url VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- Assignment 3 indexes (idx_salary was created and then dropped in that
-- assignment, so it is not here)
CREATE INDEX idx_job_title ON jobs(job_title);
CREATE INDEX idx_company_type ON jobs(company_id, job_type);
CREATE INDEX idx_app_status ON applications(status);
CREATE INDEX idx_company_industry ON companies(industry);

-- ---------------------------------------------------------------------------
-- Sample data
-- ---------------------------------------------------------------------------

-- Assignment 2, Part 4, Step 1 (websites are exactly as typed there)
INSERT INTO companies (company_name, industry, website, city, state) VALUES
('Tech Solutions Inc', 'Technology', 'www.techsolutions.com', 'Miami', 'Florida'),
('Data Analytics Corp', 'Data Science', 'www.dataanalytics.com', 'Austin', 'Texas'),
('Cloud Systems LLC', 'Cloud Computing', 'www.cloudsystems.com', 'Seattle', 'Washington'),
('Digital Innovations', 'Software', 'www.digitalinnovations.com', 'San Francisco', 'California'),
('Smart Tech Group', 'AI/ML', 'www.smarttech.com', 'Boston', 'Massachusetts');

-- Assignment 4, Part 4 (committed). Its company_id is 7 because the Test
-- Company row in Assignment 2 used 6 before it was deleted.
INSERT INTO companies (company_id, company_name, industry, city, state) VALUES
(7, 'New Tech Corp', 'Technology', 'Denver', 'Colorado');

-- Jobs. The assignments never gave job descriptions or posting URLs, so those
-- stay NULL. The requirements lists are the only invented values: they are
-- not in any assignment but the specification needs them for Job Match, so
-- each one is a short list of skills that fits the job title.

-- Assignment 2, Part 4, Step 2
INSERT INTO jobs (company_id, job_title, salary_min, salary_max, job_type, date_posted, requirements) VALUES
(1, 'Software Developer', 70000, 90000, 'Full-time', '2025-01-15', '["Python", "SQL", "Flask"]'),
(1, 'Database Administrator', 75000, 95000, 'Full-time', '2025-01-10', '["MySQL", "SQL", "Indexing"]'),
(2, 'Data Analyst', 65000, 85000, 'Full-time', '2025-01-12', '["Python", "SQL", "Tableau"]'),
(3, 'Cloud Engineer', 80000, 100000, 'Full-time', '2025-01-08', '["AWS", "Linux", "Docker"]'),
(4, 'Junior Developer', 55000, 70000, 'Full-time', '2025-01-14', '["Python", "JavaScript", "Git"]'),
(4, 'Senior Developer', 95000, 120000, 'Full-time', '2025-01-14', '["Python", "Git", "System Design"]'),
(5, 'ML Engineer', 90000, 115000, 'Full-time', '2025-01-11', '["Python", "TensorFlow", "Statistics"]');

-- Assignment 3, Part 2
INSERT INTO jobs (company_id, job_title, salary_min, salary_max, job_type, date_posted, requirements) VALUES
(1, 'QA Engineer', 60000, 80000, 'Full-time', '2025-01-05', '["Testing", "Selenium", "Python"]'),
(2, 'Business Analyst', 65000, 85000, 'Full-time', '2025-01-06', '["SQL", "Excel", "Communication"]'),
(2, 'Data Scientist', 85000, 110000, 'Full-time', '2025-01-07', '["Python", "Statistics", "Machine Learning"]'),
(3, 'DevOps Engineer', 80000, 105000, 'Full-time', '2025-01-08', '["Docker", "Linux", "CI/CD"]'),
(3, 'Security Analyst', 75000, 95000, 'Full-time', '2025-01-09', '["Networking", "Linux", "SIEM"]'),
(4, 'UI/UX Designer', 60000, 80000, 'Full-time', '2025-01-10', '["Figma", "HTML", "CSS"]'),
(5, 'Product Manager', 90000, 120000, 'Full-time', '2025-01-11', '["Agile", "Roadmapping", "Communication"]'),
(1, 'Technical Writer', 55000, 75000, 'Contract', '2025-01-12', '["Technical Writing", "Markdown", "Git"]'),
(2, 'Intern - Data', 30000, 40000, 'Internship', '2025-01-13', '["SQL", "Excel", "Python"]'),
(4, 'Intern - Development', 32000, 42000, 'Internship', '2025-01-14', '["Python", "Git", "HTML"]');

-- Assignment 4, Part 4 (committed; no date_posted was given)
INSERT INTO jobs (company_id, job_title, salary_min, salary_max, job_type, requirements) VALUES
(7, 'Software Architect', 120000, 150000, 'Full-time', '["System Design", "Python", "AWS"]');

-- Applications. Assignment 2, Part 4, Step 3 plus the status changes that
-- were committed later. Status names are mapped to the specification's ENUM:
--   Applied -> Applied, Phone Screen -> Screening,
--   Interview Scheduled / Interview Completed -> Interview,
--   Offer Accepted -> Offer
-- Application 1: Applied, then Offer Accepted (Assignment 5 update_data.py;
--   the Offer Received change in Assignment 4 was rolled back)
-- Application 2: Interview Scheduled, then Interview Completed (Assignment 4 COMMIT)
-- Application 3: Rejected, then Interview Completed (Assignment 2 UPDATE)
-- interview_data is invented, only for applications whose assignment status
-- says an interview or phone screen happened. It repeats that status and
-- nothing else (no dates or names).
INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent, interview_data) VALUES
(1, '2025-01-16', 'Offer', 'v2.1', TRUE, NULL),
(3, '2025-01-13', 'Interview', 'v2.1', TRUE, '{"rounds": [{"type": "Interview", "notes": "Interview completed"}]}'),
(4, '2025-01-09', 'Interview', 'v2.0', FALSE, '{"rounds": [{"type": "Interview", "notes": "Interview completed"}]}'),
(5, '2025-01-15', 'Applied', 'v2.1', TRUE, NULL),
(7, '2025-01-12', 'Screening', 'v2.1', TRUE, '{"rounds": [{"type": "Phone screen"}]}');

-- Assignment 4, Part 5 (committed). The assignment used CURDATE() for the
-- date, so this row is dated the day the script is run. The company notes
-- UPDATE in that part fails in MySQL ('text' + CURDATE() is an error in
-- strict mode), so company 4 keeps NULL notes.
INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent) VALUES
(6, CURDATE(), 'Applied', 'v3.0', TRUE);

-- Contacts. Assignment 2, Part 4, Step 4 (first_name and last_name joined
-- into contact_name, job_title stored as title)
INSERT INTO contacts (company_id, contact_name, email, title) VALUES
(1, 'Sarah Johnson', 'sjohnson@techsolutions.com', 'HR Manager'),
(2, 'Michael Chen', 'mchen@dataanalytics.com', 'Technical Recruiter'),
(3, 'Emily Williams', 'ewilliams@cloudsystems.com', 'Hiring Manager'),
(4, 'David Brown', NULL, 'Senior Developer'),
(5, 'Lisa Garcia', 'lgarcia@smarttech.com', 'Talent Acquisition');

-- Assignment 4, Part 5 (committed). Its contact_id is 7 because the Jennifer
-- Martinez insert in Part 4 used 6 before it was rolled back.
INSERT INTO contacts (contact_id, company_id, contact_name, email, title) VALUES
(7, 4, 'Robert Kim', 'rkim@digitalinnovations.com', 'Engineering Manager');
