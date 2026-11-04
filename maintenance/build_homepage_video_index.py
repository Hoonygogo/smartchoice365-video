#!/usr/bin/env python3
"""Free, public, verified video-format index for the Smart Choice 365 homepage.

Run on GitHub Actions when receipts change, and on a scheduled safety refresh.
The website uses this only to classify videos, never to invent publication.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "publications" / "homepage-video-index.json"
CHANNEL = "UC4DzAW-Hbd45bIECwGV7-uA"
VID = re.compile(r"^[A-Za-z0-9_-]{11}$")
HISTORICAL_DELETED = {"A59XedFBLxs", "FMdhtInQdPE", "UJ-azoT4vso",
                      "JgKqCXIvbKI", "4c82S22m69Y"}

def verified(item):
    return (isinstance(item, dict) and item.get("status") == "published_verified"
            and item.get("privacy") == "public"
            and item.get("processing_status") == "succeeded"
            and item.get("channel_id") == CHANNEL
            and isinstance(item.get("video_id"), str)
            and bool(VID.fullmatch(item["video_id"])))

def classify(item, root=ROOT):
    """Only use uploader-confirmed format, explicit Shorts URL, or request metadata."""
    fmt = item.get("format")
    if fmt not in ("shorts", "video"):
        request_id = str(item.get("id") or "")
        if re.fullmatch(r"[a-z0-9-]+", request_id):
            for parent in ("publications/requests", "requests"):
                path = root / parent / (request_id + ".json")
                if path.is_file():
                    try:
                        request_fmt = json.loads(path.read_text(encoding="utf-8")).get("video_format")
                        if request_fmt in ("shorts", "video"):
                            fmt = request_fmt
                            break
                    except (ValueError, OSError):
                        pass
    if fmt not in ("shorts", "video"):
        url = str(item.get("url") or "")
        title = str(item.get("title") or "")
        if "/shorts/" in url or re.search(r"#shorts\b|#쇼츠", title, re.I):
            fmt = "shorts"
    # A YouTube watch?v= link alone does NOT prove Full video; Shorts can use it.
    if fmt not in ("shorts", "video"):
        return None
    result = {"id": item["video_id"], "format": fmt}
    language = item.get("language")
    if language in ("ko", "en"):
        result["lang"] = language
    return result

def build(root=ROOT):
    files = sorted((root / "publications" / "receipts").glob("*-youtube.json"))
    receipts = []
    removed = set(HISTORICAL_DELETED)
    for path in files:
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(item, dict):
            continue
        receipts.append(item)
        cleanup = item.get("old_video_cleanup")
        if (isinstance(cleanup, dict) and cleanup.get("status") == "deleted_verified"
                and isinstance(cleanup.get("video_id"), str)):
            removed.add(cleanup["video_id"])
    by_id = {}
    for item in receipts:
        if not verified(item) or item["video_id"] in removed:
            continue
        entry = classify(item, root)
        if entry:
            # Prefer entries with an explicit language over legacy incomplete receipts.
            current = by_id.get(entry["id"])
            if current is None or ("lang" not in current and "lang" in entry):
                by_id[entry["id"]] = entry
    return {"version": 1, "channelId": CHANNEL,
            "videos": sorted(by_id.values(), key=lambda x: x["id"])}

if __name__ == "__main__":
    result = build()
    if not result["videos"]:
        raise SystemExit("No verified and classified public videos; retaining old index")
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Verified public video format index:", len(result["videos"]))
