#!/usr/bin/env python3
"""Generate one Cloudflare free-plan mascot still and submit to existing Wan2.2 HF Space. No paid fallback."""
import base64,json,os,pathlib,subprocess,urllib.request,urllib.error
out=pathlib.Path("out/airfryer-motion");out.mkdir(parents=True,exist_ok=True)
if os.getenv("CLOUDFLARE_WORKERS_FREE_CONFIRMED")!="true":raise SystemExit("Workers Free not confirmed: no generation")
account=os.environ["CLOUDFLARE_ACCOUNT_ID"]; token=os.environ["CLOUDFLARE_AI_TOKEN"]
url=f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/black-forest-labs/flux-1-schnell"
prompt=("ONE original stylized 3D animated-movie still of a cute cream-colored air fryer character, "
"big expressive warm brown eyes, a smiling mouth, two small arms and two short legs, "
"standing in a bright warm modern kitchen, entire body visible, frontal view, room to wave both arms, "
"single coherent shot, locked camera, no collage, no text, no logo.")
req=urllib.request.Request(url,data=json.dumps({"prompt":prompt,"steps":4}).encode(),method="POST",
headers={"Authorization":"Bearer "+token,"Content-Type":"application/json","User-Agent":"SmartChoice365-Video/1.0"})
try:
 with urllib.request.urlopen(req,timeout=90) as r:data=json.load(r)
except urllib.error.HTTPError as e:raise SystemExit(f"Cloudflare HTTP {e.code}, no retries")
raw=base64.b64decode((data.get("result") or {}).get("image",""),validate=True)
if not data.get("success") or not raw.startswith(bytes.fromhex("ffd8ff")):raise SystemExit("No JPEG image returned")
source=out/"airfryer_character.jpg";source.write_bytes(raw)
motion=("Use the supplied reference image as the exact first frame. Preserve the identical cute cream "
"air fryer character, its face, arms, legs, proportions, and kitchen background throughout. "
"The character blinks both eyes once, then gently waves both existing arms with a happy smile. "
"Subtle body bounce, natural smooth 3D animation. Stationary camera. No extra limbs, "
"no morphing, no camera zoom, no scene cuts, no new characters, no text.")
subprocess.run(["python","experiments/wan22_image_to_video.py","--image",str(source),"--prompt",motion,
"--out",str(out/"airfryer_true_motion.mp4")],check=True)
print("ANIMATED_VIDEO_PATH:",out/"airfryer_true_motion.mp4")
