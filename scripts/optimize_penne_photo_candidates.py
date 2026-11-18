#!/usr/bin/env python3
"""Optimise generated candidate JPGs without changing resolution. Originals retained for QA."""
import os,pathlib,io,hashlib,json
from PIL import Image
root=pathlib.Path("artifacts/smart-meals-process-photos/tomato-basil-penne")
m=json.loads((root/"manifest.json").read_text())
optimized=[]
for entry in m["generated"]:
 source=root/entry["file"]
 if not source.name.lower().endswith(".jpg"):continue
 name=source.stem+"-web-opt.jpg";dest=root/name
 if not dest.exists():
  with Image.open(source) as img:
   assert img.width>=1024 and img.height>=1024
   img.convert("RGB").save(dest,format="JPEG",quality=79,optimize=True,progressive=True,subsampling=0)
 data=dest.read_bytes()
 with Image.open(io.BytesIO(data)) as img:size=img.size
 assert size==tuple(entry["size"]) and len(data)<1000000, "Compressed candidate invalid or over 1MB"
 optimized.append({"source":entry["file"],"file":name,"sha256":hashlib.sha256(data).hexdigest(),"size":size,"bytes":len(data),"reviewed":False})
m["optimised"] = optimized
(root/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print("WEB_JPEG_OPTIMIZED",len(optimized),flush=True)
