#!/usr/bin/env python3
"""Regenerate three rejected three-bean salad candidates; reviewed final selection separate."""
import pathlib,json,hashlib,os
from smart_meals_process_photo_batch import api
root=pathlib.Path("artifacts/smart-meals-process-photos/three-bean-lemon-parsley-salad")
root.mkdir(parents=True,exist_ok=True)
data=json.loads((root/"manifest.json").read_text())
intro=("Professional, exceptionally realistic food photograph of an EXACT three-bean lemon-parsley salad. "
 "The recipe uses deep DARK BURGUNDY RED canned KIDNEY BEANS (smooth large curved kidney shape), "
 "PALE BEIGE ROUND chickpeas, vivid green steamed/blanched green beans cut into 3-4 cm segments, "
 "FINE 2-3mm DICE of PURPLE RED ONION, chopped Italian FLAT-LEAF PARSLEY, "
 "lemon juice, olive oil, a little Dijon mustard and black pepper. "
 "NO pinto beans, NO brown beans, NO whole red-onion rings, NO coriander/cilantro, NO cherry tomatoes, "
 "NO lettuce, NO unlisted garnish. No text, no watermarks, no collage. ")
items=[
 ("step-03-v2",1024,1024,"STEP 3 IN PROGRESS, NOT A FINISHED SALAD. Detailed top-down natural photography of neat piles of freshly FINELY DICED PURPLE RED ONION (40g) and freshly MINCED FLAT-LEAF PARSLEY (12g) on a rustic cutting board, a single clean kitchen knife positioned to one side. NO HANDS visible, no whole onions in the dish, do not show beans or sauce yet. Bright real home kitchen textures."),
 ("step-05-v2",1536,1024,"STEP 5 FINISHED COMBINED THREE BEAN SALAD. A low shallow matte cream CERAMIC BOWL on a wooden table, clearly containing roughly equal proportions of deep burgundy DARK RED kidney beans, beige round chickpeas, and tender fresh green beans cut short, FINE PURPLE ONION DICE and finely chopped flat parsley; everything lightly coated with lemon-Dijon-olive oil dressing, not creamy, and black pepper. Camera 45-degree angle, beautifully natural home-cooked food photography, horizontal 3:2; complete bowl visible."),
 ("hero-v2",1536,1024,"EDITORIAL COVER PHOTO of the SAME FINISHED SALAD, photographed from THREE-QUARTER side on a NATURAL LINEN NAPKIN with a wooden table background, distinct composition from final method photo. Small appetising mound of VERY DARK RED KIDNEY BEANS (not pale/brown), beige CHICKPEAS, BLANCHED SHORT GREEN BEANS, only tiny FINELY-DICED RED ONION and FINELY CHOPPED FLAT PARSLEY; glossy pale lemon mustard olive-oil vinaigrette, subtle black pepper. Realistic edible textures, natural daylight, 3:2 landscape, shallow neutral stoneware bowl.")
]
if os.environ.get("CLOUDFLARE_WORKERS_FREE_CONFIRMED")!="true" or not os.environ.get("CLOUDFLARE_ACCOUNT_ID") or not os.environ.get("CLOUDFLARE_AI_TOKEN"):
 raise SystemExit("Free model confirmation or credentials missing; no call and no paid fallback")
for filename,width,height,part in items:
 if any(root.glob(filename+".*")):raise SystemExit("Refuse overwrite")
 raw,ext,size=api(intro+part,width,height)
 dest=root/(filename+"."+ext);dest.write_bytes(raw)
 data["generated"].append({"file":dest.name,"step":0 if filename.startswith("hero") else 3 if filename.startswith("step-03") else 5,"size":size,"sha256":hashlib.sha256(raw).hexdigest(),"prompt":intro+part,"reviewed":False,"revision":2,"replacesRejected":True})
 (root/"manifest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
 print("REGENERATED_FOR_VISUAL_REVIEW",filename,size,flush=True)
