#!/usr/bin/env python3
"""Rebuild two instruction images where extraneous ice/can label was detected by QA."""
import os,json,pathlib,hashlib
from smart_meals_process_photo_batch import api
if os.environ.get("CLOUDFLARE_WORKERS_FREE_CONFIRMED")!="true":raise SystemExit("Stop: not free confirmed")
r=pathlib.Path("artifacts/smart-meals-process-photos/three-bean-lemon-parsley-salad")
items=[
 ("step-01-v2", "One lifelike editorial close-up kitchen photograph showing the FIRST RECIPE STAGE of preparing three-bean salad: trimmed fresh green beans (160 grams) BLANCHING in a small stainless steel saucepan of gently boiling water on stove, vivid fresh green, bubbles, NO other vegetables, NO ice cubes, NO icy water bowls, NO drain baskets, NO garnish, no labels or text. Single cooking action happening, top angled home kitchen square frame."),
 ("step-02-v2", "One lifelike editorial close-up home-kitchen photograph of SECOND STAGE of three-bean salad: a sturdy stainless steel kitchen colander under gentle running water in kitchen sink, filled with cooked DEEP BURGUNDY RED canned kidney beans (160g) and PALE BEIGE CHICKPEAS (160g), both clearly distinct, rinsing before draining. NO CANS, NO PRINTED LABELS, NO WORDS, no green beans, no other food, no person's hands, just colander, faucet water and two kinds of legumes. Square magazine-realistic photo.")
]
m=json.loads((r/"manifest.json").read_text())
for i,(base,prompt) in enumerate(items):
 if any(r.glob(base+".*")):raise SystemExit("Refuse overwrite "+base)
 b,ext,size=api(prompt,1024,1024);name=base+"."+ext
 (r/name).write_bytes(b)
 m["generated"].append({"file":name,"step":i+1,"size":size,"sha256":hashlib.sha256(b).hexdigest(),"prompt":prompt,"revision":2,"reviewed":False})
 (r/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
 print("GENERATED_MORE_EXACT",name,size,flush=True)
