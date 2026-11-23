#!/usr/bin/env python3
"""Package six visually reviewed salad JPEGs and independently verify the public KO/EN release."""
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
SLUG="cucumber-tomato-feta-olive-salad"
PHOTOS=ROOT/"artifacts/recipe-step-photo"/SLUG
PUBLIC="https://smartc365.com"
PHOTO_ROOT=f"/assets/recipe-step-photos/{SLUG}"
HERO=f"/assets/recipe-photos/{SLUG}.jpg"
HERO_VERSION="?v=20261123-hero-feta-v2"
RECEIPT=ROOT/"artifacts/live-recipe-photo-verification/cucumber-tomato-feta-salad-20261123.json"
NAMES=["hero.jpg"]+[f"step-{n:02d}.jpg" for n in range(1,6)]
EXPECTED={
"hero.jpg":"35154836238495a2fb51f0ad2f807e02d4d3d25ea7e7fd3cadbe28db7d098182",
"step-01.jpg":"a5ca0e3ed45e4c6401bd2b1d9461b2e3cfdcf2ffb0a253a36f7a1f1a3bb91050",
"step-02.jpg":"e915727678cff14abe0da15041eef9ebdeb315092a7e4a6f2b3912b621bb34cd",
"step-03.jpg":"84713a1d07bc302358bad23272cd836a702c3f9d31e46f93ec697d8fe64d1f13",
"step-04.jpg":"1bf242e2c67cc64939146794c5067a22bbe3b8693b21f078bcc9afc40e411c7d",
"step-05.jpg":"7d10af074aada504c0a729bda895e7b512e74be211320326d6cd89d658a2f16a"
}
KO=["대표사진: 오이 토마토 페타 올리브 샐러드","1단계: 오이·방울토마토 세척과 적양파 손질","2단계: 오이 썰기·토마토 반으로 자르기·적양파 얇게 썰기","3단계: 레몬 올리브유 드레싱 만들기","4단계: 오이·토마토·적양파·칼라마타 올리브 섞기","5단계: 페타 치즈와 레몬 드레싱으로 완성"]
EN=["Hero: Greek cucumber tomato feta olive salad","Step 1: Wash whole cucumber, cherry tomatoes and peel red onion","Step 2: Slice cucumber, halve tomatoes and thinly slice onion","Step 3: Mix light lemon and olive oil vinaigrette","Step 4: Toss cucumbers, tomato, onion and Kalamata olives before feta","Step 5: Add feta and lemon dressing to finish"]
def digest(data:bytes)->str:return hashlib.sha256(data).hexdigest()
items=[];thumbs=[]
for i,name in enumerate(NAMES):
    data=(PHOTOS/name).read_bytes()
    if digest(data)!=EXPECTED[name]:raise RuntimeError("Selected approved photo hash mismatch: "+name)
    if len(data)<100000:raise RuntimeError("Selected photo is unexpectedly small: "+name)
    with Image.open(io.BytesIO(data)) as im:
        if im.format!="JPEG" or im.size!=(1536,1024):raise RuntimeError("Unexpected JPEG dimensions: "+name)
        thumbs.append(ImageOps.fit(im.convert("RGB"),(480,320),method=Image.Resampling.LANCZOS))
    items.append({"file":name,"width":1536,"height":1024,"bytes":len(data),"sha256":digest(data),
                  "alt_ko":KO[i],"alt_en":EN[i]})
if len({x["sha256"] for x in items})!=6:raise RuntimeError("Unexpected duplicate originals")
contact=Image.new("RGB",(1500,750),"white");draw=ImageDraw.Draw(contact)
for i,(name,thumb) in enumerate(zip(NAMES,thumbs)):
    col,row=i%3,i//3;x,y=15+col*495,15+row*370
    contact.paste(thumb,(x,y));draw.text((x+5,y+328),name,fill=(20,20,20))
bio=io.BytesIO();contact.save(bio,"JPEG",quality=92,optimize=True)
contact_bytes=bio.getvalue()
manifest={"recipe":SLUG,"title_ko":"오이 토마토 페타 올리브 샐러드",
"title_en":"Cucumber, Tomato, Feta & Olive Salad","servings":2,
"selection":{"hero":"Cloudflare revision 2","step01":"revision 4","step02":"revision 5",
             "step03":"revision 2","step04":"revision 1","step05":"revision 3"},
"quality":"Six individual independent 1536×1024 originals, manually visually reviewed against current KO and EN cooking stages.",
"photos":items,"websiteHeroReplaced":True}
README=(
"SMART MEALS 365 / 오이 토마토 페타 올리브 샐러드\n"
"Representative hero 1 + five separate cooking-stage images, all 1536x1024 JPEGs.\n"
"Recipe for 2: Lebanese cucumber 180g; cherry tomatoes 180g; feta 70g; pitted Kalamata olives 45g; red onion 50g; olive oil 15ml; lemon juice 10ml; oregano 2g; black pepper 1g.\n"
"No mint, parsley, leafy greens, added salt or extra dressing.\n"
"Each numbered file maps directly to the current KO/EN original cooking step.\n"
"Public recipe: https://smartc365.com/guides/smart-dinner-cucumber-tomato-feta-olive-salad-ko\n"
)
(PHOTOS/"preview-contact-sheet.jpg").write_bytes(contact_bytes)
(PHOTOS/"package-manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
bundle=PHOTOS/(SLUG+"-hero-and-5-steps.zip")
with zipfile.ZipFile(bundle,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name in NAMES:z.write(PHOTOS/name,name)
    z.writestr("preview-contact-sheet.jpg",contact_bytes)
    z.writestr("manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2))
    z.writestr("README.txt",README)
with zipfile.ZipFile(bundle) as z:
    if z.testzip() is not None or len(z.namelist())!=9:raise RuntimeError("ZIP integrity check failed")
print(json.dumps({"package":str(bundle),"bytes":bundle.stat().st_size,"photoCount":len(items),"zipEntries":9}))
def get(url:str):
    req=urllib.request.Request(url,headers={"User-Agent":"SmartMeals365-public-process-photo-audit/1.0","Cache-Control":"no-cache"})
    with urllib.request.urlopen(req,timeout=22) as res:return res.status,res.read(6_000_000)
RECEIPT.parent.mkdir(parents=True,exist_ok=True)
for attempt in range(1,7):
    checks=[]
    for lang in ("ko","en"):
        url=f"{PUBLIC}/guides/smart-dinner-{SLUG}-{lang}?stage_photo_audit={attempt}"
        try:
            code,data=get(url);html=data.decode("utf-8","replace")
            expected_steps=[f"{PHOTO_ROOT}/step-{n:02d}.jpg" for n in range(1,6)]
            missing=[path for path in expected_steps if path not in html]
            schema=all(f"{PUBLIC}{path}" in html for path in expected_steps)
            hero_src=(HERO+HERO_VERSION) in html and 'data-photo-orientation="landscape"' in html
            hero_meta=f'{PUBLIC}{HERO}{HERO_VERSION}' in html
            checks.append({"kind":"page","language":lang,"http":code,"missingSteps":missing,
                           "schemaUrls":schema,"newHero":hero_src,"newHeroMetadata":hero_meta,
                           "pass":code==200 and not missing and schema and hero_src and hero_meta})
        except Exception as e:checks.append({"kind":"page","language":lang,"pass":False,"error":str(e)[:240]})
    for name in NAMES:
        urlpath=HERO+HERO_VERSION if name=="hero.jpg" else f"{PHOTO_ROOT}/{name}"
        connector="&" if "?" in urlpath else "?"
        url=f"{PUBLIC}{urlpath}{connector}stage_photo_audit={attempt}"
        try:
            code,data=get(url);sha=digest(data)
            with Image.open(io.BytesIO(data)) as im:w,h=im.size;fmt=im.format
            ok=code==200 and sha==EXPECTED[name] and fmt=="JPEG" and (w,h)==(1536,1024) and len(data)>100000
            checks.append({"kind":"image","name":name,"http":code,"bytes":len(data),"width":w,"height":h,
                          "format":fmt,"sha256":sha,"hashVerified":sha==EXPECTED[name],"pass":ok})
        except Exception as e:checks.append({"kind":"image","name":name,"pass":False,"error":str(e)[:240]})
    pass_all=all(x["pass"] for x in checks)
    report={"checkedAtUTC":dt.datetime.now(dt.timezone.utc).isoformat(),"recipe":SLUG,
            "attempt":attempt,"publicVerified":pass_all,"checks":checks}
    RECEIPT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"attempt":attempt,"publicVerified":pass_all,
                      "failed":[x for x in checks if not x["pass"]]},ensure_ascii=False))
    if pass_all:break
    if attempt<6:time.sleep(12)
