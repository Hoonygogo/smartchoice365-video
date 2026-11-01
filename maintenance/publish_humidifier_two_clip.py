#!/usr/bin/env python3
"""Publish only the owner's exact 2026-11-01 approved 18.875s humidifier Short.

The file is intentionally SHA-256 pinned. Write a lock receipt before calling
YouTube to prevent a duplicate if the result becomes uncertain. Never delete
or overwrite earlier videos.
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
MEDIA = ROOT / "uploads/SmartChoice365_Humidifier_TwoClip_Short.mp4"
SHA = "4f3c6bd5b691975e1579c86604ca86a08adcdf68f16dc65c657fc1f9e18a27c3"
SIZE = 4292974
ID = "humidifier-two-clip-ko-short-20261101"
RECEIPT = "publications/receipts/" + ID + "-youtube.json"
GUIDE = "https://smartchoice365-web.pages.dev/guides/2026-humidifier-ultrasonic-steam-evaporative-korea.html"
METADATA = {
    "snippet": {
        "title": "가습기 켰다가 방이 안개 천지?! 😂 | 가습기 제대로 고르는 법 #Shorts",
        "description": (
            GUIDE + "\n\n"
            "건조해서 가습기를 켰는데… 방이 안개 천지?! 😱\n"
            "가습기를 무조건 많이 틀기보다 실내 습도를 확인하고 조절하세요.\n\n"
            "초음파식·가열식·자연기화식, 관리와 전기요금까지 자세히 비교한 글은 위 링크에서 확인하세요.\n"
            "Smart Choice 365: https://www.youtube.com/channel/UC4DzAW-Hbd45bIECwGV7-uA\n\n"
            "영상은 이해를 돕기 위한 만화 연출입니다. 링크된 구매 가이드에는 명시된 제휴상품 링크가 포함될 수 있습니다.\n"
            "#가습기 #습도관리 #가습기추천 #SmartChoice365 #Shorts"
        ),
        "categoryId": "26",
        "defaultLanguage": "ko",
        "tags": ["가습기", "가습기 사용법", "실내 습도", "초음파식", "가열식", "자연기화식", "Smart Choice 365"],
    },
    "status": {
        "privacyStatus": "public",
        "selfDeclaredMadeForKids": False,
        "containsSyntheticMedia": True,
        "embeddable": True,
        "license": "youtube",
    },
}

def token_and_channel():
    form = {key: os.environ["YOUTUBE_" + key.upper()].strip()
            for key in ("client_id", "client_secret", "refresh_token")}
    form["grant_type"] = "refresh_token"
    token = request_json(
        "https://oauth2.googleapis.com/token",
        data=urllib.parse.urlencode(form).encode()
    )["access_token"]
    print("::add-mask::" + token, flush=True)
    items = request_json(
        "https://www.googleapis.com/youtube/v3/channels?part=id&mine=true",
        token=token
    ).get("items", [])
    if [c["id"] for c in items] != [CHANNEL]:
        raise RuntimeError("YouTube OAuth channel is not Smart Choice 365.")
    return token

def main():
    if not MEDIA.is_file():
        raise RuntimeError("The exact user-approved MP4 is not in the GitHub uploads folder.")
    data = MEDIA.read_bytes()
    if len(data) != SIZE or hashlib.sha256(data).hexdigest() != SHA:
        raise RuntimeError("Humidifier Short size/SHA mismatch. No upload attempted.")
    token = token_and_channel()
    record, _ = receipt_read(RECEIPT)
    if record:
        if record.get("sha256") != SHA:
            raise RuntimeError("Existing receipt fingerprint differs; block duplicate.")
        video_id = record.get("video_id")
        if not video_id:
            raise RuntimeError("Previous YouTube upload outcome uncertain. Inspect channel; no retry.")
    else:
        record = {
            "id": ID, "sha256": SHA, "channel_id": CHANNEL, "platform": "youtube",
            "approval": "publish", "status": "upload_initiated",
            "run_id": os.environ.get("GITHUB_RUN_ID"),
            "related_guide": GUIDE, "related_video_status": "no_matching_long_video_confirmed"
        }
        receipt_write(RECEIPT, record)
        _, headers = api(
            "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
            "POST", json.dumps(METADATA, ensure_ascii=False).encode(), token,
            {
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Length": str(len(data)),
                "X-Upload-Content-Type": "video/mp4",
            }
        )
        url = headers.get("Location", "")
        parsed = urllib.parse.urlparse(url)
        if (parsed.scheme != "https" or parsed.hostname != "www.googleapis.com"
                or not parsed.path.startswith("/upload/youtube/")):
            raise RuntimeError("Unexpected upload session URL; no media transfer.")
        response, _ = api(url, "PUT", data, token, {"Content-Type": "video/mp4"})
        video_id = response.get("id", "")
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            raise RuntimeError("YouTube upload uncertain; duplicate protected by receipt.")
        record.update(video_id=video_id,
                      url="https://www.youtube.com/shorts/" + video_id,
                      status="uploaded_processing")
        receipt_write(RECEIPT, record)
    for _ in range(36):
        result = request_json(
            "https://www.googleapis.com/youtube/v3/videos?part=snippet,status,processingDetails&id=" + video_id,
            token=token).get("items", [])
        if result:
            video = result[0]
            if video["snippet"].get("channelId") != CHANNEL:
                raise RuntimeError("Uploaded video belongs to an unexpected channel.")
            status = video["status"]
            processing = video.get("processingDetails", {}).get("processingStatus")
            if (status.get("uploadStatus") in ("failed", "rejected", "deleted")
                    or processing in ("failed", "terminated")):
                record["status"] = "processing_failed"
                receipt_write(RECEIPT, record)
                raise RuntimeError("YouTube rejected or failed to process the upload.")
            if (status.get("privacyStatus") == "public"
                    and status.get("uploadStatus") == "processed"
                    and processing == "succeeded"):
                snippet = video["snippet"]
                if (snippet.get("title") != METADATA["snippet"]["title"]
                        or snippet.get("description") != METADATA["snippet"]["description"]):
                    raise RuntimeError("Published YouTube metadata does not match approved copy.")
                record.update(status="published_verified", privacy="public",
                              processing_status="succeeded", metadata_verified=True)
                receipt_write(RECEIPT, record)
                print(json.dumps({"youtube_published": record["url"]}, ensure_ascii=False), flush=True)
                return
        time.sleep(10)
    record["status"] = "awaiting_processing_verification"
    receipt_write(RECEIPT, record)
    raise RuntimeError("YouTube processing unverified; do not retry the upload.")

if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, KeyError, OSError) as exc:
        print(str(exc) if isinstance(exc, RuntimeError) else "YouTube publication configuration failed.",
              file=sys.stderr)
        sys.exit(1)
