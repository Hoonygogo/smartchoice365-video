#!/usr/bin/env python3
"""Publish the exact owner-approved Ninja V4 MP4, verify it, then remove the old video.

Never upload a different render. Never delete the old video before confirmed public
processing and saved YouTube metadata verification of the new video.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.parse

from publish_youtube_generic import api, receipt_read, receipt_write, CHANNEL
from check_youtube import request_json

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "uploads" / "SmartChoice365_Ninja_English_V4_Precise_StableFocus.mp4"
DIGEST = "b0d49b9b59c7cfded99259501fbc744e85c83de319d21fa213dba0e81e4c4e51"
OLD_ID = "UJ-azoT4vso"
PUB_ID = "ninja-af141-af400-en-v4-precise-focus"
RECEIPT = "publications/receipts/" + PUB_ID + "-youtube.json"
GUIDE = "https://smartchoice365-web.pages.dev/guides/2026-ninja-af141-vs-af400-australia-single-dual-basket.html?utm_source=youtube&utm_medium=video&utm_campaign=ninja_af141_af400_en_v4"

META = {
    "snippet": {
        "title": "Ninja AF141 vs AF400 Australia | Which Air Fryer Should You Buy?",
        "description": (
            "👉 Full Ninja AF141 vs AF400 Australian buying guide: " + GUIDE
            + "\n\nWhich is better for your actual meals: one 4.7L basket or two 4.75L drawers?"
            + " Compare everyday cooking, capacity, dual-zone convenience, the five-dinner test,"
            + " and how to assess changing Australian prices.\n\n"
            + "The video uses AI-created illustrative images, not official product photography"
            + " or hands-on product tests. Check model specifications before purchasing."
            + " The website guide may contain clearly disclosed affiliate advertising.\n\n"
            + "Chapters\n0:00 Introduction\n0:10 HD playback tip\n0:18 The two-drawer question"
            + "\n0:25 Capacity comparison\n0:38 Basket limitations"
            + "\n0:46 Two foods, two zones\n0:54 Small households"
            + "\n1:01 Family cooking\n1:09 Australian price checklist"
            + "\n1:18 Five-dinner test\n1:26 Final recommendation\n1:36 Full buying guide\n\n"
            + "#NinjaAirFryer #AF141 #AF400 #SmartChoice365"
        ),
        "categoryId": "26",
        "defaultLanguage": "en",
        "defaultAudioLanguage": "en",
        "tags": ["Ninja AF141", "Ninja AF400", "Ninja air fryer Australia",
                 "air fryer buying guide", "Smart Choice 365"],
    },
    "status": {
        "privacyStatus": "public",
        "selfDeclaredMadeForKids": False,
        "containsSyntheticMedia": True,
        "embeddable": True,
        "license": "youtube",
    },
}

def oauth_token():
    secret = {key: os.environ["YOUTUBE_" + key.upper()].strip()
              for key in ("client_id", "client_secret", "refresh_token")}
    secret["grant_type"] = "refresh_token"
    token = request_json(
        "https://oauth2.googleapis.com/token",
        data=urllib.parse.urlencode(secret).encode("utf-8"),
    )["access_token"]
    print("::add-mask::" + token, flush=True)
    owner = request_json(
        "https://www.googleapis.com/youtube/v3/channels?part=id&mine=true",
        token=token,
    ).get("items", [])
    if [row["id"] for row in owner] != [CHANNEL]:
        raise RuntimeError("YouTube OAuth channel does not match Smart Choice 365")
    return token

def fetch_video(video_id, token, fields="snippet,status,processingDetails"):
    rows = request_json(
        "https://www.googleapis.com/youtube/v3/videos?part=" + fields + "&id=" + video_id,
        token=token,
    ).get("items", [])
    return rows[0] if rows else None

def record(r):
    receipt_write(RECEIPT, r)

def upload_once(media, token, r):
    # The durable receipt lock is recorded before starting the YouTube insert.
    record(r)
    _, headers = api(
        "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
        "POST",
        json.dumps(META, ensure_ascii=False).encode("utf-8"),
        token,
        {
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Length": str(len(media)),
            "X-Upload-Content-Type": "video/mp4",
        },
    )
    session = headers.get("Location", "")
    u = urllib.parse.urlparse(session)
    if u.scheme != "https" or u.hostname != "www.googleapis.com" or not u.path.startswith("/upload/youtube/"):
        raise RuntimeError("Unexpected YouTube upload session endpoint")
    result, _ = api(session, "PUT", media, token, {"Content-Type": "video/mp4"})
    video_id = result.get("id")
    if not video_id or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise RuntimeError("Upload result uncertain. Existing lock prevents duplicate publishing.")
    r.update(video_id=video_id, url="https://www.youtube.com/watch?v=" + video_id,
             status="uploaded_processing")
    record(r)
    return video_id

def verify_new(video_id, token, r):
    for _ in range(36):
        video = fetch_video(video_id, token)
        if video:
            if video["snippet"].get("channelId") != CHANNEL:
                raise RuntimeError("Uploaded video owner mismatch; old video retained")
            state = video["status"]
            processing = video.get("processingDetails", {}).get("processingStatus")
            if state.get("uploadStatus") in ("failed", "rejected", "deleted") or processing in ("failed", "terminated"):
                r.update(status="processing_failed")
                record(r)
                raise RuntimeError("YouTube rejected/failed new video; old video retained")
            if (state.get("uploadStatus") == "processed"
                    and processing == "succeeded"
                    and state.get("privacyStatus") == "public"):
                snippet = video["snippet"]
                if (snippet.get("title") != META["snippet"]["title"]
                        or snippet.get("description") != META["snippet"]["description"]):
                    raise RuntimeError("YouTube saved metadata differs; old video retained")
                r.update(status="published_verified", privacy="public",
                         upload_status="processed", processing_status="succeeded",
                         metadata_verified=True, description_first_line=snippet["description"].splitlines()[0])
                record(r)
                return
        time.sleep(10)
    r["status"] = "awaiting_processing_verification"
    record(r)
    raise RuntimeError("YouTube processing not yet confirmed. Old video retained; safely rerun this workflow later.")

def delete_prior_only_after_verified(token, r):
    assert r["status"] == "published_verified" and r["metadata_verified"] is True
    assert r["video_id"] != OLD_ID
    if r.get("old_video_cleanup", {}).get("status") == "deleted_verified":
        return
    current = fetch_video(r["video_id"], token)
    if not current or current["snippet"].get("channelId") != CHANNEL or current["status"].get("privacyStatus") != "public":
        raise RuntimeError("New video lost public status. Old video retained.")
    previous = fetch_video(OLD_ID, token, fields="snippet")
    if previous:
        sn = previous["snippet"]
        if sn.get("channelId") != CHANNEL or "AF141" not in sn.get("title", "").upper() or "AF400" not in sn.get("title", "").upper():
            raise RuntimeError("Old video identity failed safety check; no deletion performed.")
        try:
            api("https://www.googleapis.com/youtube/v3/videos?id=" + OLD_ID,
                "DELETE", token=token)
        except RuntimeError as e:
            r["old_video_cleanup"] = {"video_id": OLD_ID, "status": "deletion_unverified",
                                      "reason": str(e)}
            record(r)
            raise
    # A successful DELETE response is not enough; verify read-after-delete.
    for _ in range(8):
        if not fetch_video(OLD_ID, token, fields="id"):
            r["old_video_cleanup"] = {"video_id": OLD_ID, "status": "deleted_verified"}
            record(r)
            print("Verified replacement and old video deletion: " + r["url"], flush=True)
            return
        time.sleep(5)
    r["old_video_cleanup"] = {"video_id": OLD_ID, "status": "deletion_not_verified"}
    record(r)
    raise RuntimeError("Old video deletion has not been verified")

def main():
    if not FILE.is_file():
        raise RuntimeError("Approved V4 MP4 not present in uploads/")
    media = FILE.read_bytes()
    actual = hashlib.sha256(media).hexdigest()
    if actual != DIGEST:
        raise RuntimeError("Source is not exact approved V4 video. Nothing uploaded or deleted.")
    token = oauth_token()
    existing, _ = receipt_read(RECEIPT)
    if existing:
        if existing.get("sha256") != DIGEST or existing.get("id") != PUB_ID:
            raise RuntimeError("Publication receipt conflicts with approved V4 hash")
        if not existing.get("video_id"):
            raise RuntimeError("Previous upload attempt uncertain. Inspect receipt/YouTube before retrying.")
        r = existing
        video_id = r["video_id"]
    else:
        r = {"id": PUB_ID, "sha256": DIGEST, "channel_id": CHANNEL,
             "status": "upload_initiated", "approval": "publish",
             "approval_note": "Owner explicitly approved V4 publication and old Ninja removal",
             "platform": "youtube", "run_id": os.environ.get("GITHUB_RUN_ID"),
             "replaces_video_id": OLD_ID}
        video_id = upload_once(media, token, r)
    if r.get("status") != "published_verified":
        verify_new(video_id, token, r)
    delete_prior_only_after_verified(token, r)

if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, KeyError, OSError) as exc:
        print(str(exc) if isinstance(exc, RuntimeError) else "Video publication failed; old video retained.", file=sys.stderr)
        sys.exit(1)
