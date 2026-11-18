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
 "An exceptionally natural close-up photograph of STEP 2 of making a three-bean lemon parsley salad, medium overhead angle, square composition. "
 "Exactly TWO ordinary metal kitchen colanders, each with a broad visible FLAT PEDESTAL BASE, positioned SIDE BY SIDE on ONE level wooden kitchen countertop. "
 "LEFT colander contains ONLY 160 grams of rinsed glossy DARK RED CANNED KIDNEY BEANS. "
 "RIGHT colander contains ONLY 160 grams of rinsed PALE BEIGE CANNED CHICKPEAS. "
 "Both colanders stand with their WHOLE FLAT BASES IN FULL PHYSICAL CONTACT on the countertop, fully supported from below, weight, gravity, contact shadows all highly realistic. "
 "Beans glisten with clean rinse water and are naturally draining in their separate perforated colanders, with a few small water droplets visible on the colander walls and on folded absorbent towels underneath each base. "
 "Neither colander leans over a sink nor is suspended in the air. There is NO sink, faucet, tap, running water, person, fingers, utensils or additional containers visible. "
 "Natural warm window daylight, believable Australian home kitchen, authentic everyday food preparation, shallow depth of field, each physical object grounded on the same level counter. "
 "NO floating ingredients, NO falling beans, NO unsupported floating bowls, NO inexplicable extra food, NO strange props, no garnish, no lettering, no watermark, no illustration, no collage. "
 "Show just the two drained beans separately in stable colanders ready for the next step, not the finished dish."
)
raw,ext,size=module.api(prompt,1024,1024)
out=pathlib.Path("artifacts/smart-meals-process-photos/three-bean-lemon-parsley-salad")
out.mkdir(parents=True,exist_ok=True)
fileName="step-02-natural-v4."+ext
(out/fileName).write_bytes(raw)
meta={"dish":"three-bean-lemon-parsley-salad","step":2,"role":"replacement","stepDescription":"Rinse 160g each canned kidney beans and chickpeas separately in a sieve under running water; drain","fileName":fileName,"width":size[0],"height":size[1],"sha256":hashlib.sha256(raw).hexdigest(),"prompt":prompt,"humanReviewed":False,"published":False}
(out/"step-02-natural-v4.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
print("CANDIDATE_GENERATED",fileName,size,meta["sha256"],"NEEDS_VISUAL_QA",flush=True)
