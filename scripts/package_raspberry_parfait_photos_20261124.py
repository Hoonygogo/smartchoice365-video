#!/usr/bin/env python3
"""Validate seven independently generated raspberry yoghurt granola parfait photos and package for user."""
import hashlib
import io
import json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import zipfile

ROOT=Path(__file__).resolve().parents[1]
SLUG="raspberry-yogurt-granola-parfait"
DIR=ROOT/"artifacts"/"recipe-step-photo"/SLUG
NAMES=["hero.jpg"]+[f"step-{n:02d}.jpg" for n in range(1,7)]
LABELS=["HERO","01 Clean dry glasses","02 Rinse raspberries","03 Mix honey-lemon yoghurt",
        "04 First yoghurt & berries","05 Layer crunchy granola","06 Serve both parfaits"]
STEPS_KO=["대표사진","깨끗한 빈 컵 두 개 준비","라즈베리 살살 씻어 물기 제거",
          "요거트·꿀·레몬 제스트 섞기","두 컵에 요거트 반과 라즈베리 반만 넣기",
          "그래놀라·남은 요거트·라즈베리로 층 쌓기","두 잔의 파르페를 차갑게 제공"]
SIZES=[]
digests=[]
for name in NAMES:
    data=(DIR/name).read_bytes()
    if not data.startswith(bytes.fromhex("ffd8")) or len(data)<75000:
        raise RuntimeError("Missing or wrong JPEG: "+name)
    with Image.open(io.BytesIO(data)) as im:
        if im.format!="JPEG" or im.size!=(1536,1024):
            raise RuntimeError(f"Wrong format or dimensions: {name}, {im.format}, {im.size}")
    SIZES.append(len(data))
    digests.append(hashlib.sha256(data).hexdigest())
if len(set(digests))!=len(NAMES):
    raise RuntimeError("Photos not distinct")
generation=json.loads((DIR/"generation-report.json").read_text(encoding="utf-8"))
if generation.get("requestRevision") != 2:
    raise RuntimeError("Latest correction revision 2 missing")
if sorted(x["step"] for x in generation.get("stages",[])) != [4,6]:
    raise RuntimeError("Expected replacement pair not reported")
if any(x.get("status")!="candidate_needs_actual_visual_review" for x in generation["stages"]):
    raise RuntimeError("Failed photo generation for stage 4 or 6")
manifest={"title_ko":"라즈베리 요거트 그래놀라 파르페",
          "title_en":"Raspberry Yoghurt Granola Parfait",
          "originalRecipe":"https://smartc365.com/guides/smart-dinner-raspberry-yogurt-granola-parfait-ko",
          "servings":2,
          "ingredients":["240 g plain Greek yoghurt","130 g crunchy granola","140 g fresh raspberries","15 ml honey","1 g lemon zest"],
          "source":"Cloudflare Workers AI, independently generated and visually reviewed originals",
          "dimensions":[1536,1024],"format":"JPEG",
          "stageVersion":{"hero":1,"step-01":1,"step-02":1,"step-03":1,"step-04":2,"step-05":1,"step-06":2},
          "files":[{"name":name,"sizeBytes":size,"sha256":sha,"labelKo":label}
                   for name,size,sha,label in zip(NAMES,SIZES,digests,["대표사진"]+STEPS_KO[1:])]}
# 3 columns x 3 rows (7 images) with labels in a compact visual contact sheet.
thumbw,thumbh=480,320
canvas=Image.new("RGB",(1500,1125),(251,249,245))
draw=ImageDraw.Draw(canvas)
for i,(name,label) in enumerate(zip(NAMES,LABELS)):
    with Image.open(DIR/name) as image:
        thumb=ImageOps.fit(image.convert("RGB"),(thumbw,thumbh),method=Image.Resampling.LANCZOS)
    x=15+(i%3)*495
    y=15+(i//3)*370
    canvas.paste(thumb,(x,y))
    draw.text((x+8,y+328),label,fill=(38,39,40))
buf=io.BytesIO();canvas.save(buf,format="JPEG",quality=92,optimize=True)
contact=buf.getvalue()
preview=DIR/"preview-contact-sheet.jpg"
preview.write_bytes(contact)
(DIR/"package-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
file=DIR/"raspberry-parfait-hero-and-6-process-photos.zip"
with zipfile.ZipFile(file,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=7) as bundle:
    for name in NAMES:bundle.write(DIR/name,arcname=name)
    bundle.writestr("preview-contact-sheet.jpg",contact)
    bundle.writestr("manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2))
    bundle.writestr("README.txt","Smart Meals 365 - Raspberry Yoghurt Granola Parfait\nOne hero and six independent process photos, 1536x1024 each, KO/EN same set.\nThe order is hero, step-01 to step-06. Not yet published to production website.\n")
with zipfile.ZipFile(file,"r") as bundle:
    bad=bundle.testzip()
    if bad is not None or len(bundle.namelist())!=10:
        raise RuntimeError("ZIP validation failed")
print(json.dumps({"ok":True,"zipName":file.name,"zipBytes":file.stat().st_size,"images":len(NAMES),
                  "contactSheet":preview.name,"sha256":hashlib.sha256(file.read_bytes()).hexdigest()},ensure_ascii=False))
