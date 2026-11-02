#!/usr/bin/env python3
"""Validate and reuse the owner's approved RUA 10-second signature ending V2.

Runs with standard ffmpeg in free GitHub Actions; does not publish anything.
The approved V2 full video is archived in ChatGPT Library under
/SmartChoice365/RUA/RUA_Official_Signature_Outro_V2_10s.mp4.
Never reconstruct or substitute a previous outro; the repository media must match
its approved SHA256 before reuse.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
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
    """Only accept the owner's newly approved 10-second V2 video; never reconstruct V1."""
    if not OUTRO.is_file():
        raise RuntimeError(
            "Approved RUA V2 is saved in ChatGPT Library but its GitHub MP4 has not yet "
            "been synchronized. Upload the approved 10-second file as assets/rua/official-outro.mp4. "
            "Refusing to recreate or reuse the removed 4.5-second V1."
        )
    duration = probe(OUTRO)
    if not 9.9 <= duration <= 10.2:
        raise RuntimeError("Expected the approved 10-second RUA V2, not the old 4.5-second V1.")
    digest = sha256(OUTRO)
    approved_sha = "ae161a9dc3d34f705d67ca081cbb708d03e1a2778a4753e2a2ee413ce768b495"
    if digest != approved_sha:
        raise RuntimeError("Official RUA V2 SHA256 mismatch. Refusing to use an unapproved video.")
    if not MANIFEST.is_file():
        raise RuntimeError("Official RUA V2 manifest is missing.")
    recorded = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if recorded.get("sha256") != digest or recorded.get("video_duration_seconds") != 10.026667:
        raise RuntimeError("RUA V2 manifest does not match approved video.")
    print("OFFICIAL_OUTRO_V2_READY", str(OUTRO.relative_to(ROOT)), digest, duration)

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
    if not duration + 9.8 <= final_duration <= duration + 10.2:
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
