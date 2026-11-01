#!/usr/bin/env python3
"""Automatically share an approved, verified Instagram Reel as an Instagram Story.

Called immediately after the existing Reels publisher in the SAME GitHub job.
The Story is a separate native Instagram video Story (not an in-app shared-Reel
sticker); Meta's official API does not support link stickers. GitHub receipts
ensure retries do not publish a second Story.
"""
from __future__ import annotations

import os
import sys

from publish_meta_reels import (
    checked_file, fail, receipt_read, validate_request,
)
from publish_meta_stories import IG_ACCOUNT, PAGE, publish as publish_story


def main():
    # Do not turn a dry-run Reel into a real Story. This is the SAME publishing gate.
    if os.environ.get("META_PUBLISH_ENABLED", "").strip().lower() != "true":
        print("AUTO_STORY_SKIPPED: Reels publishing is in dry-run mode.")
        return

    reel = validate_request()
    if reel.get("approval") != "publish":
        fail("A Story must not publish from a non-approved Reel request.")
    if "instagram" not in reel["platforms"]:
        print("AUTO_STORY_SKIPPED: Request does not publish an Instagram Reel.")
        return
    if reel.get("share_to_instagram_story") is False:
        print("AUTO_STORY_SKIPPED: Owner opted out for this Reel.")
        return
    if reel.get("share_to_instagram_story") not in (None, True, False):
        fail("share_to_instagram_story must be a JSON boolean if supplied.")

    # A Story can be published only AFTER our Meta Reel receipt is fully verified.
    reel_receipt_path = f"publications/meta-receipts/{reel['id']}-instagram.json"
    reel_receipt, _ = receipt_read(reel_receipt_path)
    if not reel_receipt:
        fail("Missing Instagram Reel receipt; no Story attempted.")
    if (reel_receipt.get("status") != "published_verified"
            or reel_receipt.get("platform") != "instagram"
            or reel_receipt.get("sha256") != reel["sha256"]
            or not str(reel_receipt.get("permalink", "")).startswith("https://www.instagram.com/reel/")):
        fail("Instagram Reel is not verified for this approved video; no Story attempted.")

    # Reuse the already approved clip and Meta credential; never include URL stickers.
    url, info = checked_file(reel)
    if not (3 <= info["duration"] <= 60):
        fail("Instagram Story requires an eligible 3-60-second video; cannot auto-share.")

    # Stable ID: exactly one automatic Story for each Reel request. The story
    # publisher's own receipt is stored at <reel_id>-instagram-story.json.
    story = {
        "id": reel["id"],
        "approval": "publish",
        "platform": "instagram_story",
        "channel_id": reel["channel_id"],
        "instagram_account_id": IG_ACCOUNT,
        "facebook_page_id": PAGE,
        "media_path": reel["media_path"],
        "sha256": reel["sha256"],
        "parent_instagram_reel": reel_receipt["permalink"],
    }
    publish_story(story, url, info)
    print("AUTO_STORY_AFTER_REEL_DONE: " + reel["id"])


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, KeyError, ValueError) as e:
        print("AUTO_STORY_FAIL_CLOSED: " + (
            str(e) if isinstance(e, RuntimeError) else "media/config error"),
            file=sys.stderr)
        sys.exit(1)
