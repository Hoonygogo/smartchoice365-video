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
 "Single completely natural and believable close-up candid home cooking photograph, slightly angled overhead camera. "
 "This shows the COMPLETED vegetable chopping stage of a three-bean salad: "
 "on the left a small pile of 40 grams of FINELY DICED purple-and-white RED ONION (tiny cubes approximately 4 mm), "
 "and on the right 12 grams of finely MINCED FLAT-LEAF PARSLEY consisting entirely of TINY CHOPPED GREEN FLAKES, approximately 2 to 4 mm each. "
 "All parsley is properly chopped into small fragments, not intact sprigs, not large leaves, not stems, not a bunch of whole parsley. "
 "These two modest piles rest directly on ONE realistically scratched rectangular wooden chopping board, stable on a light kitchen worktop. "
 "Only the two prepared chopped ingredients and wood board in focus; no knife, no tools, no other vegetables, no other food. "
 "No humans, no hands, no bodies, no limbs. All food rests directly on the board with convincing gravity and soft contact shadows. "
 "Unstyled truthful home cooking image with slightly irregular natural knife cuts and some scattered chopped parsley flecks. "
 "Gentle north-facing window daylight, realistic textures and scale, no staged advertising look, no artificial glossy CG appearance, no dramatic blur, no hovering objects, no captions or graphics."
)
raw,ext,size=gen.api(prompt,1024,1024)
out=pathlib.Path("artifacts/smart-meals-process-photos/three-bean-lemon-parsley-salad")
out.mkdir(parents=True,exist_ok=True)
filename="step-03-natural-v5."+ext
(out/filename).write_bytes(raw)
manifest={"type":"one-off rephotograph candidate","recipe":"three-bean-lemon-parsley-salad","step":3,"reason":"User preference: candid food-and-board closeup, no human body or artificial floating utensils","source":"Published bilingual original method: diced red onion 40g and chopped flat-leaf parsley 12g","filename":filename,"size":size,"sha256":hashlib.sha256(raw).hexdigest(),"prompt":prompt,"humanReviewed":False,"sitePublished":False}
(out/"step-03-natural-v5.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print("GENERATED",filename,size,manifest["sha256"],"MANUAL_QA_REQUIRED",flush=True)
