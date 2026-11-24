#!/usr/bin/env python3
"""Validate and package original individual hummus process photographs for user review."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
import hashlib,io,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
SLUG="silky-lemon-garlic-hummus"
DIR=ROOT/"artifacts"/"recipe-step-photo"/SLUG
FILES=["hero.jpg"]+[f"step-{i:02d}.jpg" for i in range(1,7)]
LABELS=["HERO",
"01 Drain and rinse chickpeas","02 Prepare lemon and minced garlic",
"03 Blend tahini and lemon alone","04 Add chickpeas, garlic and cumin",
"05 Blend with water and olive oil","06 Serve hummus with a swirl"]
KO=["대표사진","병아리콩 헹구고 물기 빼기","레몬즙 걸러 마늘 잘게 다지기","타히니와 레몬만 먼저 갈기","병아리콩·마늘·큐민·소금 갈기","찬물과 올리브유 넣어 곱게 갈기","완성 후무스를 그릇에 담아 무늬 내기"]
SIZES=[];HASHES=[];thumbs=[]
for file in FILES:
  b=(DIR/file).read_bytes()
  if not b.startswith(bytes.fromhex("ffd8")) or len(b)<100000: raise RuntimeError(f"Bad image {file}")
  with Image.open(io.BytesIO(b)) as im:
    if im.format!="JPEG" or im.size!=(1536,1024): raise RuntimeError(f"Bad dimensions {file} {im.size}")
    thumbs.append(ImageOps.fit(im.convert("RGB"),(480,320),method=Image.Resampling.LANCZOS))
  SIZES.append(len(b));HASHES.append(hashlib.sha256(b).hexdigest())
if len(set(HASHES))!=7:raise RuntimeError("Duplicate photos")
report=json.loads((DIR/"generation-report.json").read_text())
if report.get("status")!="candidates_created_unreviewed":raise RuntimeError("Cloudflare creation status not complete")
sheet=Image.new("RGB",(1500,1125),(252,249,246));draw=ImageDraw.Draw(sheet)
for i,(img,label) in enumerate(zip(thumbs,LABELS)):
  x=15+(i%3)*495;y=15+(i//3)*370;sheet.paste(img,(x,y));draw.text((x+8,y+330),label,fill=(36,36,36))
preview=DIR/"preview-contact-sheet.jpg";sheet.save(preview,quality=92,optimize=True)
manifest={"titleKo":"레몬 마늘 크리미 후무스","titleEn":"Silky Lemon Garlic Hummus",
"servings":4,"source":"Official Smart Meals 365 KO/EN 6-step recipe",
"stageCount":6,"images":[{"file":p,"bytes":n,"sha256":s,"descriptionKo":k} for p,n,s,k in zip(FILES,SIZES,HASHES,KO)],
"reviewNote":"One standalone photograph per recipe step, no storyboard, 1536x1024 images. Website publication not automatic."}
(DIR/"package-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
zipfile_path=DIR/"hummus-hero-and-6-process-photos.zip"
with zipfile.ZipFile(zipfile_path,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in FILES: z.write(DIR/p,arcname=p)
  z.write(preview,arcname=preview.name)
  z.writestr("manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2))
  z.writestr("README.txt","Smart Meals 365 - Silky Lemon Garlic Hummus: hero.jpg and step-01.jpg through step-06.jpg, original 1536x1024 photographs. Not deployed to live website.\n")
with zipfile.ZipFile(zipfile_path,"r") as z:
  if z.testzip() is not None or len(z.namelist())!=10:raise RuntimeError("ZIP integrity failed")
print(json.dumps({"zip":str(zipfile_path),"size":zipfile_path.stat().st_size,"images":7,"ok":True},ensure_ascii=False))
