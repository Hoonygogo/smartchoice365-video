#!/usr/bin/env python3
"""Free Workers AI image candidate for English buying guides. Failure is NOT a publishing gate."""
import base64, datetime as dt, hashlib, io, json, os, pathlib, re, sys, urllib.request, urllib.error
from PIL import Image
BRISBANE=dt.timezone(dt.timedelta(hours=10))
TODAY=dt.datetime.now(BRISBANE).strftime("%Y-%m-%d")
REQUEST=pathlib.Path("requests/site-article-hero")/(TODAY+".json")
OUT=pathlib.Path("artifacts/site-article-hero")
META=OUT/(TODAY+".json")
MODEL="@cf/black-forest-labs/flux-1-schnell"
def write(status,reason,topic="",**extra):
    OUT.mkdir(parents=True,exist_ok=True)
    result={"schemaVersion":1,"publishingDate":TODAY,"channel":"en-au","topicId":topic,
            "status":status,"reason":reason,"model":MODEL,"attemptLimit":1,
            "paidFallback":False,"imagePath":None,"sha256":None,"neuronUsage":None,
            "visualReviewRequired":True,"usageApproved":False,
            "checkedAtUTC":dt.datetime.now(dt.timezone.utc).isoformat(),**extra}
    META.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("FREE_IMAGE_RESULT",status,reason,flush=True)
def run():
    if META.exists():print("ALREADY_PROCESSED_NO_RETRY",TODAY);return
    if not REQUEST.exists():print("NO_NEW_IMAGE_REQUEST",TODAY);return
    try:
        obj=json.loads(REQUEST.read_text())
        assert obj["schemaVersion"]==1 and obj["channel"]=="en-au" and obj["publishingDate"]==TODAY
        topic=obj["topicId"]; assert re.fullmatch("[a-z0-9][a-z0-9-]{5,100}",topic)
        prompt=obj["scenePrompt"];assert isinstance(prompt,str) and 100<=len(prompt)<=1450
        assert re.fullmatch("[0-9a-f]{40}",obj["researchCommitSha"])
    except (ValueError,AssertionError,KeyError,TypeError,OSError) as e:
        write("fallback","invalid_request_"+type(e).__name__);return
    if os.getenv("CLOUDFLARE_WORKERS_FREE_CONFIRMED")!="true":
        write("fallback","workers_free_not_confirmed",topic);return
    account=os.getenv("CLOUDFLARE_ACCOUNT_ID","").strip()
    token=os.getenv("CLOUDFLARE_AI_TOKEN","").strip()
    if not account or not token:write("fallback","workers_ai_credentials_missing",topic);return
    url="https://api.cloudflare.com/client/v4/accounts/"+account+"/ai/run/"+MODEL
    req=urllib.request.Request(url,method="POST",data=json.dumps({"prompt":prompt,"steps":4}).encode(),
         headers={"Authorization":"Bearer "+token,"Content-Type":"application/json",
                  "User-Agent":"SmartChoice365-Free-Article-Image/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=80) as r:result=json.load(r)
        encoded=(result.get("result") or {}).get("image")
        if result.get("success") is not True or not isinstance(encoded,str):raise ValueError("no_image")
        raw=base64.b64decode(encoded,validate=True)
        extension="jpg" if raw[:3]==bytes.fromhex("ffd8ff") else ("png" if raw[:8]==bytes.fromhex("89504e470d0a1a0a") else "")
        if not extension or not 20000<=len(raw)<=8000000:raise ValueError("invalid_image")
        with Image.open(io.BytesIO(raw)) as img:
            img.verify()
        with Image.open(io.BytesIO(raw)) as img:
            size=img.size
        if min(size)<768:raise ValueError("image_too_small")
        OUT.mkdir(parents=True,exist_ok=True)
        dest=OUT/(TODAY+"."+extension);dest.write_bytes(raw)
        write("ready","image_candidate_needs_editorial_review",topic,imagePath=dest.as_posix(),
             sha256=hashlib.sha256(raw).hexdigest(),imageBytes=len(raw),width=size[0],height=size[1],
             callsAttempted=1,researchCommitSha=obj["researchCommitSha"])
    except urllib.error.HTTPError as e:
        write("fallback","free_limit_or_rate_limit" if e.code==429 else "cloudflare_http_"+str(e.code),topic,
              callsAttempted=1,httpStatus=e.code)
    except (urllib.error.URLError,TimeoutError,ValueError,OSError,TypeError) as e:
        write("fallback","image_error_"+type(e).__name__,topic,callsAttempted=1)
def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as root:
        os.chdir(root)
        REQUEST.parent.mkdir(parents=True)
        REQUEST.write_text(json.dumps({"schemaVersion":1,"channel":"en-au","publishingDate":TODAY,
           "topicId":"fallback-test-guide","researchCommitSha":"0"*40,
           "scenePrompt":"Original high-quality editorial Australian household product scene, one complete appliance on a bright kitchen counter, realistic composition, no logos, watermark or brand labels, no text, no collage, no invented model markings."}))
        os.environ["CLOUDFLARE_WORKERS_FREE_CONFIRMED"]="false"
        run()
        data=json.loads(META.read_text())
        assert data["status"]=="fallback" and data["imagePath"] is None
        print("NO_COST_FALLBACK_TEST_OK")
if __name__=="__main__":
    selftest() if "--self-test" in sys.argv else run()
