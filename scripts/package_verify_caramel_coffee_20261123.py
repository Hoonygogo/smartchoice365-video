#!/usr/bin/env python3
"""One-off exact-original caramel iced coffee photo ZIP + public Cloudflare verification."""
import datetime as dt
import hashlib
import io
import json
import pathlib
import time
import urllib.error
import urllib.request
import zipfile
from PIL import Image, ImageDraw, ImageOps

ROOT=pathlib.Path(__file__).resolve().parents[1]
SLUG="iced-caramel-coffee-cream"
PHOTO=ROOT/"artifacts/recipe-step-photo"/SLUG
OUT_ZIP=PHOTO/"iced-caramel-coffee-cream-hero-and-5-steps.zip"
RECEIPT=ROOT/"artifacts/live-recipe-photo-verification/caramel-coffee-20261123.json"
BASE="https://smartc365.com"
STAGE_DIR=f"/assets/recipe-step-photos/{SLUG}"
HERO_URL=f"/assets/recipe-photos/{SLUG}.jpg"
HERO_QUERY="?v=20261123-hero-revised"
PHOTO_NAMES=["hero.jpg"]+[f"step-{i:02d}.jpg" for i in range(1,6)]
EXPECTED={
 "hero.jpg":"59f6407066624394eba488ed48374615923e765afc82ab4cbf6ba99ab2b177d7",
 "step-01.jpg":"6097fc9c0c5164064ed8f5350f538a2491f6b9a0661591e08fee7036c1b131ac",
 "step-02.jpg":"fb51b347843339eb7b4ab15974ac71349363d5879a0ec9adcf3bcb8b00e5c187",
 "step-03.jpg":"a9d511b4aa02f24356a392083591590c81a136cb426aa4d793d4c6bf16d13409",
 "step-04.jpg":"7c6296aa0073044f71225063f9e5af9d44f9dbb8393bf0e06517b44aa76f8bae",
 "step-05.jpg":"3edf0b6f37f1bb64f152e54630930fdfa3b7209003423575a996e80ee3beaea2",
}
KO=["대표사진: 휘핑크림을 올린 아이스 캐러멜 커피 두 잔","1. 에스프레소 추출 후 식히기","2. 유리잔 두 개에 얼음 나눠 담기","3. 캐러멜 시럽과 찬 우유 넣기","4. 식힌 에스프레소 나눠 넣기","5. 휘핑크림을 올려 완성"]
EN=["Hero: two caramel iced coffees with cream","1. Brew and cool espresso","2. Divide ice between two glasses","3. Add caramel syrup and cold milk","4. Add cooled espresso to both glasses","5. Finish both with whipped cream"]
def sha256(raw):return hashlib.sha256(raw).hexdigest()

records=[]
thumbs=[]
for index,name in enumerate(PHOTO_NAMES):
    data=(PHOTO/name).read_bytes()
    digest=sha256(data)
    if digest!=EXPECTED[name]:raise RuntimeError("Source photo digest mismatch: "+name+" "+digest)
    if len(data)<100000:raise RuntimeError("Photo is unexpectedly tiny: "+name)
    with Image.open(io.BytesIO(data)) as im:
        if im.format!="JPEG" or im.size!=(1536,1024):raise RuntimeError("Wrong image format or true dimensions: "+name)
        thumbs.append(ImageOps.fit(im.convert("RGB"),(480,320),method=Image.Resampling.LANCZOS))
    records.append({"filename":name,"width":1536,"height":1024,"bytes":len(data),"sha256":digest,"alt_ko":KO[index],"alt_en":EN[index]})
preview=Image.new("RGB",(1500,750),"white")
draw=ImageDraw.Draw(preview)
for i,(name,img) in enumerate(zip(PHOTO_NAMES,thumbs)):
    col=i%3;row=i//3;x=15+col*495;y=15+row*370
    preview.paste(img,(x,y));draw.text((x+5,y+329),name,fill=(25,25,25))
preview_buffer=io.BytesIO()
preview.save(preview_buffer,"JPEG",quality=90,optimize=True)
manifest={"recipe_slug":SLUG,"title_ko":"아이스 캐러멜 크림 커피","title_en":"Iced Caramel Coffee with Cream",
          "yield":"2 glasses","items":records,"generated_by":"Cloudflare Workers AI Free, visually reviewed",
          "websiteHeroReplaced":True,"stepPhotos":[1,2,3,4,5]}
readme=(
"SMART MEALS 365 / 아이스 캐러멜 크림 커피\n"
"Representative hero 1 + five separate original step photographs (1536 x 1024 JPEG).\n"
"두 잔 레시피: 식힌 에스프레소 80ml, 우유 260ml, 캐러멜 시럽 30ml, 얼음 160g, 휘핑크림 45g.\n"
"step-01 espresso; step-02 ice; step-03 caramel+milk; step-04 espresso layers; step-05 whipped cream.\n"
"Unlike earlier progress-only packages, this ZIP contains ALL 6 approved original photos.\n"
"Published recipe: https://smartc365.com/guides/smart-dinner-iced-caramel-coffee-cream-ko\n"
)
PHOTO.mkdir(parents=True,exist_ok=True)
(PHOTO/"preview-contact-sheet.jpg").write_bytes(preview_buffer.getvalue())
(PHOTO/"package-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
with zipfile.ZipFile(OUT_ZIP,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for x in PHOTO_NAMES:z.write(PHOTO/x,x)
    z.writestr("preview-contact-sheet.jpg",preview_buffer.getvalue())
    z.writestr("manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2))
    z.writestr("README.txt",readme)
with zipfile.ZipFile(OUT_ZIP) as z:
    if z.testzip() is not None or len(z.namelist())!=9:raise RuntimeError("ZIP integrity failed")
print(json.dumps({"package":str(OUT_ZIP),"bytes":OUT_ZIP.stat().st_size,"fileCount":6,"format":"six unique 1536x1024 JPEGs"}))

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"SmartMeals365-real-public-release-check/1.0","Cache-Control":"no-cache"})
    with urllib.request.urlopen(req,timeout=22) as response:return response.status,response.read(6000000)

RECEIPT.parent.mkdir(parents=True,exist_ok=True)
for attempt in range(1,7):
    checks=[]
    for lang in ("ko","en"):
        url=f"{BASE}/guides/smart-dinner-{SLUG}-{lang}?caramel_photo_release={attempt}"
        try:
            code,body=get(url);html=body.decode("utf-8","replace")
            missing=[f"{STAGE_DIR}/step-{n:02d}.jpg" for n in range(1,6) if f"{STAGE_DIR}/step-{n:02d}.jpg" not in html]
            structured=all(f"{BASE}{STAGE_DIR}/step-{n:02d}.jpg" in html for n in range(1,6))
            hero_updated=HERO_URL+HERO_QUERY in html and 'data-photo-orientation="landscape"' in html
            checks.append({"type":"page","language":lang,"http":code,"missing_steps":missing,"schema_urls":structured,
                "newHero":hero_updated,"pass":code==200 and not missing and structured and hero_updated})
        except Exception as err:checks.append({"type":"page","language":lang,"pass":False,"error":str(err)[:250]})
    for name in PHOTO_NAMES:
        path=HERO_URL+HERO_QUERY if name=="hero.jpg" else f"{STAGE_DIR}/{name}"
        try:
            code,data=get(BASE+path+f"{'&' if '?' in path else '?'}caramel_photo_release={attempt}")
            digest=sha256(data)
            with Image.open(io.BytesIO(data)) as im: w,h=im.size;fmt=im.format
            checks.append({"type":"photo","name":name,"url":path,"http":code,"sha256":digest,
              "size":[w,h],"bytes":len(data),"hash_verified":digest==EXPECTED[name],
              "pass":code==200 and digest==EXPECTED[name] and fmt=="JPEG" and (w,h)==(1536,1024) and len(data)>100000})
        except Exception as err:checks.append({"type":"photo","name":name,"pass":False,"error":str(err)[:250]})
    status=all(x["pass"] for x in checks)
    audit={"checkedAtUTC":dt.datetime.now(dt.timezone.utc).isoformat(),"slug":SLUG,
           "publicVerified":status,"attempt":attempt,"checks":checks}
    RECEIPT.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"attempt":attempt,"publicVerified":status,"failed":[x for x in checks if not x["pass"]]},ensure_ascii=False))
    if status:break
    if attempt<6:time.sleep(12)
