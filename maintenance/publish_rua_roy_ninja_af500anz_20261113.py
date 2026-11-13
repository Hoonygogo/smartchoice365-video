#!/usr/bin/env python3
"""Publish the owner-approved 30.027-second RUA & ROY Ninja AF500ANZ cartoon with official ending.

One-time upload gate: upload only uploads/SmartChoice365_Ninja_AF500ANZ_RUA_ROY_Official_Outro_30s.mp4.
Other releases need separate owner-approved metadata/hash. No deletion or edits.
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
MEDIA = ROOT / "uploads" / "SmartChoice365_Ninja_AF500ANZ_RUA_ROY_Official_Outro_30s.mp4"
SHA256 = "5db49b1061e56e23f270784e8812bbc4ea2728ec5d40b3899678ab59733de019"
SIZE = 26213477
PUB_ID = "rua-roy-ninja-af500anz-20261113"
RECEIPT = "publications/receipts/" + PUB_ID + "-youtube.json"
SITE = "https://smartchoice365-web.pages.dev/"
CHANNEL_URL = "https://www.youtube.com/channel/" + CHANNEL
META = json.loads((ROOT / "publications/requests/rua-roy-ninja-af500anz-20261113-youtube.json").read_text(encoding="utf-8"))["metadata"]

def save(record):
    receipt_write(RECEIPT, record)

def main():

    caption = META["snippet"]["description"]
    required = (
        "https://link.amazon/B0iDDqoqj",
        "https://ebay.us/Rg5QFm",
        "2026-ninja-af500anz-curated-buying-australia",
        "As an Amazon Associate I earn from qualifying purchases.",
        "eBay Partner Network", "affiliate fee",
    )
    for item in required:
        if item not in caption:
            raise RuntimeError("Required product-specific affiliate copy missing: " + item)
    if len(META["snippet"]["title"]) > 100 or len(caption) > 5000:
        raise RuntimeError("YouTube metadata length invalid")
    if META["status"]["containsSyntheticMedia"] is not False:
        raise RuntimeError("RUA fictional animation requires YouTube AI use No.")
    if not MEDIA.is_file():
        raise RuntimeError("The one owner-approved RUA ROY Ninja AF500ANZ final media is missing from uploads/.")
    video = MEDIA.read_bytes()
    digest = hashlib.sha256(video).hexdigest()
    if len(video) != SIZE or digest != SHA256:
        raise RuntimeError("Unapproved media SHA-256 or size; YouTube upload blocked.")
    creds = {name: os.environ["YOUTUBE_" + name.upper()].strip()
             for name in ("client_id", "client_secret", "refresh_token")}
    if not all(creds.values()):
        raise RuntimeError("YouTube OAuth secrets missing.")
    creds["grant_type"] = "refresh_token"
    token = request_json("https://oauth2.googleapis.com/token",
                         data=urllib.parse.urlencode(creds).encode())["access_token"]
    print("::add-mask::" + token, flush=True)
    channels = request_json(
        "https://www.googleapis.com/youtube/v3/channels?part=id&mine=true", token=token
    ).get("items", [])
    if [c.get("id") for c in channels] != [CHANNEL]:
        raise RuntimeError("OAuth account does not match the approved Smart Choice 365 channel.")

    record, _ = receipt_read(RECEIPT)
    if record:
        if record.get("sha256") != digest or record.get("id") != PUB_ID:
            raise RuntimeError("Conflicting YouTube receipt; duplicate upload blocked.")
        video_id = record.get("video_id")
        if not video_id:
            raise RuntimeError("Prior YouTube upload result uncertain; inspect Studio first.")
    else:
        record = {
            "id": PUB_ID, "sha256": digest, "channel_id": CHANNEL,
            "approval": "publish", "platform": "youtube",
            "status": "upload_initiated", "run_id": os.environ.get("GITHUB_RUN_ID"),
            "note": "Owner approved the exact 30.027s Ninja AF500ANZ 3D cartoon RUA ROY fight + official outro on 2026-11-13; no extra outro",
        }
        save(record)
        _, headers = api(
            "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
            "POST", json.dumps(META, ensure_ascii=False).encode(), token,
            {"Content-Type": "application/json; charset=UTF-8",
             "X-Upload-Content-Length": str(len(video)),
             "X-Upload-Content-Type": "video/mp4"},
        )
        session = headers.get("Location", "")
        u = urllib.parse.urlparse(session)
        if u.scheme != "https" or u.hostname != "www.googleapis.com" or not u.path.startswith("/upload/youtube/"):
            raise RuntimeError("Unexpected YouTube upload endpoint.")
        result, _ = api(session, "PUT", video, token, {"Content-Type": "video/mp4"})
        video_id = result.get("id", "")
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            raise RuntimeError("Upload result uncertain; duplicate locked by receipt.")
        record.update(video_id=video_id, url="https://www.youtube.com/shorts/" + video_id,
                      status="uploaded_processing")
        save(record)

    for _ in range(36):
        rows = request_json(
            "https://www.googleapis.com/youtube/v3/videos?part=snippet,status,processingDetails&id=" + video_id,
            token=token,
        ).get("items", [])
        if rows:
            item = rows[0]
            if item.get("snippet", {}).get("channelId") != CHANNEL:
                raise RuntimeError("YouTube video channel mismatch.")
            status = item["status"]
            processing = item.get("processingDetails", {}).get("processingStatus")
            if status.get("uploadStatus") in ("failed", "rejected", "deleted") or processing in ("failed", "terminated"):
                record["status"] = "processing_failed"
                save(record)
                raise RuntimeError("YouTube processing failed; no retry upload.")
            if (status.get("uploadStatus") == "processed"
                    and processing == "succeeded"
                    and status.get("privacyStatus") == "public"):
                snippet = item["snippet"]
                if snippet.get("title") != META["snippet"]["title"] or snippet.get("description") != META["snippet"]["description"]:
                    raise RuntimeError("Published metadata does not match the approved copy.")
                record.update(status="published_verified", privacy="public",
                              processing_status="succeeded", metadata_verified=True)
                save(record)
                print("NINJA_AF500ANZ_YOUTUBE_VERIFIED " + record["url"], flush=True)
                return
        time.sleep(10)

    record["status"] = "awaiting_processing_verification"
    save(record)
    raise RuntimeError("Video may be uploaded but public processing is not verified. No duplicate.")

if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, KeyError, OSError, ValueError) as exc:
        print("NINJA_AF500ANZ_YOUTUBE_FAIL_CLOSED: " + str(exc), file=sys.stderr)
        sys.exit(1)
