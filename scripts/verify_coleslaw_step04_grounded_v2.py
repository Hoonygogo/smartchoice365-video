#!/usr/bin/env python3
"""One-time read-only production verification of coleslaw step-4 physical realism image replacement."""
import datetime as dt, hashlib, io, json, pathlib, time, urllib.request
from PIL import Image
BASE="https://smartc365.com"
SLUG="crunchy-purple-cabbage-coleslaw"
REL=f"/assets/recipe-step-photos/{SLUG}/step-04.jpg"
QUERY="?v=20261123-grounded-v2"
EXPECTED_SHA256="91ec2e3fce3389fe3e2d3f49ea3c230f4fab73b6a28b78524c084ec24782d6c4"
OUT=pathlib.Path("artifacts/live-recipe-photo-verification/coleslaw-step04-grounded-v2.json")
OUT.parent.mkdir(parents=True,exist_ok=True)
def get(url):
    request=urllib.request.Request(url,headers={"User-Agent":"SmartMeals365-photo-grounding-qa/1.0","Cache-Control":"no-cache"})
    with urllib.request.urlopen(request,timeout=22) as res:return res.status,res.read(6000000)
report=None
for attempt in range(1,9):
    checks=[]
    for lang in ("ko","en"):
        url=f"{BASE}/guides/smart-dinner-{SLUG}-{lang}?release_audit={attempt}"
        try:
            code,raw=get(url)
            html=raw.decode("utf-8","replace")
            exact_src=f'src="{REL}{QUERY}"'
            exact_schema=f"{BASE}{REL}{QUERY}"
            checks.append({"kind":"page","language":lang,"http":code,"hasVersionedSource":exact_src in html,
                "hasVersionedStepSchema":exact_schema in html,
                "pass":code==200 and exact_src in html and exact_schema in html})
        except Exception as e:
            checks.append({"kind":"page","language":lang,"pass":False,"error":str(e)[:240]})
    try:
        code,b=get(BASE+REL+QUERY)
        actual=hashlib.sha256(b).hexdigest()
        with Image.open(io.BytesIO(b)) as img:dimensions=img.size;kind=img.format
        checks.append({"kind":"image","path":REL+QUERY,"http":code,"format":kind,
            "width":dimensions[0],"height":dimensions[1],"bytes":len(b),
            "sha256":actual,"expectedSha256":EXPECTED_SHA256,
            "pass":code==200 and actual==EXPECTED_SHA256 and kind=="JPEG"
              and dimensions[0]>=1200 and dimensions[1]>=800 and len(b)>100000})
    except Exception as e:
        checks.append({"kind":"image","pass":False,"error":str(e)[:240]})
    ok=all(x["pass"] for x in checks)
    report={"checkedAtUTC":dt.datetime.now(dt.timezone.utc).isoformat(),
        "attempt":attempt,"publicVerified":ok,"slug":SLUG,"step":4,"results":checks}
    if ok:break
    if attempt<8:time.sleep(12)
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,ensure_ascii=False))
if not report["publicVerified"]:raise SystemExit("Live coleslaw image replacement not verified")
