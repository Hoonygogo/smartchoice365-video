#!/usr/bin/env python3
"""One-off read-only public Cloudflare QA for the 2026-11-23 coleslaw photo release."""
import datetime, io, json, pathlib, time, urllib.request
from PIL import Image
BASE="https://smartc365.com"
SLUG="crunchy-purple-cabbage-coleslaw"
OUT=pathlib.Path("artifacts/live-recipe-photo-verification/coleslaw-20261123.json")
OUT.parent.mkdir(parents=True,exist_ok=True)
images=[f"/assets/recipe-step-photos/{SLUG}/step-{n:02d}.jpg" for n in (3,4,5)]
def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"SmartMeals365-step-image-public-check/1.0","Cache-Control":"no-cache"})
    with urllib.request.urlopen(req,timeout=22) as res:return res.status,res.read(5_000_000)
results=[]
for attempt in range(1,7):
    checks=[]
    for lang in ("ko","en"):
        url=f"{BASE}/guides/smart-dinner-{SLUG}-{lang}?photo_release_check={attempt}"
        try:
            code,body=get(url);text=body.decode("utf-8","replace")
            missing=[im for im in images if im not in text]
            checks.append({"kind":"page","lang":lang,"url":url,"status":code,"missing":missing,"pass":code==200 and not missing})
        except Exception as e:checks.append({"kind":"page","lang":lang,"pass":False,"error":str(e)[:200]})
    for im in images:
        url=BASE+im+f"?photo_release_check={attempt}"
        try:
            code,body=get(url)
            with Image.open(io.BytesIO(body)) as i:size=i.size;fmt=i.format
            checks.append({"kind":"image","path":im,"status":code,"bytes":len(body),"width":size[0],"height":size[1],"format":fmt,
                "pass":code==200 and fmt=="JPEG" and size[0]>=1200 and size[1]>=800 and len(body)>100000})
        except Exception as e:checks.append({"kind":"image","path":im,"pass":False,"error":str(e)[:200]})
    results=checks
    if all(x["pass"] for x in checks):break
    if attempt<6:time.sleep(8)
receipt={"checkedAtUTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),"slug":SLUG,
 "attempts":attempt,"publicVerified":all(x["pass"] for x in results),"results":results}
OUT.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"publicVerified":receipt["publicVerified"],"attempts":attempt,"results":results},ensure_ascii=False))
if not receipt["publicVerified"]:raise SystemExit("Not all live image and recipe URLs verified")
