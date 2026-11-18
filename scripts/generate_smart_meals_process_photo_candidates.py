#!/usr/bin/env python3
"""One-off FREE-only, editor-unapproved Smart Meals recipe process photo candidates.
No user reviews, no production publication, no automatic acceptance.
"""
import base64
import datetime
import hashlib
import io
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

from PIL import Image

MODEL = "@cf/black-forest-labs/flux-2-klein-4b"
BASE = pathlib.Path(__file__).resolve().parents[1]
REQUESTS = BASE / "requests/recipe-step-photo"
OUTPUT = BASE / "artifacts/recipe-step-photo"

def save_result(slug, obj):
    target = OUTPUT / slug / "generation-report.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def generate(request_path):
    request = json.loads(request_path.read_text(encoding="utf-8"))
    slug = request["slug"]
    if request.get("schemaVersion") != 1 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("Invalid recipe request")
    if request_path.name != slug + ".json":
        raise ValueError("Request filename does not match recipe slug")
    stages = request["stages"]
    if len(stages) < 1 or len(stages) > 3 or len({x["step"] for x in stages}) != len(stages):
        raise ValueError("One-off batch must have 1–3 distinct process stages")
    report = {
        "schemaVersion": 1, "slug": slug, "recipeName": request["title"],
        "source": "Original official Smart Meals bilingual recipe method",
        "model": MODEL, "reviewed": False, "published": False,
        "paidFallback": False, "attemptLimitPerStage": 1,
        "requestRevision": request.get("requestRevision", 1),
        "generatedAtUTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "stages": []
    }
    out_dir = OUTPUT / slug
    previous = out_dir / "generation-report.json"
    if previous.exists():
        old = json.loads(previous.read_text(encoding="utf-8"))
        if old.get("requestRevision", 1) >= request.get("requestRevision", 1):
            print("ALREADY_PROCESSED_NO_RETRY", slug)
            return
    if os.getenv("CLOUDFLARE_WORKERS_FREE_CONFIRMED") != "true":
        report["status"] = "free_plan_not_confirmed_no_requests"
        save_result(slug, report)
        return
    account = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
    token = os.getenv("CLOUDFLARE_AI_TOKEN", "").strip()
    if not account or not token:
        report["status"] = "credentials_unavailable_no_requests"
        save_result(slug, report)
        return
    endpoint = f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{MODEL}"
    full_ingredients = "; ".join(request["ingredients"])
    ordered_method = " ".join(f"{i+1}. {s}" for i,s in enumerate(request["fullMethod"]))
    for item in stages:
        step = item["step"]
        if not isinstance(step, int) or step < 1 or step > len(request["fullMethod"]):
            raise ValueError("Out of range recipe stage")
        # Keep the generative prompt under established Cloudflare FLUX Schnell input limit.
        # Original full bilingual method stays in request JSON for editor inspection.
        prefix = (
            f"Photorealistic close-up food preparation photograph. Dish: {request['title']}. "
            f"Step {step} ONLY: {request['fullMethod'][step-1]}. "
            f"Scene: {item['scene']}. "
            f"Allowed measured ingredients: {full_ingredients}. "
            "Natural Australian home kitchen, stable real work surface, actual gravity and shadows, "
            "authentic food textures, small natural imperfections and honest daylight. "
            "No people or body; optional tiny hand edge only if required. "
            "No unlisted ingredients, text, captions, collage, floating food or equipment, fake CGI finish."
        )
        if len(prefix) > 1400:
            prefix = prefix[:1400].rsplit(" ", 1)[0]
        result = {"step": step, "status": "not_generated", "reviewed": False, "published": False}
        try:
            boundary = "----SC365ProcessPhoto" + hashlib.sha256(os.urandom(16)).hexdigest()[:16]
            payload = b""
            for key, value in {"prompt": prefix, "width": 1024, "height": 1024}.items():
                payload += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}\r\n").encode("utf-8")
            payload += (f"--{boundary}--\r\n").encode("utf-8")
            http_req = urllib.request.Request(endpoint, data=payload, method="POST", headers={
                "Authorization": "Bearer " + token,
                "Content-Type": "multipart/form-data; boundary=" + boundary,
                "User-Agent": "SmartMeals-Free-Process-Photo/1.1"
            })
            with urllib.request.urlopen(http_req, timeout=90) as response:
                body = json.load(response)
            encoded = (body.get("result") or {}).get("image")
            if body.get("success") is not True or not isinstance(encoded, str):
                raise ValueError("Image response missing")
            raw = base64.b64decode(encoded, validate=True)
            with Image.open(io.BytesIO(raw)) as src:
                src.verify()
            with Image.open(io.BytesIO(raw)) as src:
                width, height = src.size
                if min(width, height) < 768:
                    raise ValueError("Image size smaller than usable process-photo minimum")
                converted = src.convert("RGB")
            photo_name = "step-%02d.jpg" % step
            out_dir.mkdir(parents=True, exist_ok=True)
            output = out_dir / photo_name
            converted.save(output, "JPEG", quality=88, optimize=True)
            binary = output.read_bytes()
            result.update(status="candidate_needs_actual_visual_review",
                          path=str(output.relative_to(BASE)),
                          width=width, height=height, bytes=len(binary),
                          sha256=hashlib.sha256(binary).hexdigest())
        except urllib.error.HTTPError as exc:
            detail = exc.read(350).decode("utf-8", "replace")
            result.update(status="cloudflare_429_free_quota_or_rate" if exc.code == 429 else "cloudflare_http_"+str(exc.code), errorDetail=detail[:300])
            report["stages"].append(result)
            if exc.code == 429:
                break
        except (urllib.error.URLError, TimeoutError, ValueError, OSError, TypeError) as exc:
            result.update(status="candidate_error_"+type(exc).__name__)
        else:
            report["stages"].append(result)
            continue
        if result not in report["stages"]:
            report["stages"].append(result)
    report["status"] = "candidates_created_unreviewed" if any(
        x["status"] == "candidate_needs_actual_visual_review" for x in report["stages"]
    ) else "no_images_created"
    save_result(slug, report)
    print("RECIPE_PHOTO_CANDIDATES", json.dumps({
        "slug": slug, "status": report["status"],
        "stages": [{"step": x["step"], "status": x["status"]} for x in report["stages"]]
    }))

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/generate_smart_meals_process_photo_candidates.py requests/recipe-step-photo/<slug>.json")
    request_path = pathlib.Path(sys.argv[1]).resolve()
    if REQUESTS.resolve() not in request_path.parents:
        raise ValueError("Request must be in designated photo folder")
    generate(request_path)

if __name__ == "__main__":
    main()
