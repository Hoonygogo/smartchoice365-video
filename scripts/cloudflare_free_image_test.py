#!/usr/bin/env python3
"""One-shot Cloudflare Workers AI FLUX.1 schnell test. No retries or paid fallback."""
import base64,json,os,pathlib,urllib.request,urllib.error
url="https://api.cloudflare.com/client/v4/accounts/"+os.environ["CF_ACCOUNT"]+"/ai/run/@cf/black-forest-labs/flux-1-schnell"
prompt=("One original standalone high quality 3D stylized animated film still of a friendly tiny air fryer mascot, "
"expressive eyes and small waving arms, a bright modern Australian kitchen, soft cinematic lighting, "
"entire mascot visible, horizontal composition, no words, no brand labels, no collage, no multiple panels.")
req=urllib.request.Request(url,data=json.dumps({"prompt":prompt,"steps":4,"seed":365}).encode(),headers={
"Authorization":"Bearer "+os.environ["CF_TOKEN"],"Content-Type":"application/json",
"User-Agent":"SmartChoice365-AI-Test/1.0"},method="POST")
try:
    with urllib.request.urlopen(req,timeout=75) as r:
        payload=json.load(r)
except urllib.error.HTTPError as e:
    raise SystemExit("Cloudflare AI returned HTTP "+str(e.code)+"; no fallback or retry.") from None
image=(payload.get("result") or {}).get("image")
if not payload.get("success") or not isinstance(image,str):raise SystemExit("No image in Cloudflare response")
raw=base64.b64decode(image,validate=True)
if not raw.startswith(bytes.fromhex("ffd8ff")) and not raw.startswith(bytes.fromhex("89504e470d0a1a0a")):raise SystemExit("Not a verified JPEG or PNG")
p=pathlib.Path("out/cloudflare-ai/scene_01.jpg" if raw.startswith(bytes.fromhex("ffd8ff")) else "out/cloudflare-ai/scene_01.png")
p.parent.mkdir(parents=True,exist_ok=True)
p.write_bytes(raw)
print("Single independent AI scene generated:",len(raw),"bytes; file",p)
