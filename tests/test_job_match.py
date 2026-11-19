import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from matching import match_job, parse_skills, rank_jobs  # noqa: E402


class ParseSkillsTest(unittest.TestCase):
    def test_trims_and_drops_empty(self):
        self.assertEqual(parse_skills(" Python , ,SQL,, flask "), ["Python", "SQL", "flask"])

    def test_empty_input(self):
        self.assertEqual(parse_skills(""), [])
        self.assertEqual(parse_skills(None), [])


class MatchJobTest(unittest.TestCase):
    def test_full_match(self):
        result = match_job(["python", "sql", "flask"], ["Python", "SQL", "Flask"])
        self.assertEqual(result["percent"], 100)
        self.assertEqual((result["matched_count"], result["total"]), (3, 3))
        self.assertEqual(result["missing"], [])

    def test_partial_match_lists_missing(self):
        result = match_job(["sql", "excel"], ["SQL", "Excel", "Tableau"])
        self.assertEqual(result["percent"], 67)
        self.assertEqual(result["matched"], ["SQL", "Excel"])
        self.assertEqual(result["missing"], ["Tableau"])

    def test_case_and_whitespace_ignored(self):
        result = match_job(["  PYTHON  "], ["python"])
        self.assertEqual(result["percent"], 100)

    def test_no_match(self):
        result = match_job(["Java"], ["Python", "SQL"])
        self.assertEqual(result["percent"], 0)
        self.assertEqual(result["missing"], ["Python", "SQL"])

    def test_no_requirements(self):
        for reqs in ([], None):
            result = match_job(["Python"], reqs)
            self.assertIsNone(result["percent"])
            self.assertEqual(result["total"], 0)


class RankJobsTest(unittest.TestCase):
    def test_sorted_best_first_and_empty_last(self):
        jobs = [
            {"job_title": "Writer", "requirements": []},
            {"job_title": "Analyst", "requirements": ["SQL", "Excel", "Tableau"]},
            {"job_title": "Developer", "requirements": ["Python", "SQL", "Flask"]},
        ]
        ranked = rank_jobs(["python", "sql", "flask", "excel"], jobs)
        self.assertEqual([r["job"]["job_title"] for r in ranked], ["Developer", "Analyst", "Writer"])
        self.assertEqual([r["percent"] for r in ranked], [100, 67, None])


if __name__ == "__main__":
    unittest.main()
