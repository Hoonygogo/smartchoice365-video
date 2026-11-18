#!/usr/bin/env python3
"""Regenerate exactly the original stage-2 photo with stable physically supported colanders."""
import os,json,pathlib,hashlib,importlib.util
if os.getenv("CLOUDFLARE_WORKERS_FREE_CONFIRMED")!="true":raise SystemExit("No AI call: Free tier not confirmed")
for key in ("CLOUDFLARE_ACCOUNT_ID","CLOUDFLARE_AI_TOKEN"):
 if not os.getenv(key):raise SystemExit("No AI call: missing credential "+key)
file=pathlib.Path(__file__).resolve().parent/"smart_meals_process_photo_batch.py"
spec=importlib.util.spec_from_file_location("recipe_photos",file)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
prompt=(
"Professional authentic photorealistic food preparation photograph, natural eye-level kitchen close-up, square image. "
"Show exactly STEP 2 from the recipe Three-Bean Lemon Parsley Salad: rinse 160 g canned red kidney beans AND 160 g canned chickpeas SEPARATELY in colanders under running clean water, then drain. "
"Show a real stainless-steel kitchen sink with a normal faucet. "
"ONE small round metal colander contains only DARK RED KIDNEY BEANS, sits FIRMLY ON ITS OWN FLAT BASE AT THE BOTTOM OF THE SINK DIRECTLY BELOW THE RUNNING FAUCET, water gently rinsing the beans and draining through its holes; "
"its foot clearly TOUCHES THE SINK BASIN and casts a realistic contact shadow. "
"A SECOND separate small colander contains ONLY PALE BEIGE CHICKPEAS, placed FIRMLY on a flat wooden countertop BESIDE THE SINK, with its feet physically contacting the countertop, draining, no water running onto the counter. "
"Colanders have believable real-world shapes and bases; gravity and shadows are correct. "
"Real hands of a home cook can gently tilt an individual rinsed bean while standing at the sink, "
"but all kitchen tools, food and colanders MUST BE supported by solid surfaces, absolutely no levitating colanders, no floating beans, no impossible faucet. "
"Natural Australian home kitchen, soft daylight, realistic scale, correct red kidney bean and chickpea shapes, no extra ingredients, no salt, no finished dish, no text, no logos, no collage."
)
raw,ext,size=module.api(prompt,1024,1024)
out=pathlib.Path("artifacts/smart-meals-process-photos/three-bean-lemon-parsley-salad")
out.mkdir(parents=True,exist_ok=True)
fileName="step-02-natural-v2."+ext
(out/fileName).write_bytes(raw)
meta={"dish":"three-bean-lemon-parsley-salad","step":2,"role":"replacement","stepDescription":"Rinse 160g each canned kidney beans and chickpeas separately in a sieve under running water; drain","fileName":fileName,"width":size[0],"height":size[1],"sha256":hashlib.sha256(raw).hexdigest(),"prompt":prompt,"humanReviewed":False,"published":False}
(out/"step-02-natural-v2.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
print("CANDIDATE_GENERATED",fileName,size,meta["sha256"],"NEEDS_VISUAL_QA",flush=True)
