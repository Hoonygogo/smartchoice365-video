#!/usr/bin/env python3
"""Check both canonical language editions and actual released photo bytes, not just a git commit."""
import datetime as dt
import io
import json
import os
import pathlib
import time
import urllib.error
import urllib.request
from PIL import Image

BASE = "https://smartc365.com"
SLUGS = ["avocado-boiled-egg-toast", "raspberry-lime-lemonade", "indian-butter-chicken", "cinnamon-apple-oat-porridge"]
STAGES = {"avocado-boiled-egg-toast": [4,6,7], "raspberry-lime-lemonade": [2,3,5], "indian-butter-chicken": [3,4,5,8], "cinnamon-apple-oat-porridge": [2,3,6]}
OUT = pathlib.Path("artifacts/live-recipe-photo-verification/latest.json")
OUT.parent.mkdir(parents=True, exist_ok=True)

def get(url):
    req = urllib.request.Request(url,headers={"User-Agent":"SmartMeals365-live-release-audit/1.0","Cache-Control":"no-cache"})
    with urllib.request.urlopen(req, timeout=28) as resp:
        return resp.status, resp.read(5_000_000)

rows=[]
for attempt in range(1,7):
    rows=[]
    for slug in SLUGS:
        paths=[f"/assets/recipe-step-photos/{slug}/hero.jpg"]+[f"/assets/recipe-step-photos/{slug}/step-{n:02d}.jpg" for n in STAGES[slug]]
        row={"slug":slug,"pages":[],"assets":[]}
        for lang in ("ko","en"):
            url=f"{BASE}/guides/smart-dinner-{slug}-{lang}?photo_audit={attempt}"
            try:
                status,raw=get(url)
                html=raw.decode("utf-8","replace")
                missing=[x for x in paths if x not in html]
                row["pages"].append({"lang":lang,"http":status,"bytes":len(raw),"missing":missing,"pass":status==200 and not missing})
            except Exception as exc:
                row["pages"].append({"lang":lang,"pass":False,"error":str(exc)[:300]})
        for p in paths:
            try:
                status,raw=get(BASE+p+"?photo_audit="+str(attempt))
                with Image.open(io.BytesIO(raw)) as pic:
                    width,height=pic.size
                row["assets"].append({"path":p,"http":status,"bytes":len(raw),"width":width,"height":height,"pass":status==200 and width>= (1400 if p.endswith(("hero.jpg",f"step-{max(STAGES[slug]):02d}.jpg")) else 900)})
            except Exception as exc:
                row["assets"].append({"path":p,"pass":False,"error":str(exc)[:300]})
        row["pass"]=all(p["pass"] for p in row["pages"]+row["assets"])
        rows.append(row)
    if all(x["pass"] for x in rows):
        break
    if attempt<6:time.sleep(15)
report={"checkedAtUTC":dt.datetime.now(dt.timezone.utc).isoformat(),"attempt":attempt,"allLiveVerified":all(x["pass"] for x in rows),"entries":rows}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(report,ensure_ascii=False,indent=2))
if not report["allLiveVerified"]:raise SystemExit("Cloudflare public pages not verified")
