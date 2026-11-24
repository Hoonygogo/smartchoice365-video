#!/usr/bin/env python3
"""Package six visually reviewed Cloudflare pineapple-coconut smoothie photographs and verify live KO/EN pages."""
from __future__ import annotations
import datetime as dt
import hashlib
import io
import json
import pathlib
import time
import urllib.request
import zipfile
from PIL import Image, ImageDraw, ImageOps

ROOT=pathlib.Path(__file__).resolve().parents[1]
SLUG="pineapple-coconut-smoothie"
PHOTOS=ROOT/"artifacts/recipe-step-photo"/SLUG
PUBLIC="https://smartc365.com"
PHOTO_ROOT=f"/assets/recipe-step-photos/{SLUG}"
HERO=f"/assets/recipe-photos/{SLUG}.jpg"
VERSION="?v=20261124-pineapple-photos-v2"
RECEIPT=ROOT/"artifacts/live-recipe-photo-verification/pineapple-coconut-smoothie-20261124.json"
FILES=["hero.jpg"]+[f"step-{n:02d}.jpg" for n in range(1,6)]
GIT_HASHES={
 "hero.jpg":"e9261a3b2ceae46a23c2389f550ea2ec86db6465",
 "step-01.jpg":"db2f91655944ca5b82d0711e74d9bcb649321062",
 "step-02.jpg":"45e7cbd49917f4e6e0704d5953ec6a44b3da6be8",
 "step-03.jpg":"d33bae0b379976f5d98a66d4ddc03e748faf765f",
 "step-04.jpg":"2154dffcb1299c555fb215cc833085c63cea2097",
 "step-05.jpg":"40e82f64aa8bb742b97e87751bdf4be252f8aeaa",
}
KO=["파인애플 코코넛 스무디 대표사진 두 잔","파인애플 껍질과 심을 제거하고 과육 300g을 작은 큐브로 손질",
    "무가당 코코넛밀크와 차가운 물을 깨끗한 믹서에 넣어 계량","파인애플과 코코넛밀크를 갈아 연노란 스무디로 만든 중간 과정",
    "믹서의 파인애플 코코넛 혼합물에 라임즙과 얼음을 더하기","파인애플 코코넛 스무디 두 잔 완성"]
EN=["Two finished pineapple coconut smoothies","Peeled cored pineapple chopped into small cubes",
    "Unsweetened coconut milk and cold water in an open blender","Smooth pineapple blended with coconut milk before lime and ice",
    "Add clean ice and lime juice to pineapple coconut blender mixture","Two finished glasses of pineapple coconut smoothie"]
def sha256(data): return hashlib.sha256(data).hexdigest()
def gitblob(data): return hashlib.sha1(f"blob {len(data)}".encode()+bytes([0])+data).hexdigest()

items=[];thumbs=[]
for idx,name in enumerate(FILES):
    data=(PHOTOS/name).read_bytes()
    if gitblob(data)!=GIT_HASHES[name]: raise RuntimeError("Unreviewed or replaced photo: "+name)
    if len(data)<100000: raise RuntimeError("Photo too small: "+name)
    with Image.open(io.BytesIO(data)) as im:
        if im.format!="JPEG" or im.size!=(1536,1024): raise RuntimeError("Bad photo resolution: "+name)
        thumbs.append(ImageOps.fit(im.convert("RGB"),(480,320),method=Image.Resampling.LANCZOS))
    items.append(dict(file=name,width=1536,height=1024,bytes=len(data),sha256=sha256(data),alt_ko=KO[idx],alt_en=EN[idx]))
if len({i["sha256"] for i in items})!=6: raise RuntimeError("Duplicate file detected")
contact=Image.new("RGB",(1500,750),"white");draw=ImageDraw.Draw(contact)
for idx,(name,thumb) in enumerate(zip(FILES,thumbs)):
    x=15+idx%3*495;y=15+idx//3*370
    contact.paste(thumb,(x,y));draw.text((x+5,y+328),name,fill=(20,20,20))
buf=io.BytesIO();contact.save(buf,"JPEG",quality=90,optimize=True)
contact_bytes=buf.getvalue()
(PHOTOS/"preview-contact-sheet.jpg").write_bytes(contact_bytes)
manifest=dict(recipe=SLUG,titleKo="파인애플 코코넛 스무디",titleEn="Pineapple Coconut Smoothie",
    servings=2, ingredients=["fresh pineapple 300 g","unsweetened coconut milk 200 ml","fresh lime juice 20 ml","clean ice cubes 120 g","cold drinking water 40 ml"],
    selectedRevisions={"hero":2,"step1":1,"step2":2,"step3":1,"step4":2,"step5":1},
    images=items, visuallyReviewed=True, processPhotoCount=5,
    siteCommit="6c1fa06da6bec6bf5ca024a9376b1d8aeae15cee")
(PHOTOS/"package-manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
bundle=PHOTOS/(SLUG+"-hero-and-5-steps.zip")
with zipfile.ZipFile(bundle,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for name in FILES: archive.write(PHOTOS/name,name)
    archive.writestr("preview-contact-sheet.jpg",contact_bytes)
    archive.writestr("manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2))
    archive.writestr("README.txt","Smart Meals 365 pineapple coconut smoothie. One hero and five individual stages, original 1536x1024 JPEGs.\nRecipe: https://smartc365.com/guides/smart-dinner-pineapple-coconut-smoothie-ko\n")
with zipfile.ZipFile(bundle) as archive:
    if archive.testzip() is not None or len(archive.namelist())!=9: raise RuntimeError("ZIP failed integrity check")
print("PACKAGE_READY",bundle,bundle.stat().st_size,flush=True)

def get(url):
    q=urllib.request.Request(url,headers={"User-Agent":"SmartMeals365-pineapple-public-QA/1.0","Cache-Control":"no-cache"})
    with urllib.request.urlopen(q,timeout=28) as response:
        return response.status,response.read(6_000_000)

RECEIPT.parent.mkdir(parents=True,exist_ok=True)
successful=False
for attempt in range(1,9):
    checks=[]
    for lang in ("ko","en"):
        url=f"{PUBLIC}/guides/smart-dinner-{SLUG}-{lang}?photo_audit={attempt}"
        try:
            code,body=get(url);html=body.decode("utf-8","replace")
            missing=[i for i in range(1,6) if f"{PHOTO_ROOT}/step-{i:02d}.jpg" not in html]
            schema=all(f"{PUBLIC}{PHOTO_ROOT}/step-{i:02d}.jpg" in html for i in range(1,6))
            hero=HERO+VERSION in html and f"{PUBLIC}{HERO}{VERSION}" in html
            embedded=all(f'data-reviewed-process-photo="{i}"' in html for i in range(1,6))
            checks.append(dict(kind="page",lang=lang,http=code,missingSteps=missing,schema=schema,hero=hero,embedded=embedded,ok=code==200 and not missing and schema and hero and embedded))
        except Exception as exc:checks.append(dict(kind="page",lang=lang,ok=False,error=str(exc)[:220]))
    for item in items:
        name=item["file"];path=HERO+VERSION if name=="hero.jpg" else PHOTO_ROOT+"/"+name
        joiner="&" if "?" in path else "?"
        try:
            code,body=get(PUBLIC+path+joiner+"photo_audit="+str(attempt))
            with Image.open(io.BytesIO(body)) as im:size=im.size;fmt=im.format
            matches=code==200 and sha256(body)==item["sha256"] and size==(1536,1024) and fmt=="JPEG"
            checks.append(dict(kind="image",name=name,http=code,sha256=sha256(body),expected=item["sha256"],size=list(size),ok=matches))
        except Exception as exc:checks.append(dict(kind="image",name=name,ok=False,error=str(exc)[:220]))
    successful=all(x["ok"] for x in checks)
    RECEIPT.write_text(json.dumps(dict(checkedAtUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
                  recipe=SLUG,attempt=attempt,publicVerified=successful,checks=checks),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PUBLIC_VERIFY",json.dumps(dict(attempt=attempt,success=successful,failed=[x for x in checks if not x["ok"]]),ensure_ascii=False),flush=True)
    if successful:break
    if attempt<8:time.sleep(10)
if not successful: raise RuntimeError("Public verification did not pass within 8 attempts; see QA receipt")
