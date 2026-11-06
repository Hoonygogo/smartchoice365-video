#!/usr/bin/env python3
"""One-shot, free-only image pipeline pilot. Does not touch daily publishing."""
import base64
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import urllib.request
import urllib.error
from PIL import Image

ID = "bedroom-fan-placement-2026-11-06"
ROOT = Path("artifacts/image-pilots")
OUT = ROOT / (ID + ".jpg")
META = ROOT / (ID + ".json")
PROMPT = (
    "Photorealistic editorial lifestyle photography, wide horizontal framing, an airy Australian "
    "bedroom in warm natural morning sunlight. One completely generic simple pedestal fan with a "
    "clean, unmarked circular centre cap, its plain smooth rear motor casing angled slightly away "
    "from the viewer, positioned beside a bed and directing airflow across the sleeping area. "
    "Show the entire believable fan including stable base. A lightly fluttering plain curtain "
    "indicates a summer breeze. Beautiful inviting home photograph with realistic physical "
    "proportions, gentle soft light and uncluttered composition. No recognizable retail model, "
    "NO letters, NO symbols, NO digits, NO text, NO fake brand markings, NO logos, NO labels, "
    "NO digital displays, NO control labels, NO captions, NO graphics, NO arrows, NO split screen. "
    "This is only a generic illustrative interior scene, not an actual product photo."
)

def main():
    if META.exists() or OUT.exists():
        print("ALREADY_PROCESSED_NO_RETRY", ID)
        return
    ROOT.mkdir(parents=True, exist_ok=True)
    result = {"id": ID, "model": "@cf/black-forest-labs/flux-1-schnell",
              "paidFallback": False, "attemptLimit": 1,
              "timestampUTC": dt.datetime.now(dt.timezone.utc).isoformat()}
    if os.getenv("CLOUDFLARE_WORKERS_FREE_CONFIRMED") != "true":
        result.update(status="fallback", reason="free_tier_not_confirmed")
    elif not os.getenv("CLOUDFLARE_ACCOUNT_ID") or not os.getenv("CLOUDFLARE_AI_TOKEN"):
        result.update(status="fallback", reason="credentials_missing")
    else:
        url = ("https://api.cloudflare.com/client/v4/accounts/"
               + os.environ["CLOUDFLARE_ACCOUNT_ID"]
               + "/ai/run/@cf/black-forest-labs/flux-1-schnell")
        req = urllib.request.Request(url,
            data=json.dumps({"prompt": PROMPT, "steps": 4}).encode(),
            headers={"Authorization": "Bearer " + os.environ["CLOUDFLARE_AI_TOKEN"],
                     "Content-Type": "application/json"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=80) as response:
                data = json.load(response)
            b64 = (data.get("result") or {}).get("image")
            if data.get("success") is not True or not b64:
                raise ValueError("no_image")
            raw = base64.b64decode(b64, validate=True)
            if raw[:3] != bytes.fromhex("ffd8ff") or not 20000 <= len(raw) <= 8000000:
                raise ValueError("invalid_jpeg")
            with Image.open(io.BytesIO(raw)) as image:
                image.verify()
            with Image.open(io.BytesIO(raw)) as image:
                width, height = image.size
            if min(width, height) < 768:
                raise ValueError("small_image")
            OUT.write_bytes(raw)
            result.update(status="ready", imagePath=OUT.as_posix(),
                          sha256=hashlib.sha256(raw).hexdigest(),
                          imageBytes=len(raw), width=width, height=height,
                          usageApproved=False, visualReviewRequired=True)
        except urllib.error.HTTPError as exc:
            result.update(status="fallback", reason="http_"+str(exc.code))
        except Exception as exc:
            result.update(status="fallback", reason=type(exc).__name__)
    META.write_text(json.dumps(result, indent=2)+"\n")
    print("PILOT_RESULT", result["status"], result.get("reason","image_ready"))

if __name__ == "__main__":
    main()
