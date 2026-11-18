#!/usr/bin/env python3
"""Photo QA remediation: only onion and parsley preparation, absolutely no other food."""
import json,hashlib,os,pathlib
from smart_meals_process_photo_batch import api
if os.environ.get("CLOUDFLARE_WORKERS_FREE_CONFIRMED")!="true":raise SystemExit("Not confirmed free, no call")
root=pathlib.Path("artifacts/smart-meals-process-photos/three-bean-lemon-parsley-salad")
p=("Square editorial instructional kitchen photograph of precisely THIS isolated prep stage: "
 "40 grams of FINELY DICED RED ONION, purple and white little 3mm cubes, and 12 grams of FRESH FINELY CHOPPED ITALIAN FLAT-LEAF PARSLEY, green leaf confetti, organized as two separate little piles on a clean LIGHT WOODEN CUTTING BOARD. "
 "ONE stainless chef knife rests beside the diced vegetables, blade safely on board. "
 "NO BEANS OF ANY KIND, NO CHICKPEAS, NO GREEN BEANS, NO OTHER VEGETABLES, NO FINISHED SALAD, NO COOKED FOOD, NO WATER, NO COLANDER, NO HANDS, NO HUMAN BODY, NO GARNISH, NO WORDS. "
 "Close and clear lifelike photographic details, natural light, one coherent preparation scene, correct cut sizes, beautiful warm neutral kitchen background.")
name="step-03-v3"
if any(root.glob(name+".*")):raise SystemExit("Already generated, no calls")
b,ext,size=api(p,1024,1024)
dest=root/(name+"."+ext);dest.write_bytes(b)
m=json.loads((root/"manifest.json").read_text())
m["generated"].append({"file":dest.name,"step":3,"size":size,"sha256":hashlib.sha256(b).hexdigest(),"prompt":p,"reviewed":False,"revision":3})
(root/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print("REVISED_STAGE3_ONLY",dest,size,flush=True)
