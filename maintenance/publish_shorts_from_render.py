#!/usr/bin/env python3
"""Publish a short produced inside GitHub Actions, without any manual MP4 upload.

Use only with a user-approved request stored in publications/auto-shorts-requests/.
The generated file is read from the SAME runner as the renderer. The YouTube
Related Video field is Studio-only, so this script never claims it was set.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.parse

from publish_youtube_generic import api, receipt_read, receipt_write, CHANNEL
from check_youtube import request_json

ROOT = Path(__file__).resolve().parents[1]
GUIDE_DEFAULT = "https://smartchoice365-web.pages.dev/"

def validated_source(value):
    source = (ROOT / str(value)).resolve()
    if not source.is_relative_to(ROOT) or not source.is_file() or source.suffix.lower() != ".mp4":
        raise RuntimeError("Invalid generated video path")
    if source.stat().st_size < 100_000:
        raise RuntimeError("Generated short video is missing or empty")
    return source

def inspect_short(p):
    info = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_format", "-show_streams",
        "-of", "json", str(p)], text=True, timeout=30))
    tracks = info.get("streams", [])
    videos = [s for s in tracks if s.get("codec_type") == "video"]
    audios = [s for s in tracks if s.get("codec_type") == "audio"]
    if len(videos) != 1 or len(audios) != 1:
        raise RuntimeError("Short must contain one video track and one audio track")
    v, a = videos[0], audios[0]
    if v.get("codec_name") != "h264" or a.get("codec_name") != "aac":
        raise RuntimeError("Only verified H264/AAC Shorts can auto publish")
    if v.get("width", 0) < 540 or v.get("height", 0) < 960:
        raise RuntimeError("Shorts resolution too small")
    if v["width"] >= v["height"]:
        raise RuntimeError("Auto-publish only portrait Shorts")
    duration = float(info.get("format", {}).get("duration", 0))
    if not (8 <= duration <= 180):
        raise RuntimeError("Short must be 8 to 180 seconds")
    return {"width": v["width"], "height": v["height"], "duration": duration}

def owner_token():
    params = {k: os.environ["YOUTUBE_" + k.upper()].strip()
              for k in ("client_id", "client_secret", "refresh_token")}
    params["grant_type"] = "refresh_token"
    token = request_json("https://oauth2.googleapis.com/token",
                         data=urllib.parse.urlencode(params).encode())["access_token"]
    print("::add-mask::" + token, flush=True)
    channels = request_json(
        "https://www.googleapis.com/youtube/v3/channels?part=id&mine=true",
        token=token).get("items", [])
    if [c["id"] for c in channels] != [CHANNEL]:
        raise RuntimeError("YouTube OAuth channel mismatch")
    return token

def video_info(token, video_id, part="snippet,status,processingDetails"):
    videos = request_json(
        "https://www.googleapis.com/youtube/v3/videos?part=" + part + "&id=" + video_id,
        token=token).get("items", [])
    return videos[0] if videos else None

def upload(request, media, token, receipt_path, receipt, metadata):
    receipt_write(receipt_path, receipt)
    _, headers = api(
        "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
        "POST", json.dumps(metadata, ensure_ascii=False).encode(), token,
        {"Content-Type": "application/json; charset=UTF-8",
         "X-Upload-Content-Length": str(len(media)),
         "X-Upload-Content-Type": "video/mp4"})
    session = headers.get("Location", "")
    u = urllib.parse.urlparse(session)
    if u.scheme != "https" or u.hostname != "www.googleapis.com" or not u.path.startswith("/upload/youtube/"):
        raise RuntimeError("Unexpected YouTube resumable upload URL")
    response, _ = api(session, "PUT", media, token, {"Content-Type": "video/mp4"})
    vid = response.get("id")
    if not vid or not re.fullmatch(r"[A-Za-z0-9_-]{11}", vid):
        raise RuntimeError("YouTube insertion outcome uncertain, locked against duplicate")
    receipt.update(status="uploaded_processing", video_id=vid, url="https://www.youtube.com/shorts/" + vid)
    receipt_write(receipt_path, receipt)
    return vid

def main():
    req_path = Path(os.environ["SHORTS_REQUEST_FILE"])
    if req_path.parts[:2] != ("publications", "auto-shorts-requests") or req_path.suffix != ".json":
        raise RuntimeError("Request must be under publications/auto-shorts-requests/")
    req = json.loads((ROOT / req_path).read_text())
    identity = req.get("id", "")
    if not re.fullmatch(r"[a-z0-9-]{4,90}", identity):
        raise RuntimeError("Invalid Short request identity")
    if req.get("approval") != "publish" or req.get("privacy") != "public":
        raise RuntimeError("Only explicitly approved PUBLIC shorts may auto publish")
    if req.get("channel_id") != CHANNEL:
        raise RuntimeError("YouTube channel does not match")
    if req.get("render_mode") != "github_actions_generated":
        raise RuntimeError("Only renderer-produced Shorts supported; no manual MP4 needed")
    source = validated_source(os.environ["SHORTS_VIDEO_FILE"])
    stats = inspect_short(source)
    media = source.read_bytes()
    digest = hashlib.sha256(media).hexdigest()
    title = req.get("title", "")
    description = req.get("description", "")
    related = req.get("related_video_id", "")
    if not title or len(title) > 100 or not description or len(description) > 5000:
        raise RuntimeError("Invalid title or description")
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", related):
        raise RuntimeError("A valid related video ID must be provided")
    if "https://www.youtube.com/watch?v=" + related not in description:
        raise RuntimeError("Description must contain exact corresponding long-video link")
    if not req.get("visual_review_approved"):
        raise RuntimeError("Visual review has not been approved")
    token = owner_token()
    full = video_info(token, related, part="snippet,status")
    if (not full or full["snippet"].get("channelId") != CHANNEL
            or full["status"].get("privacyStatus") not in ("public", "unlisted")):
        raise RuntimeError("Linked full video is not available on the same channel")
    meta = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": "26",
            "defaultLanguage": req.get("language", "en"),
            "defaultAudioLanguage": req.get("language", "en"),
            "tags": req.get("tags", []),
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": bool(req.get("contains_synthetic_media", True)),
            "embeddable": True,
            "license": "youtube"
        }
    }
    receipt_path = "publications/receipts/" + identity + "-youtube.json"
    receipt, _ = receipt_read(receipt_path)
    if receipt:
        if receipt.get("sha256") != digest:
            raise RuntimeError("An earlier run used the same ID with different media; duplicate blocked")
        vid = receipt.get("video_id")
        if not vid:
            raise RuntimeError("Earlier YouTube upload state uncertain; manual inspection required")
    else:
        receipt = {
            "id": identity, "sha256": digest, "channel_id": CHANNEL,
            "status": "upload_initiated", "run_id": os.environ.get("GITHUB_RUN_ID"),
            "approval": req["approval"], "platform": "youtube",
            "source": "generated_in_same_github_actions_runner", "resolution": stats,
            "related_video_id": related,
            "related_video_status": "STUDIO_MANUAL_ACTION_REQUIRED",
            "related_video_note": "YouTube Data API cannot set clickable Shorts Related video. Select target in Studio."
        }
        vid = upload(req, media, token, receipt_path, receipt, meta)
    for _ in range(36):
        current = video_info(token, vid)
        if current:
            if current["snippet"].get("channelId") != CHANNEL:
                raise RuntimeError("Uploaded Short channel mismatch")
            status = current["status"]
            processing = current.get("processingDetails", {}).get("processingStatus")
            if status.get("uploadStatus") in ("failed", "rejected", "deleted") or processing in ("failed", "terminated"):
                receipt["status"] = "processing_failed"
                receipt_write(receipt_path, receipt)
                raise RuntimeError("Short processing failed; receipt retained")
            if (status.get("uploadStatus") == "processed"
                    and processing == "succeeded"
                    and status.get("privacyStatus") == "public"):
                sn = current["snippet"]
                if sn.get("title") != title or sn.get("description") != description:
                    raise RuntimeError("Saved YouTube metadata differs")
                receipt.update(
                    status="published_verified", privacy="public",
                    upload_status="processed", processing_status="succeeded",
                    metadata_verified=True)
                receipt_write(receipt_path, receipt)
                print(json.dumps(receipt, ensure_ascii=False), flush=True)
                return
        time.sleep(10)
    receipt["status"] = "awaiting_processing_verification"
    receipt_write(receipt_path, receipt)
    raise RuntimeError("Uploaded; processing not yet verified, duplicate blocked")

if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, KeyError, OSError, ValueError, subprocess.CalledProcessError) as e:
        print("Auto-short publishing blocked: " + str(e), file=sys.stderr)
        sys.exit(1)
