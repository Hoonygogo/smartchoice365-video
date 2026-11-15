"""Free regression tests for official website URLs in new social publishing."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "maintenance"))
from official_site_urls import verify_new_publication_site_links

class OfficialWebsiteLinkTests(unittest.TestCase):
    def test_valid_guide_and_affiliate(self):
        text = ("#ad\nhttps://smartc365.com/guides/example?utm_source=youtube"
                "\nAmazon: https://link.amazon/B0iDDqoqj")
        verify_new_publication_site_links(text, platform="YouTube")
    def test_homepage_for_channel_introduction(self):
        verify_new_publication_site_links("Visit https://smartc365.com/", platform="Meta")
    def test_legacy_rejected(self):
        with self.assertRaisesRegex(ValueError, "old Pages domain"):
            verify_new_publication_site_links("https://smartchoice365-web.pages.dev/guides/example", platform="YouTube")
    def test_no_site_rejected(self):
        with self.assertRaisesRegex(ValueError, "include the official"):
            verify_new_publication_site_links("Only merchant https://ebay.us/some-affiliate", platform="Meta")
    def test_http_rejected(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            verify_new_publication_site_links("http://smartc365.com/guides/example", platform="Meta")
    def test_authoring_html_rejected(self):
        with self.assertRaisesRegex(ValueError, "extensionless"):
            verify_new_publication_site_links("https://smartc365.com/guides/example.html", platform="Naver")
    def test_legacy_case_variant_rejected(self):
        with self.assertRaisesRegex(ValueError, "old Pages domain"):
            verify_new_publication_site_links("HTTPS://SMARTCHOICE365-WEB.PAGES.DEV/guides/example", platform="YouTube")
    def test_legacy_www_variant_rejected(self):
        with self.assertRaisesRegex(ValueError, "old Pages domain"):
            verify_new_publication_site_links("https://www.smartchoice365-web.pages.dev/", platform="Meta")
    def test_authoring_html_with_fragment_rejected(self):
        with self.assertRaisesRegex(ValueError, "extensionless"):
            verify_new_publication_site_links("https://smartc365.com/guides/Example_v2.html#details", platform="YouTube")
    def test_naver_clip_optional_site(self):
        verify_new_publication_site_links("관련 블로그: https://blog.naver.com/smartchoice365/1234",
                                          platform="Naver Clip", require_website=False)
    def test_naver_clip_legacy_still_rejected(self):
        with self.assertRaisesRegex(ValueError, "old Pages"):
            verify_new_publication_site_links("https://smartchoice365-web.pages.dev/", platform="Naver Clip",
                                              require_website=False)

if __name__ == "__main__":
    unittest.main()
