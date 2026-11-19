import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import EMAIL_RE, URL_RE, get_url, weblink  # noqa: E402


class UrlTest(unittest.TestCase):
    def test_accepts_addresses_from_the_assignments(self):
        for url in ("www.techsolutions.com", "www.pythonsolutions.com", "https://www.smarttech.com"):
            self.assertTrue(URL_RE.match(url), url)

    def test_accepts_paths_and_http(self):
        for url in ("http://example.com", "example.com/jobs/12?ref=a#top", "https://www.linkedin.com/in/someone"):
            self.assertTrue(URL_RE.match(url), url)

    def test_rejects_junk(self):
        for url in ("javascript:alert(document.domain)", "not a url", "ftp://example.com",
                    "http://", "https://nodot", "data:text/html,hi", "a b.com"):
            self.assertIsNone(URL_RE.match(url), url)

    def test_get_url_reports_error(self):
        errors = []
        value = get_url({"website": "javascript:alert(1)"}, "website", "Website", 200, errors)
        self.assertEqual(value, "javascript:alert(1)")
        self.assertEqual(len(errors), 1)

    def test_weblink_adds_scheme_only_when_missing(self):
        self.assertEqual(weblink("www.techsolutions.com"), "https://www.techsolutions.com")
        self.assertEqual(weblink("http://example.com"), "http://example.com")
        self.assertEqual(weblink(None), "")


class EmailTest(unittest.TestCase):
    def test_email(self):
        self.assertTrue(EMAIL_RE.match("sjohnson@techsolutions.com"))
        self.assertIsNone(EMAIL_RE.match("not-an-email"))


if __name__ == "__main__":
    unittest.main()
