#!/usr/bin/env python3
"""Publish only owner-approved Smart Choice 365 Instagram Business Stories.

Uses Meta Graph API and the existing GitHub Actions system-user secret.
No third-party paid API, no link stickers, no token logging, no duplicate retries.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.parse

from publish_meta_reels import (
    API, CHANNEL, checked_file, json_request, preflight_identity, token_for,
    receipt_read, receipt_write, fail,
)

ROOT = Path(__file__).resolve().parents[1]
IG_ACCOUNT = "17841475811391464"
PAGE = "1424295310764332"


def validate_request():
    relative = Path(os.environ.get("STORY_REQUEST_FILE", ""))
    if (relative.is_absolute() or len(relative.parts) != 3
            or relative.parts[:2] != ("publications", "story-requests")
            or relative.suffix != ".json" or ".." in relative.parts):
        fail("Invalid Instagram Story request path.")
    req = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(req, dict):
        fail("Expected JSON story publication request.")
    identity = req.get("id", "")
    if not isinstance(identity, str) or not re.fullmatch(r"[a-z0-9-]{5,96}", identity):
        fail("Invalid Story publication ID.")
    if req.get("approval") != "publish":
        fail("Story publication requires owner approval.")
    if req.get("platform") != "instagram_story" or req.get("channel_id") != CHANNEL:
        fail("Story request target mismatch.")
    if req.get("instagram_account_id") != IG_ACCOUNT:
        fail("Instagram Story account mismatch.")
    if req.get("facebook_page_id") != PAGE:
        fail("Instagram Story linked Page mismatch.")
    if not re.fullmatch(r"[0-9a-f]{64}", str(req.get("sha256",""))):
        fail("Missing SHA-256 of approved Story media.")
    return req


def update_receipt(path, receipt, **fields):
    receipt.update(fields)
    receipt_write(path, receipt)


def verify_story(token, account_id, media_id):
    info = json_request(
        API + "/" + media_id + "?" +
        urllib.parse.urlencode({"fields": "id,media_type,media_product_type,timestamp"}),
        headers={"Authorization": "Bearer " + token})
    if str(info.get("id")) != media_id:
        fail("Instagram Story identity could not be verified; publication might have succeeded.")
    product = info.get("media_product_type", "")
    if product and product != "STORY":
        fail("Meta returned a non-Story media product; manual inspection required.")
    return info


def publish(req, media_url, media_info):
    receipt_path = f"publications/meta-receipts/{req['id']}-instagram-story.json"
    record, _ = receipt_read(receipt_path)
    if record:
        if (record.get("sha256") != req["sha256"]
                or record.get("platform") != "instagram_story"):
            fail("Existing receipt differs. Block duplicate publishing.")
        if record.get("status") == "published_verified":
            print("STORY_ALREADY_VERIFIED id=" + record["media_id"])
            return
    else:
        record = {
            "id": req["id"],
            "platform": "instagram_story",
            "sha256": req["sha256"],
            "media_path": req["media_path"],
            "video_source_url": media_url,
            "video_size": media_info["size"],
            "status": "ready",
            "account_id": IG_ACCOUNT,
            "run_id": os.environ.get("GITHUB_RUN_ID", "")
        }
        receipt_write(receipt_path, record)

    system_credential, is_system_user = token_for("instagram")
    page_id, ig, page_token = preflight_identity(
        {"platforms": ["instagram"]},
        system_credential, system_user_token=is_system_user)
    if page_id != PAGE or ig != IG_ACCOUNT:
        fail("Meta token resolved a different publishing destination.")
    # The linked professional-account identity was checked above. Meta accounts
    # reached through Facebook Login can reject account_type field expansions.
    # The owner confirmed this account is Business in Meta's account UI.
    print("STORY_PAGE_ACCOUNT_PREFLIGHT_OK")

    container = str(record.get("container_id") or "")
    if not container:
        if record.get("status") != "ready":
            fail("Prior Story container creation was uncertain; manual inspection required.")
        update_receipt(receipt_path, record, status="container_creation_initiated")
        created = json_request(
            API + "/" + ig + "/media", method="POST", form={
                "media_type": "STORIES",
                "video_url": media_url,
                "access_token": page_token,
            })
        container = str(created.get("id", ""))
        if not container.isdigit():
            fail("Story container response uncertain; do not retry blindly.")
        update_receipt(
            receipt_path, record, status="container_processing", container_id=container)

    for _ in range(36):
        state = json_request(
            API + "/" + container + "?fields=status_code",
            headers={"Authorization": "Bearer " + page_token})
        result = state.get("status_code")
        if result == "FINISHED":
            break
        if result in ("ERROR", "EXPIRED"):
            update_receipt(receipt_path, record, status="container_failed")
            fail("Instagram Story video processing failed or expired.")
        time.sleep(8)
    else:
        fail("Story container still processing; inspect receipt, do not start another.")

    if record.get("media_id"):
        media_id = str(record["media_id"])
    else:
        if record.get("status") == "media_publish_initiated":
            fail("Previous Story publishing outcome uncertain; don't repost.")
        update_receipt(receipt_path, record, status="media_publish_initiated")
        result = json_request(
            API + "/" + ig + "/media_publish", method="POST",
            form={"creation_id": container, "access_token": page_token})
        media_id = str(result.get("id", ""))
        if not media_id.isdigit():
            fail("Story publish response uncertain; inspect Instagram before any retry.")
        update_receipt(
            receipt_path, record, status="published_unverified", media_id=media_id)

    verify_story(page_token, ig, media_id)
    permalink = f"https://www.instagram.com/stories/smartchoice365official/{media_id}/"
    update_receipt(
        receipt_path, record,
        status="published_verified", media_id=media_id, permalink=permalink)
    print("INSTAGRAM_STORY_VERIFIED " + permalink)


def main():
    req = validate_request()
    media_url, info = checked_file(req)
    if not (3 <= info["duration"] <= 60):
        fail("Instagram Story video must be 3-60 seconds.")
    print("Validated Story media format and bytes. Publishing only approved Instagram Business Story.")
    publish(req, media_url, info)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, KeyError, ValueError) as exc:
        print("META_STORY_FAIL_CLOSED: " + (
            str(exc) if isinstance(exc, RuntimeError) else "media/config error"),
            file=sys.stderr)
        sys.exit(1)
