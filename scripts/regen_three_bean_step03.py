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
 "ONE extremely natural home-cooking preparation photograph, 1024x1024, intimate slightly overhead viewpoint. "
 "Step 3 of Three Bean Lemon Parsley Salad: exactly 40 grams of RED ONION diced finely, "
 "and 12 grams of washed, dried FLAT-LEAF PARSLEY finely chopped. "
 "A well-used, solid rectangular wooden chopping board lies FLAT on a normal kitchen countertop. "
 "A small pile of realistically cut purple-and-white red onion dice sits LEFT; a distinct modest pile of roughly chopped green flat-leaf parsley sits RIGHT. "
 "One ordinary clean chef's knife is placed completely flat on the wooden board, blade touching the board with realistic contact shadow; its blade is near the parsley but NOT floating. "
 "Tight food-centered crop: the vegetables and chopping board occupy at least 85 percent of the frame. "
 "NO PEOPLE, NO FACES, NO HANDS, NO FINGERS, NO WRISTS, NO ARMS, NO TORSO, NO BODY in frame. "
 "Candid authentic everyday kitchen photography, not stock glamour, no overly perfect symmetrical piles, a few tiny herb fragments on the board, normal knife marks and wood grain, realistic cut ingredients, soft diffuse natural window light. "
 "Believable gravity and contact shadows, no unlisted vegetables or garnish, no floating food, no floating knife, no exaggerated glossy CG food textures, no fake bokeh, no captions, no typography, no logos, no finished salad."
)
raw,ext,size=gen.api(prompt,1024,1024)
out=pathlib.Path("artifacts/smart-meals-process-photos/three-bean-lemon-parsley-salad")
out.mkdir(parents=True,exist_ok=True)
filename="step-03-natural-v3."+ext
(out/filename).write_bytes(raw)
manifest={"type":"one-off rephotograph candidate","recipe":"three-bean-lemon-parsley-salad","step":3,"reason":"User preference: candid food-and-board closeup, no human body or artificial floating utensils","source":"Published bilingual original method: diced red onion 40g and chopped flat-leaf parsley 12g","filename":filename,"size":size,"sha256":hashlib.sha256(raw).hexdigest(),"prompt":prompt,"humanReviewed":False,"sitePublished":False}
(out/"step-03-natural-v3.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print("GENERATED",filename,size,manifest["sha256"],"MANUAL_QA_REQUIRED",flush=True)
