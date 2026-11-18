#!/usr/bin/env python3
"""Two genuine original-recipe photo fixes for penne preparation without extra ingredients."""
import os,json,hashlib,pathlib
from smart_meals_process_photo_batch import api
if os.environ.get('CLOUDFLARE_WORKERS_FREE_CONFIRMED')!='true':raise SystemExit("No confirmed free tier")
root=pathlib.Path("artifacts/smart-meals-process-photos/tomato-basil-penne")
items=[
 ("step-01-v2","Square lifelike culinary editorial photo ONLY of preparing ingredients for two-person tomato basil PENNE pasta: a single chopped pile of FINE 90 GRAM brown onion dice (no whole onions), 9 GRAM finely minced garlic, 120 grams bright red CHERRY TOMATOES cut into equal halves, 12g fresh basil leaves torn by hand and kept separately. Beautifully arranged on wooden prep board with ONE kitchen knife resting nearby. Exactly these ingredients only, NO PASTA, no pasta sauce, no other food, no text, no hands."),
 ("step-02-v2","Square lifelike detailed cooking-process photograph ONLY of 180 GRAMS DRY PENNE TUBE PASTA cooking in rapidly boiling WATER with a tiny pinch of salt in ONE stainless-steel pot on a stovetop; PENNE TUBES evenly visible just below bubbling clear water surface. No TOMATOES, NO RED INGREDIENTS, no pasta sauce, no garlic, no oil, no garnish, no extra food, no label, no fake writing. Fresh natural kitchen light. This is al-dente boiling stage, NOT a completed dish.")
]
manifest=json.loads((root/"manifest.json").read_text())
for i,(name,prompt) in enumerate(items):
 if any(root.glob(name+".*")):raise SystemExit("Refuse to overwrite "+name)
 raw,ext,size=api(prompt,1024,1024);filename=name+"."+ext
 (root/filename).write_bytes(raw)
 manifest["generated"].append({"file":filename,"step":i+1,"size":size,"sha256":hashlib.sha256(raw).hexdigest(),"prompt":prompt,"reviewed":False,"revision":2})
 (root/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
 print("CORRECTED_PENNE_STAGE",filename,size,flush=True)
