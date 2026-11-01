#!/usr/bin/env python3
"""One-shot ice-maker editorial image. Cloudflare Workers AI free only; no retries."""
import os, json, base64, hashlib, urllib.request, urllib.error, pathlib
assert os.environ.get("CF_FREE")=="true", "Workers Free confirmation is required"
assert os.environ.get("CF_ACCOUNT") and os.environ.get("CF_TOKEN"), "Cloudflare AI credentials missing"
prompt=("One original premium photorealistic editorial lifestyle photograph for an Australian home-shopping advice article. "
"A sleek unbranded compact countertop ice maker in a beautiful bright coastal Australian kitchen on a sunny summer afternoon, "
"transparent glass filled with chunky bullet-shaped ice cubes, fresh lemon and mint, soft dappled sunshine, natural textures, "
"beautiful editorial composition, realistic appliance shape and proportions, complete machine visible with generous margins, "
"eye-level 16:9 horizontal frame, warm light, sophisticated styling. One single coherent scene. "
"No logos, no text, no typography, no price labels, no collage, no people, no watermark. "
"Illustrative scene, not a photograph of any particular product model.")
url="https://api.cloudflare.com/client/v4/accounts/"+os.environ["CF_ACCOUNT"]+"/ai/run/@cf/black-forest-labs/flux-1-schnell"
req=urllib.request.Request(url,data=json.dumps({"prompt":prompt,"steps":4}).encode(),headers={"Authorization":"Bearer "+os.environ["CF_TOKEN"],"Content-Type":"application/json","User-Agent":"SmartChoice365-IceMaker-FreeTest/1.0"},method="POST")
try:
    with urllib.request.urlopen(req,timeout=80) as r: payload=json.load(r)
except urllib.error.HTTPError as e:
    raise SystemExit("Cloudflare Workers AI HTTP "+str(e.code)+"; no retry or paid fallback") from None
image=(payload.get("result") or {}).get("image")
if payload.get("success") is not True or not isinstance(image,str):raise SystemExit("No supported image returned; no retry")
raw=base64.b64decode(image,validate=True)
if raw[:3]==bytes.fromhex("ffd8ff"): ext="jpg"
elif raw[:8]==bytes.fromhex("89504e470d0a1a0a"):ext="png"
else:raise SystemExit("Cloudflare response was not a JPEG or PNG")
if len(raw)<20000 or len(raw)>8000000:raise SystemExit("Unexpected image byte size")
out=pathlib.Path("experiments/ice-maker-ai");out.mkdir(parents=True,exist_ok=True)
(out/"hero-2026-11-01.b64").write_text(base64.b64encode(raw).decode("ascii"))
metadata={"model":"@cf/black-forest-labs/flux-1-schnell","topic":"Do You Really Need an Ice Maker This Australian Summer?","prompt":prompt,"mimeType":"image/"+("jpeg" if ext=="jpg" else "png"),"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),"freeConfirmed":True,"attempts":1,"humanReviewed":False,"usageApproved":False}
(out/"hero-2026-11-01.json").write_text(json.dumps(metadata,indent=2)+"\n")
print("WORKERS_AI_SUCCESS format:",ext,"bytes:",len(raw),"sha256:",metadata["sha256"])
