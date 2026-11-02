#!/usr/bin/env python3
"""Build and reuse a fixed RUA 4.5-second official ending from the approved master.

Runs with standard ffmpeg in free GitHub Actions; does not publish anything.
The precise original exported MP4 is backed up separately in the owner's
ChatGPT Library /SmartChoice365/RUA/. This is a faithful excerpt from the
already committed original Korean RUA video, not a byte-for-byte copy
of that separately rendered export.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "uploads/SmartChoice365_RUA_EP00_20261102.mp4"
MASTER_SHA256 = "5f7f4cd01c23c2bf9f7869ac4a6850e1825e7e515e80994b975bf2689c223dcf"
OUTRO = ROOT / "assets/rua/official-outro.mp4"
MANIFEST = ROOT / "assets/rua/official-outro.json"

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(args):
    subprocess.run(args, check=True)

def probe(path):
    data = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path)
    ]))
    videos = [x for x in data["streams"] if x.get("codec_type") == "video"]
    audios = [x for x in data["streams"] if x.get("codec_type") == "audio"]
    if len(videos) != 1 or len(audios) != 1:
        raise RuntimeError("Expected one video and one audio stream.")
    video, audio = videos[0], audios[0]
    if (video.get("width"), video.get("height")) != (720, 1280):
        raise RuntimeError("RUA must remain 720x1280 portrait.")
    if video.get("codec_name") != "h264" or audio.get("codec_name") != "aac":
        raise RuntimeError("Expected H.264/AAC.")
    return float(data["format"]["duration"])

def build():
    if not MASTER.is_file() or sha256(MASTER) != MASTER_SHA256:
        raise RuntimeError("Approved source master hash mismatch.")
    if not 9.9 <= probe(MASTER) <= 10.2:
        raise RuntimeError("Unexpected master clip duration.")
    OUTRO.parent.mkdir(parents=True, exist_ok=True)
    if not OUTRO.exists():
        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", "5.5", "-i", str(MASTER), "-t", "4.5",
            "-map", "0:v:0", "-map", "0:a:0",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", str(OUTRO)
        ])
    duration = probe(OUTRO)
    if not 4.45 <= duration <= 4.65:
        raise RuntimeError("Unexpected official outro duration.")
    digest = sha256(OUTRO)
    if MANIFEST.exists():
        recorded = json.loads(MANIFEST.read_text(encoding="utf-8"))
        if digest != recorded.get("sha256"):
            raise RuntimeError("Official outro changed from the recorded copy; refusing to use.")
    else:
        MANIFEST.write_text(json.dumps({
            "asset": "assets/rua/official-outro.mp4",
            "derived_from": "uploads/SmartChoice365_RUA_EP00_20261102.mp4",
            "source_sha256": MASTER_SHA256,
            "extraction_start_seconds": 5.5,
            "extraction_duration_seconds": 4.5,
            "video_duration_seconds": duration,
            "sha256": digest,
            "meaning": "Original RUA voice and animated content, re-extracted and encoded for durable GitHub reuse",
            "exact_original_export_backup": "/SmartChoice365/RUA/RUA_Signature_Outro_5p5_to_10s_Original_Audio.mp4",
            "language": "reuse for Korean and English RUA Shorts"
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("OFFICIAL_OUTRO_READY", str(OUTRO.relative_to(ROOT)), digest, duration)

def append(clip_name):
    clip = (ROOT / clip_name).resolve()
    permitted = (ROOT / "uploads/rua-comedy").resolve()
    if not clip.is_relative_to(permitted) or clip.suffix.lower() != ".mp4" or not clip.is_file():
        raise RuntimeError("Source must be an existing uploads/rua-comedy/*.mp4 file.")
    duration = probe(clip)
    if not 9.7 <= duration <= 10.3:
        raise RuntimeError("Comedy clip must be about 10 seconds; no auto-trimming.")
    build()
    result = ROOT / "renders/rua" / (clip.stem + "_with_official_outro.mp4")
    result.parent.mkdir(parents=True, exist_ok=True)
    if result.exists():
        raise RuntimeError("Output already exists. Never overwrite an approved render.")
    filter_graph = (
        "[0:v]fps=24,scale=720:1280:flags=lanczos,setsar=1,setpts=PTS-STARTPTS[v0];"
        "[1:v]fps=24,scale=720:1280:flags=lanczos,setsar=1,setpts=PTS-STARTPTS[v1];"
        "[0:a]aresample=async=1:first_pts=0,asetpts=PTS-STARTPTS[a0];"
        "[1:a]aresample=async=1:first_pts=0,asetpts=PTS-STARTPTS[a1];"
        "[v0][v1]concat=n=2:v=1:a=0[v];"
        "[a0][a1]concat=n=2:v=0:a=1[a]"
    )
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(clip), "-i", str(OUTRO),
        "-filter_complex", filter_graph, "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", str(result)
    ])
    final_duration = probe(result)
    if not duration + 4.25 <= final_duration <= duration + 4.75:
        raise RuntimeError("Wrong joined video duration.")
    print("RUA_SHORT_RENDERED", str(result.relative_to(ROOT)), final_duration, sha256(result))
    print("REVIEW_REQUIRED_BEFORE_SOCIAL_PUBLICATION")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["build", "append"])
    parser.add_argument("clip", nargs="?")
    args = parser.parse_args()
    if args.action == "build":
        build()
    else:
        if not args.clip:
            parser.error("append requires clip path")
        append(args.clip)
