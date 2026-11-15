#!/usr/bin/env python3
"""One-time metadata-only source migration.

Converts owned website URLs in reusable/one-time video publishing source
WITHOUT changing any historical approved request JSON, public receipts, media,
affiliate merchant-issued URLs, or external YouTube/Meta accounts.
Invoked only by the domain migration GitHub Action (no publication step).
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OLD_HOST = "smartchoice365-web.pages.dev"
NEW_HOST = "smartc365.com"
# These are historical *live metadata edit* scripts: retain frozen input
# expectations/receipts instead of silently modifying an existing published post.
EXCLUDE = {
    "maintenance/refresh_affiliate_links_20261107.py",
    "maintenance/youtube_description_top.py",
    "maintenance/official_site_urls.py",
    ".github/workflows/official-site-links-qa.yml",
    ".github/workflows/one-time-official-domain-migration.yml",
}
def migrate():
    candidates = list((ROOT/".github/workflows").glob("*.yml"))
    candidates += list((ROOT/"maintenance").glob("publish_*.py"))
    candidates += [ROOT/"scripts/publish_youtube.py"]
    changed = []
    for f in sorted(set(candidates)):
        rel = f.relative_to(ROOT).as_posix()
        if rel in EXCLUDE or not f.is_file():
            continue
        before = f.read_text(encoding="utf-8")
        if OLD_HOST not in before:
            continue
        # Only first-party URLs. Preserve affiliate merchant networks and
        # every immutable approvals/receipts file.
        after = before.replace(OLD_HOST, NEW_HOST)
        after = re.sub(r"https://smartc365\.com/guides/([a-z0-9-]+)\.html",
                       r"https://smartc365.com/guides/\1", after)
        if after != before:
            f.write_text(after, encoding="utf-8")
            changed.append((rel, before.count(OLD_HOST)))
    print("UPDATED SOURCE FILES:")
    for p, hits in changed:
        print(p, hits)
    print("Updated files:", len(changed),
          "; old-domain source literals corrected:", sum(n for _, n in changed))
    print("Approved publication requests, all receipts, actual YouTube/Meta posts and MP4 files: UNCHANGED.")
if __name__ == "__main__":
    migrate()
