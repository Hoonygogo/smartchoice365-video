#!/usr/bin/env python3
"""Check the public deployed admin photo manager and removed recipe source photo."""
import datetime,json,pathlib,time,urllib.request
BASE="https://smartc365.com"
OUT=pathlib.Path("artifacts/live-recipe-photo-verification/admin-source-photo-removal.json")
OUT.parent.mkdir(parents=True,exist_ok=True)
def get(p):
 req=urllib.request.Request(BASE+p,headers={"User-Agent":"SmartChoice365-photo-owner-controls-live-QA/1.0","Cache-Control":"no-cache"})
 with urllib.request.urlopen(req,timeout=25) as r: return r.status,r.read(600000).decode("utf-8","replace")
last=None
for attempt in range(1,7):
 try:
  admin=get("/admin/?audit=source-photo-owner-controls-"+str(attempt))
  admin_js=get("/assets/admin-recipe-step-photos.js?v=20261118-remove-embedded-v1&audit="+str(attempt))
  reader_js=get("/assets/official-recipe-step-photos.js?v=20261118-original-visibility-v2&audit="+str(attempt))
  shared_js=get("/assets/smart-dinner-recipe.js?v=20261118-reviews-standard-v1&audit="+str(attempt))
  ko=get("/guides/smart-dinner-raspberry-lime-lemonade-ko?audit="+str(attempt))
  en=get("/guides/smart-dinner-raspberry-lime-lemonade-en?audit="+str(attempt))
  tests={
    "admin_http_200":admin[0]==200,
    "admin_new_version":"/assets/admin-recipe-step-photos.js?v=20261118-remove-embedded-v1" in admin[1],
    "admin_control_present":"async function toggleEmbedded(" in admin_js[1] and "official_recipe_embedded_hidden_photos" in admin_js[1] and "사이트에서 제거" in admin_js[1],
    "public_source_hiding_available":"official_recipe_embedded_hidden_photos" in reader_js[1] and "target.closest('figure')" in reader_js[1],
    "shared_script_uses_new_loader":"official-recipe-step-photos.js?v=20261118-original-visibility-v2" in shared_js[1],
    "korean_problem_step_3_removed":'data-reviewed-process-photo="3"' not in ko[1] and 'step-03.jpg' not in ko[1],
    "english_problem_step_3_removed":'data-reviewed-process-photo="3"' not in en[1] and 'step-03.jpg' not in en[1],
    "recipe_steps_preserved":('id="step-3"' in ko[1] and 'id="step-3"' in en[1])
  }
  last={"attempt":attempt,"checks":tests,"http":{n:r[0] for n,r in [("admin",admin),("admin_js",admin_js),("reader_js",reader_js),("shared_js",shared_js),("ko",ko),("en",en)]}}
  if all(tests.values()):break
 except Exception as ex:last={"attempt":attempt,"error":str(ex)[:500]}
 if attempt<6:time.sleep(12)
result={"checkedAtUTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),"pass":bool(last and last.get("checks") and all(last["checks"].values())),**(last or {})}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False))
if not result["pass"]:raise SystemExit("Public site failed photo-control verification; see receipt")
