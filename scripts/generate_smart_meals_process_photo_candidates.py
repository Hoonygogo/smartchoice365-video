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
COUNTERTOP_SET_ID = "smart-meals-ivory-quartz-countertop-v2"
# Use only the surface MATERIAL from input image 0. The reference is a texture
# guide, NOT a scene to reconstruct. Every dish must dominate its photograph.
COUNTERTOP_PROMPT = (
    "LOCK ONLY THE VISIBLE COUNTERTOP MATERIAL: warm pale ivory quartz, subtle tiny beige-grey speckles, "
    "matte satin finish, matching input image 0 in colour and fine-grain pattern. "
    "The countertop is only a small supporting surface beneath the food or cutting board. "
    "NO visible kitchen room, backsplash, cabinets, windows, full cooker, house plants, or background decor. "
    "NO overhead wide kitchen establishing shots. For stove steps a tight cooking-pan close-up is correct: "
    "countertop may be invisible. Photograph the actual food, not the setting. "
)

BASE = pathlib.Path(__file__).resolve().parents[1]
REQUESTS = BASE / "requests/recipe-step-photo"
OUTPUT = BASE / "artifacts/recipe-step-photo"
COUNTERTOP_REFERENCE = BASE / "assets/reference/smart-meals-countertop-quartz-v2.jpg"
# Real binary reference input is mandatory. Model requires every input image <512x512.
COUNTERTOP_REFERENCE_SHA256 = "8a30f68180e58f47cd9aacbd6fde20e72a8c01a9ba3273ada3b6c18250473771"

def read_countertop_reference():
    if not COUNTERTOP_REFERENCE.is_file():
        raise FileNotFoundError("Fixed kitchen image missing; refusing to create mismatched recipe photos")
    raw = COUNTERTOP_REFERENCE.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != COUNTERTOP_REFERENCE_SHA256:
        raise ValueError("Fixed kitchen reference SHA256 changed; refusing silently substituted background")
    with Image.open(io.BytesIO(raw)) as image:
        size = image.size
        if image.format != "JPEG" or size[0] >= 512 or size[1] >= 512:
            raise ValueError("Fixed reference must be a JPEG smaller than 512 pixels in both dimensions")
    return raw, size


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
    if len(stages) < 1 or len(stages) > 9 or len({x["step"] for x in stages}) != len(stages):
        raise ValueError("One-off batch must have 1–9 distinct photographs")
    report = {
        "schemaVersion": 1, "slug": slug, "recipeName": request["title"],
        "source": "Original official Smart Meals bilingual recipe method",
        "model": MODEL, "reviewed": False, "published": False,
        "paidFallback": False, "attemptLimitPerStage": 1,
        "requestRevision": request.get("requestRevision", 1),
        "countertopSet": COUNTERTOP_SET_ID,
        "referenceImageConditioningUsed": False,
        "referenceImagePath": str(COUNTERTOP_REFERENCE.relative_to(BASE)),
        "referenceRole": "countertop_material_only_not_room_layout",
        "compositionRule": "food_fills_75_to_90_percent_of_frame_with_natural_countertop_contact_shadow",
        "referenceSha256": COUNTERTOP_REFERENCE_SHA256,
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
    reference_bytes, reference_dims = read_countertop_reference()
    report["referenceDimensions"] = list(reference_dims)
    endpoint = f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{MODEL}"
    full_ingredients = "; ".join(request["ingredients"])
    ordered_method = " ".join(f"{i+1}. {s}" for i,s in enumerate(request["fullMethod"]))
    for item in stages:
        step = item["step"]
        # Keep the generative prompt under established Cloudflare FLUX Schnell input limit.
        # Original full bilingual method stays in request JSON for editor inspection.
        if not isinstance(step, int) or step < 0 or step > len(request["fullMethod"]):
            raise ValueError("Invalid recipe step index")
        is_hero = step == 0
        is_final = step == len(request["fullMethod"])
        target_method = request["fullMethod"][-1] if is_hero else request["fullMethod"][step-1]
        prefix = (
            "Extreme food-first authentic close-up candid cooking photograph. "
            "The actual food and cooking action fill 75–90 percent of the image; "
            "show only a narrow band of quartz counter where needed to prove grounding. "
            "Use image 0 ONLY for counter material colour and tiny speckled texture, NOT its camera view. "
            + COUNTERTOP_PROMPT
            + " Precisely show this stage: " + item["scene"]
            + " Every vessel or finished plate has visible genuine contact with its supporting surface, "
              "never appears suspended or floating. Edible imperfect home-cooked textures, natural light, "
              "neutral colour, no plastic gloss, no odd tools or foods, no unrelated props, no people or captions."
        )
        if len(prefix) > 1650:
            required = ("Food dominates 75–90% of frame, food is sharp and realistically grounded. "
                        "Use input image 0 only for subtle ivory speckled quartz counter material. "
                        "No kitchen room, cabinets, wall tiles or background staging. "
                        "Exact cooking stage: " + item["scene"])
            if len(required) > 1650:
                raise ValueError("Stage scene too long; shorten without deleting food and countertop requirements")
            prefix = required
        result = {"step": step, "status": "not_generated", "reviewed": False, "published": False}
        try:
            boundary = "----SC365ProcessPhoto" + hashlib.sha256(os.urandom(16)).hexdigest()[:16]
            payload = b""
            for key, value in {"prompt": prefix, "width": (1536 if (is_final or is_hero or slug in ("korean-kimchi-fried-rice", "crunchy-purple-cabbage-coleslaw", "iced-matcha-milk-latte", "iced-caramel-coffee-cream", "cucumber-tomato-feta-olive-salad")) else 1024), "height": 1024}.items():
                payload += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}\r\n").encode("utf-8")
            payload += (f"--{boundary}\r\n"
                        'Content-Disposition: form-data; name="input_image_0"; filename="countertop-material-v2.jpg"\r\n'
                        "Content-Type: image/jpeg\r\n\r\n").encode("utf-8")
            payload += reference_bytes + b"\r\n"
            payload += (f"--{boundary}--\r\n").encode("utf-8")
            report["referenceImageConditioningUsed"] = True
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
            photo_name = "hero.jpg" if is_hero else "step-%02d.jpg" % step
            out_dir.mkdir(parents=True, exist_ok=True)
            output = out_dir / photo_name
            converted.save(output, "JPEG", quality=88, optimize=True)
            binary = output.read_bytes()
            result.update(status="candidate_needs_actual_visual_review", role="hero" if is_hero else ("final" if is_final else "step"),
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
