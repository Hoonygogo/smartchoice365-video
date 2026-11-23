#!/usr/bin/env python3
"""Package six visually reviewed Cloudflare milkshake photographs and verify live KO/EN pages."""
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
SLUG="chocolate-cookie-milkshake"
PHOTOS=ROOT/"artifacts/recipe-step-photo"/SLUG
PUBLIC="https://smartc365.com"
PHOTO_ROOT=f"/assets/recipe-step-photos/{SLUG}"
HERO=f"/assets/recipe-photos/{SLUG}.jpg"
VERSION="?v=20261123-cloudflare-milkshake-v4"
RECEIPT=ROOT/"artifacts/live-recipe-photo-verification/chocolate-cookie-milkshake-20261123.json"
FILES=["hero.jpg"]+[f"step-{n:02d}.jpg" for n in range(1,6)]
GIT_HASHES={
 "hero.jpg":"f952632553d309fb482110c15f188808714a5518",
 "step-01.jpg":"71a33cbef598a8e843bccd007fcd35c69d5c3488",
 "step-02.jpg":"1597d650255357eb2cb6bbe3eba597f4d5b0f03a",
 "step-03.jpg":"68705f3df546894bd82a725a1b5e71869796213c",
 "step-04.jpg":"41da0ef3fcc1404ce76005b0928df5069c102d6d",
 "step-05.jpg":"c92631ffaa9a79b18bdaad4e6121106683ab2c4f",
}
KO=["초콜릿 쿠키 밀크셰이크 완성 2잔","차가운 우유와 바닐라 아이스크림을 빈 믹서 옆에 준비",
    "초콜릿 쿠키를 부수고 장식용 부스러기를 따로 보관","우유·바닐라 아이스크림·코코아를 뚜껑 닫고 갈기",
    "초콜릿 셰이크에 부순 쿠키를 넣고 짧게 섞기 직전","초콜릿 시럽과 쿠키 부스러기를 올린 완성 밀크셰이크 2잔"]
EN=["Chocolate cookie milkshake, two finished glasses","Separate cold milk and vanilla ice cream beside an empty blender",
    "Broken chocolate biscuits and reserved garnish crumbs","Smooth milk, vanilla ice cream and cocoa in a closed blender",
    "Broken chocolate cookies added to the blender before brief pulsing","Two chocolate cookie milkshakes finished with syrup and cookie crumbs"]

def sha256(data): return hashlib.sha256(data).hexdigest()
def gitblob(data): return hashlib.sha1(f"blob {len(data)}\\0".encode()+data).hexdigest()

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
manifest=dict(recipe=SLUG,titleKo="초콜릿 쿠키 밀크셰이크",titleEn="Chocolate Cookie Milkshake",
    servings=2, ingredients=["vanilla ice cream 260 g","milk 180 ml","cocoa 12 g",
    "chocolate biscuits 60 g","chocolate syrup 20 ml"],
    selectedRevisions={"hero":2,"step1":3,"step2":2,"step3":2,"step4":4,"step5":2},
    images=items, visuallyReviewed=True, processPhotoCount=5,
    siteCommit="463d90e1172d8749da07724a45f9ea6e7dca68fc")
(PHOTOS/"package-manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\\n",encoding="utf-8")
bundle=PHOTOS/(SLUG+"-hero-and-5-steps.zip")
with zipfile.ZipFile(bundle,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for name in FILES: archive.write(PHOTOS/name,name)
    archive.writestr("preview-contact-sheet.jpg",contact_bytes)
    archive.writestr("manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2))
    archive.writestr("README.txt","Smart Meals 365 chocolate cookie milkshake. One hero and five individual stages, original 1536x1024 JPEGs.\\nRecipe: https://smartc365.com/guides/smart-dinner-chocolate-cookie-milkshake-ko\\n")
with zipfile.ZipFile(bundle) as archive:
    if archive.testzip() is not None or len(archive.namelist())!=9: raise RuntimeError("ZIP failed integrity check")
print("PACKAGE_READY",bundle,bundle.stat().st_size,flush=True)

def get(url):
    q=urllib.request.Request(url,headers={"User-Agent":"SmartMeals365-milkshake-public-QA/1.0","Cache-Control":"no-cache"})
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
                  recipe=SLUG,attempt=attempt,publicVerified=successful,checks=checks),ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
    print("PUBLIC_VERIFY",json.dumps(dict(attempt=attempt,success=successful,failed=[x for x in checks if not x["ok"]]),ensure_ascii=False),flush=True)
    if successful:break
    if attempt<8:time.sleep(10)
if not successful: raise RuntimeError("Public verification did not pass within 8 attempts; see QA receipt")
