#!/usr/bin/env python3
"""Verify live bilingual iced matcha latte photos against exact published binary SHA-256."""
import datetime, hashlib, io, json, pathlib, time, urllib.request
from PIL import Image
BASE="https://smartc365.com"
SLUG="iced-matcha-milk-latte"
DIR=f"/assets/recipe-step-photos/{SLUG}"
EXPECTED={
 "hero.jpg":"f7411730cc5fb80933a10843fbcbcee5f0b571ab2853d5ab6d29de0da64008fc",
 "step-01.jpg":"c17a0896917f939c1fb95911140dfbb2f4e4ee68a219f102994a83a38fda2788",
 "step-02.jpg":"b5fdf5597fdfcf037092834ee93ea7f0008ceffc71b32c62563a2575cce944e2",
 "step-03.jpg":"7e6a3df95303aab280c8f97e5b75018977e9a687af0a5fde1fa2b10672ecc4e4",
 "step-04.jpg":"46b9f5a01d4c2ee23e2b53acbd5345db01dc5beb3f21980e0c90a3480c5231a2",
 "step-05.jpg":"85c1709510fda3727ebe99969d51b4df69ac66ab11d64a6848f38dd870b38cdc",
}
OUT=pathlib.Path("artifacts/live-recipe-photo-verification/matcha-latte-20261123.json")
OUT.parent.mkdir(parents=True,exist_ok=True)
def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"SmartMeals365-live-matcha-release-QA/1.0","Cache-Control":"no-cache"})
    with urllib.request.urlopen(req,timeout=25) as resp:return resp.status,resp.read(8_000_000)
for attempt in range(1,8):
    checks=[]
    for lang in ("ko","en"):
        url=f"{BASE}/guides/smart-dinner-{SLUG}-{lang}?photo_qa={attempt}"
        try:
            code,raw=get(url);h=raw.decode("utf-8","replace")
            missing=[name for name in EXPECT if name!="hero.jpg" and f'{DIR}/{name}' not in h]
            # The original site hero stays unchanged even when an optional new hero file is available.
            preserved="/assets/recipe-photos/iced-matcha-milk-latte.jpg" in h
            schema_all=all(f"{BASE}{DIR}/step-{i:02d}.jpg" in h for i in range(1,6))
            checks.append({"kind":"page","language":lang,"http":code,"missingStages":missing,
                "originalHeroPreserved":preserved,"schemaImageURLsFound":schema_all,
                "pass":code==200 and not missing and preserved and schema_all})
        except Exception as e:checks.append({"kind":"page","language":lang,"pass":False,"error":str(e)[:220]})
    for name,expected in EXPECT.items():
        url=f"{BASE}{DIR}/{name}?photo_qa={attempt}"
        try:
            code,raw=get(url);sha=hashlib.sha256(raw).hexdigest()
            with Image.open(io.BytesIO(raw)) as im:w,h=im.size;kind=im.format
            checks.append({"kind":"asset","name":name,"http":code,"width":w,"height":h,"bytes":len(raw),
                "format":kind,"sha256":sha,"hashVerified":sha==expected,
                "pass":code==200 and sha==expected and kind=="JPEG" and w==1536 and h==1024 and len(raw)>100000})
        except Exception as e:checks.append({"kind":"asset","name":name,"pass":False,"error":str(e)[:220]})
    passed=all(x["pass"] for x in checks)
    report={"checkedAtUTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "slug":SLUG,"attempt":attempt,"publicVerified":passed,"results":checks}
    if passed:break
    if attempt<7:time.sleep(12)
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,ensure_ascii=False,indent=2))
if not report["publicVerified"]:raise SystemExit("Matcha latte photos not fully visible on Cloudflare")
