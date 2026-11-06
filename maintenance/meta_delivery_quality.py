#!/usr/bin/env python3
"""Prepare a Meta delivery copy for future approved Reels without altering source media.

Meta fetches MP4 from a public, commit-pinned GitHub URL. This module stages one
technically re-encoded delivery copy only for new publications, preserves the
original source and sound, and never submits anything to Meta by itself.
"""
from __future__ import annotations
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REPO = "Hoonygogo/smartchoice365-video"
VERSION = "meta-1080p-2sec-v1"
MAX_BYTES = 95_000_000


def _run(args, timeout=180):
    return subprocess.run(args, check=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, timeout=timeout)


def probe(path):
    result = _run(["ffprobe", "-v", "error", "-show_streams",
                   "-show_format", "-of", "json", str(path)], timeout=45)
    data = json.loads(result.stdout)
    vs = [s for s in data.get("streams", []) if s.get("codec_type") == "video"]
    audios = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]
    if len(vs) != 1 or len(audios) != 1:
        raise RuntimeError("Meta quality requires exactly one video and one audio stream.")
    video = vs[0]
    if video.get("codec_name") != "h264" or audios[0].get("codec_name") != "aac":
        raise RuntimeError("Meta quality accepts only H.264/AAC approved source.")
    if not 4 <= float(data["format"]["duration"]) <= 60:
        raise RuntimeError("Meta Reel duration must be 4 to 60 seconds.")
    return data, video, audios[0]


def keyframe_times(path):
    result = _run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                   "-skip_frame", "nokey", "-show_entries",
                   "frame=best_effort_timestamp_time",
                   "-of", "csv=p=0", str(path)], timeout=65)
    stamps = []
    for line in result.stdout.splitlines():
        try:
            stamps.append(float(line.split(",")[0]))
        except ValueError:
            continue
    return stamps


def _faststart(path):
    # moov must be ahead of mdat for progressive MP4 delivery.
    with open(path, "rb") as stream:
        head = stream.read(min(path.stat().st_size, 4_000_000))
    moov, mdat = head.find(b"moov"), head.find(b"mdat")
    return moov >= 0 and mdat >= 0 and moov < mdat


def already_optimized(path):
    data, v, _ = probe(path)
    if (v.get("width"), v.get("height"), v.get("pix_fmt")) != (1080, 1920, "yuv420p"):
        return False
    bitrate = int(v.get("bit_rate") or 0)
    if bitrate < 3_700_000 or not _faststart(path):
        return False
    points = keyframe_times(path)
    duration = float(data["format"]["duration"])
    if not points or abs(points[0]) > 0.25:
        return False
    if any(b-a > 2.6 for a,b in zip(points, points[1:])):
        return False
    if duration > 4.5 and len(points) < math.floor((duration - 0.2) / 2):
        return False
    return True


def encode(source, destination):
    data, video, _ = probe(source)
    fps_num, fps_den = map(int, video.get("avg_frame_rate","24/1").split("/"))
    if fps_den == 0:
        raise RuntimeError("Unknown frame rate.")
    fps = fps_num / fps_den
    if not 23 <= fps <= 60:
        raise RuntimeError("Video frame rate outside 23 to 60 FPS.")
    # Preserve the source frame cadence. Two-second IDRs allow reliable seeking.
    gop = round(fps * 2)
    filtergraph = ("scale=1080:1920:force_original_aspect_ratio=decrease,"
                   "pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1")
    _run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
          "-i", str(source), "-map", "0:v:0", "-map", "0:a:0",
          "-vf", filtergraph, "-c:v", "libx264", "-preset", "medium",
          "-b:v", "5M", "-maxrate", "7M", "-bufsize", "10M",
          "-pix_fmt", "yuv420p", "-g", str(gop), "-sc_threshold", "0",
          "-force_key_frames", "expr:gte(t,n_forced*2)",
          "-c:a", "copy", "-movflags", "+faststart", str(destination)],
         timeout=480)
    new, v, a = probe(destination)
    if (v["width"], v["height"]) != (1080, 1920):
        raise RuntimeError("Encoded delivery dimensions failed.")
    if abs(float(new["format"]["duration"]) - float(data["format"]["duration"])) > 0.25:
        raise RuntimeError("Delivery duration changed unexpectedly.")
    if a.get("codec_name") != "aac" or not _faststart(destination):
        raise RuntimeError("Delivery audio/faststart verification failed.")
    points = keyframe_times(destination)
    if not points or any(b-a > 2.6 for a,b in zip(points,points[1:])):
        raise RuntimeError("Keyframe spacing exceeds 2.6 seconds.")
    # Full decoding smoke test before a public upload.
    _run(["ffmpeg", "-hide_banner", "-v", "error", "-xerror",
          "-i", str(destination), "-f", "null", "-"], timeout=480)


def _github(method, path, token, payload=None):
    url = "https://api.github.com/repos/" + REPO + path
    headers = {"Authorization": "Bearer " + token,
               "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28"}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as error:
        if method == "GET" and error.code == 404:
            return None
        raise RuntimeError("GitHub delivery asset operation failed (HTTP %s)" % error.code) from None


def _public_ready(url, expected_size):
    for attempt in range(5):
        request = urllib.request.Request(url, method="HEAD",
                                         headers={"User-Agent":"SC365-Meta-Quality/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=35) as resp:
                actual = resp.headers.get("Content-Length")
                if resp.status == 200 and (actual is None or int(actual) == expected_size):
                    return
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(2)
    raise RuntimeError("Optimized public media is not yet verifiable. No Meta upload.")


def prepare_delivery(req, source_url, source_size):
    """Return (commit-pinned URL, delivered bytes, delivered SHA-256).

    Requests with an existing Meta receipt are handled by the caller so retries
    cannot silently change an already initiated media upload.
    """
    if req.get("meta_quality_profile") == "passthrough":
        return source_url, source_size, req["sha256"]
    if req.get("meta_quality_profile", VERSION) != VERSION:
        raise RuntimeError("Unknown Meta delivery quality profile.")
    path = ROOT / req["media_path"]
    if already_optimized(path):
        print("META_QUALITY_REUSE_EXISTING_APPROVED_1080P")
        return source_url, source_size, req["sha256"]

    token = os.environ.get("GH_TOKEN", "").strip()
    if not token:
        raise RuntimeError("GH_TOKEN required to stage the quality-optimized delivery copy.")
    with tempfile.TemporaryDirectory(prefix="meta-quality-") as folder:
        final = Path(folder) / "delivery.mp4"
        encode(path, final)
        raw = final.read_bytes()
        if not 100000 < len(raw) < MAX_BYTES:
            raise RuntimeError("Optimized delivery file outside safe GitHub byte limit.")
        sha256 = hashlib.sha256(raw).hexdigest()
        filename = req["id"] + "-" + req["sha256"][:12] + "-" + VERSION + ".mp4"
        relative = "uploads/meta-delivery/" + filename
        api_path = "/contents/" + urllib.parse.quote(relative)
        blob_sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        existing = _github("GET", api_path, token)
        if existing:
            if existing.get("sha") != blob_sha:
                raise RuntimeError("Different file already occupies deterministic delivery path.")
            head = _github("GET", "/git/ref/heads/main", token)["object"]["sha"]
            commit_sha = head
        else:
            result = _github("PUT", api_path, token, {
                "message": "Stage quality-optimized Meta Reel delivery for " + req["id"],
                "branch": "main",
                "content": base64.b64encode(raw).decode("ascii")
            })
            commit_sha = result["commit"]["sha"]
        url = "https://raw.githubusercontent.com/" + REPO + "/" + commit_sha + "/" + relative
        _public_ready(url, len(raw))
        print("META_QUALITY_READY 1080x1920 GOP~2sec bitrate_target=5Mbps "
              "delivery_sha256=" + sha256 + " source_sha256=" + req["sha256"])
        return url, len(raw), sha256
