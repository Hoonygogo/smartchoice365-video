#!/usr/bin/env python3
"""Package six visually inspected iced-matcha photos as individual, unaltered JPGs."""
import hashlib, io, json, pathlib, zipfile
from PIL import Image, ImageDraw, ImageOps
ROOT=pathlib.Path(__file__).resolve().parents[1]
FOLDER=ROOT/"artifacts/recipe-step-photo/iced-matcha-milk-latte"
NAMES=["hero.jpg"]+[f"step-{i:02d}.jpg" for i in range(1,6)]
EXPECTED={
 "hero.jpg":"f7411730cc5fb80933a10843fbcbcee5f0b571ab2853d5ab6d29de0da64008fc",
 "step-01.jpg":"c17a0896917f939c1fb95911140dfbb2f4e4ee68a219f102994a83a38fda2788",
 "step-02.jpg":"b5fdf5597fdfcf037092834ee93ea7f0008ceffc71b32c62563a2575cce944e2",
 "step-03.jpg":"7e6a3df95303aab280c8f97e5b75018977e9a687af0a5fde1fa2b10672ecc4e4",
 "step-04.jpg":"46b9f5a01d4c2ee23e2b53acbd5345db01dc5beb3f21980e0c90a3480c5231a2",
 "step-05.jpg":"85c1709510fda3727ebe99969d51b4df69ac66ab11d64a6848f38dd870b38cdc",
}
CAPTIONS_KO=["대표사진 — 아이스 말차 밀크 라테 2잔","1. 투명한 물 70ml 준비","2. 말차 가루 6g 체 치기","3. 따뜻한 물로 말차 원액 풀기","4. 얼음과 우유 두 잔, 말차 원액 따로 준비","5. 말차를 우유에 부어 두 잔 완성"]
CAPTIONS_EN=["Hero — two iced matcha milk lattes","1. Prepare 70 ml clear warm water","2. Sift 6 g matcha powder","3. Whisk matcha in warm water","4. Two iced milk glasses and separate concentrate","5. Finished two iced matcha milk lattes"]
items=[]
thumbs=[]
for index,name in enumerate(NAMES):
    data=(FOLDER/name).read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    if digest!=EXPECTED[name]:raise ValueError(f"Unexpected photo bytes {name}: {digest}")
    if len(data)<100000:raise ValueError("Too small "+name)
    with Image.open(io.BytesIO(data)) as im:
        if im.format!="JPEG" or im.size!=(1536,1024):raise ValueError(f"Unexpected photo dimensions {name}")
        thumbs.append(ImageOps.fit(im.convert("RGB"),(520,346),method=Image.Resampling.LANCZOS))
    items.append({"file":name,"width":1536,"height":1024,"bytes":len(data),"sha256":digest,"ko":CAPTIONS_KO[index],"en":CAPTIONS_EN[index]})
preview=Image.new("RGB",(3*520+4*22,2*(346+42)+3*22),"white")
draw=ImageDraw.Draw(preview)
for i,(name,thumb) in enumerate(zip(NAMES,thumbs)):
    x=22+(i%3)*(520+22);y=22+(i//3)*(346+42+22)
    preview.paste(thumb,(x,y))
    draw.text((x+5,y+352),name,fill=(20,20,20))
buffer=io.BytesIO();preview.save(buffer,format="JPEG",quality=90,optimize=True)
manifest={"recipe":"iced-matcha-milk-latte","yield":"2 glasses","originalHeroOnSitePreserved":True,
 "photos":items,"stagePhotos":[1,2,3,4,5],"originalPhotoSource":"Cloudflare Workers AI Free, visually checked",
 "qualityRule":"The six JPEGs are independent full-resolution originals, never crops of a collage."}
readme="""SMART MEALS 365 — 아이스 말차 밀크 라테
대표사진 1장 + 과정사진 5장 (각각 1536 x 1024)
우리 홈페이지 원래 대표사진은 그대로 유지됩니다.
이 ZIP의 hero.jpg는 추가 제작한 대안 대표사진입니다.
Steps 1–5 appear on both KO/EN recipe pages.
Ingredient contract: matcha 6g, warm water 70ml, milk 320ml, maple syrup 15ml, ice 140g (2 glasses).
There are no duplicate step photos, collages or upscaled thumbnails in this bundle.
"""
target=FOLDER/"iced-matcha-milk-latte-hero-and-5-steps.zip"
with zipfile.ZipFile(target,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for item in items:z.write(FOLDER/item["file"],item["file"])
    z.writestr("preview-contact-sheet.jpg",buffer.getvalue())
    z.writestr("manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2))
    z.writestr("README.txt",readme)
with zipfile.ZipFile(target) as z:
    if z.testzip():raise RuntimeError("ZIP failed integrity test")
    assert len(z.namelist())==9
(FOLDER/"package-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
(FOLDER/"preview-contact-sheet.jpg").write_bytes(buffer.getvalue())
print(json.dumps({"package":str(target),"bytes":target.stat().st_size,"photos":len(items),"zipEntries":9}))
