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
 "Professional lifelike candid home-kitchen food photograph, overhead 45-degree angle, 1024 by 1024. "
 "Exact step three: 40 grams finely DICED purple RED ONION and 12 grams finely CHOPPED flat leaf PARSLEY, fully cut, ready for a three bean salad. "
 "Two modest DISTINCT piles of prepared vegetables rest directly on a single well-used rectangular brown wooden chopping board, onion dice on LEFT, finely chopped tiny leaf pieces of parsley on RIGHT. "
 "There is EXACTLY ONE SINGLE COMPLETE ORDINARY CHEF KNIFE: a continuous silver blade joined to its ONLY black handle on the right, laying HORIZONTALLY FLAT on the board BEHIND both piles, blade edge down touching the wood. "
 "The knife is NOT on top of any vegetable, no other knives, no extra blade, no second handle, no duplicates or overlapping knife forms. "
 "Full single knife visible with believable geometry, only one tip and one handle, ordinary scale, accurate shadow contact and gravity. "
 "NO people, hands, bodies, arms, fingers, chopping action or extra ingredients. "
 "Authentic small home kitchen imperfections: slight unevenness to vegetable cuts, realistic washed flat leaf parsley texture, a few crumbs on board, natural grain, diffused daylight from left. "
 "Food and board fill frame, no stylized product photography, no synthetic glassy shine, no fake blur, no hovering ingredients, no text, no garnish, no finished salad. "
)
raw,ext,size=gen.api(prompt,1024,1024)
out=pathlib.Path("artifacts/smart-meals-process-photos/three-bean-lemon-parsley-salad")
out.mkdir(parents=True,exist_ok=True)
filename="step-03-natural-v4."+ext
(out/filename).write_bytes(raw)
manifest={"type":"one-off rephotograph candidate","recipe":"three-bean-lemon-parsley-salad","step":3,"reason":"User preference: candid food-and-board closeup, no human body or artificial floating utensils","source":"Published bilingual original method: diced red onion 40g and chopped flat-leaf parsley 12g","filename":filename,"size":size,"sha256":hashlib.sha256(raw).hexdigest(),"prompt":prompt,"humanReviewed":False,"sitePublished":False}
(out/"step-03-natural-v4.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print("GENERATED",filename,size,manifest["sha256"],"MANUAL_QA_REQUIRED",flush=True)
