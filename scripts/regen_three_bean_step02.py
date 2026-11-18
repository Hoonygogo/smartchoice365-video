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
 "One photorealistic instructional home kitchen photograph, square format, 45 degree view. "
 "Original salad cooking step: separately rinse and drain 160 grams of canned red kidney beans and 160 grams of canned pale beige chickpeas. "
 "Show ONLY ONE stainless steel perforated colander containing ONLY red kidney beans. "
 "The colander has a wide integrated FLAT BASE physically resting DIRECTLY on the flat floor of a deep stainless steel kitchen sink, with visible shadow and weight bearing. "
 "A thin continuous stream of clean water from the kitchen tap falls straight into the beans in this colander; clear draining water flows through its holes into the sink. "
 "Beside the sink on the kitchen countertop stands ONE white ceramic bowl containing pale beige canned chickpeas ready to rinse separately after the kidney beans. "
 "The white bowl physically rests on the counter, its base clearly touching solid wood. "
 "Only two vessels total: ONE kidney-bean colander IN sink, ONE chickpea bowl ON counter. No other colanders, bowls, stands, dishes or vessels. "
 "NO HANDS and NO PEOPLE, no floating food or tools, no stacked colanders, no second heap of beans anywhere, no beans falling through colander, no tilted or suspended objects, no levitation. "
 "All ingredients fully physically supported by their vessels; all vessels supported by stable solid surfaces. "
 "Highly realistic home cooking food editorial scene in warm natural daylight, accurate gravity and clear physical contact shadows, no unnecessary ingredients, no garnish, no typography, no logos or collage."
)
raw,ext,size=module.api(prompt,1024,1024)
out=pathlib.Path("artifacts/smart-meals-process-photos/three-bean-lemon-parsley-salad")
out.mkdir(parents=True,exist_ok=True)
fileName="step-02-natural-v3."+ext
(out/fileName).write_bytes(raw)
meta={"dish":"three-bean-lemon-parsley-salad","step":2,"role":"replacement","stepDescription":"Rinse 160g each canned kidney beans and chickpeas separately in a sieve under running water; drain","fileName":fileName,"width":size[0],"height":size[1],"sha256":hashlib.sha256(raw).hexdigest(),"prompt":prompt,"humanReviewed":False,"published":False}
(out/"step-02-natural-v3.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
print("CANDIDATE_GENERATED",fileName,size,meta["sha256"],"NEEDS_VISUAL_QA",flush=True)
