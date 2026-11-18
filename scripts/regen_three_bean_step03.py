#!/usr/bin/env python3
"""One image ONLY: redo 3-bean salad step-3 with physically grounded food prep."""
import os,sys,json,hashlib,pathlib,importlib.util
if os.getenv("CLOUDFLARE_WORKERS_FREE_CONFIRMED")!="true":
 raise SystemExit("Workers Free guard failed; no image request")
for key in ("CLOUDFLARE_AI_TOKEN","CLOUDFLARE_ACCOUNT_ID"):
 if not os.getenv(key):raise SystemExit("Missing scoped credential "+key)
module=pathlib.Path(__file__).resolve().parent/"smart_meals_process_photo_batch.py"
spec=importlib.util.spec_from_file_location("recipe_photo_generator",module)
gen=importlib.util.module_from_spec(spec);spec.loader.exec_module(gen)
prompt=(
 "ONE highly realistic instructional food photograph, square format 1024x1024. "
 "Exactly step three of Three-Bean Lemon Parsley Salad: chop 40 grams of RED ONION "
 "into small dice, wash, dry and finely chop 12 grams of FLAT-LEAF PARSLEY. "
 "A REAL home cook, wearing casual kitchen clothing, is actively chopping the "
 "parsley with a standard chef's knife held firmly in the right hand. "
 "A left hand carefully gathers the leaves safely. "
 "THE KNIFE BLADE'S TIP AND CUTTING EDGE ARE PHYSICALLY TOUCHING THE WOODEN BOARD "
 "and visibly supported while cutting. NO floating knives, NO levitating food, "
 "no detached hands or object collisions. "
 "A stable thick cutting board lies FLAT on a kitchen countertop, "
 "with a small separate pile of accurately diced purple red onion on the LEFT, "
 "a small pile of freshly chopped green parsley on the RIGHT. "
 "Use realistic human hands and anatomy with exactly five fingers on each hand, "
 "natural joints and grip, realistic scale and shadow contact. "
 "Slight three-quarter overhead camera angle, warm bright real kitchen light, "
 "original appetising culinary teaching photography, natural material textures. "
 "No added ingredients, vegetables, food containers, floating objects, text, labels, "
 "captions, graphics, collage or logos. Do not show completed salad."
)
raw,ext,size=gen.api(prompt,1024,1024)
out=pathlib.Path("artifacts/smart-meals-process-photos/three-bean-lemon-parsley-salad")
out.mkdir(parents=True,exist_ok=True)
filename="step-03-natural-v2."+ext
(out/filename).write_bytes(raw)
manifest={"type":"one-off rephotograph candidate","recipe":"three-bean-lemon-parsley-salad","step":3,"reason":"Physical plausibility: floating knife / missing real person","source":"Published bilingual original method: diced red onion 40g and chopped flat-leaf parsley 12g","filename":filename,"size":size,"sha256":hashlib.sha256(raw).hexdigest(),"prompt":prompt,"humanReviewed":False,"sitePublished":False}
(out/"step-03-natural-v2.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print("GENERATED",filename,size,manifest["sha256"],"MANUAL_QA_REQUIRED",flush=True)
