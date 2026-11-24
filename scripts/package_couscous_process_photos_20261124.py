#!/usr/bin/env python3
"""Validate and package original individual couscous process photographs for user review."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
import hashlib,io,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
SLUG="lemon-herb-chickpea-couscous"
DIR=ROOT/"artifacts"/"recipe-step-photo"/SLUG
FILES=["hero.jpg"]+[f"step-{i:02d}.jpg" for i in range(1,7)]
LABELS=["HERO: Finished couscous","01 Dry instant couscous","02 Soak with boiling water","03 Fluff cooled couscous",
"04 Prep chickpeas and vegetables","05 Mix lemon oil dressing","06 Combine and serve"]
KO=["대표사진","작은 알갱이 건조 즉석 쿠스쿠스 160g 계량","끓는 물 190ml를 넣고 덮어 불리기","포크로 쿠스쿠스 알갱이 풀기",
"병아리콩·토마토·오이·올리브·파슬리 손질","레몬즙·올리브유·소금 드레싱 만들기","모든 재료를 고루 섞어 완성"]
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
manifest={"titleKo":"레몬 허브 병아리콩 쿠스쿠스","titleEn":"Lemon Herb Chickpea Couscous",
"servings":4,"source":"Official Smart Meals 365 KO/EN 6-step recipe",
"stageCount":6,"images":[{"file":p,"bytes":n,"sha256":s,"descriptionKo":k} for p,n,s,k in zip(FILES,SIZES,HASHES,KO)],
"reviewNote":"One standalone photograph per recipe step, no storyboard, 1536x1024 images. Website publication not automatic."}
(DIR/"package-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
zipfile_path=DIR/"couscous-hero-and-6-process-photos.zip"
with zipfile.ZipFile(zipfile_path,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in FILES: z.write(DIR/p,arcname=p)
  z.write(preview,arcname=preview.name)
  z.writestr("manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2))
  z.writestr("README.txt","Smart Meals 365 - Lemon Herb Chickpea Couscous: hero.jpg and step-01.jpg through step-06.jpg, original 1536x1024 photographs. Not deployed to live website.\n")
with zipfile.ZipFile(zipfile_path,"r") as z:
  if z.testzip() is not None or len(z.namelist())!=10:raise RuntimeError("ZIP integrity failed")
print(json.dumps({"zip":str(zipfile_path),"size":zipfile_path.stat().st_size,"images":7,"ok":True},ensure_ascii=False))
