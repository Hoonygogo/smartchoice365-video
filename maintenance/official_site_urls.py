"""New-publication website link gate for Smart Choice 365 social channels.

Does not update existing public YouTube/Meta/Naver posts or historical receipts.
Only validates new content before it is sent to a third-party publisher.
"""
from __future__ import annotations
import re

OFFICIAL_SITE = "https://smartc365.com"
LEGACY_HOST = "smartchoice365-web.pages.dev"

def verify_new_publication_site_links(text: str, *, platform: str,
                                      require_website: bool = True) -> None:
    """Raise before upload if a new caption/description uses the old website.

    Third-party issued merchant affiliate URLs are deliberately not modified.
    """
    if not isinstance(text, str):
        raise ValueError(f"{platform}: missing caption/description")
    if re.search(r"(?i)(?:https?://)?(?:www\\.)?smartchoice365-web\\.pages\\.dev(?:[/:?#\\s]|$)", text):
        raise ValueError(f"{platform}: old Pages domain is not allowed; use {OFFICIAL_SITE}")
    if re.search(r"http://(?:www\.)?smartc365\.com(?:/|\b)", text, re.I):
        raise ValueError(f"{platform}: official site must use HTTPS")
    if re.search(r"https://smartc365\.com/guides/[a-z0-9-]+\.html(?:[?#\s]|$)", text):
        raise ValueError(f"{platform}: link the canonical extensionless guide URL")
    if require_website and not re.search(r"https://smartc365\.com(?:/|\b)", text):
        raise ValueError(f"{platform}: include the official Smart Choice 365 website or guide")
