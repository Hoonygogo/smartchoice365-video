#!/usr/bin/env python3
"""Owner-approved CUCKOO 20L V4 full-length buyer guide. Upload once by exact GitHub upload trigger only."""
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.parse
from publish_youtube_generic import api, receipt_read, receipt_write, CHANNEL
from check_youtube import request_json

ROOT=Path(__file__).resolve().parents[1]
MEDIA=ROOT/"uploads"/"CUCKOO_V4.mp4"
SHA256="f61d6db7629f591ec681c40d06f0c738bebfa14fc02fbb1892d8aaae08528ef7"
SIZE=24665457
PUB_ID="rua-cuckoo-20l-v4-full-20261108"
RECEIPT=f"publications/receipts/{PUB_ID}-youtube.json"
REQUEST=json.loads((ROOT/"publications/requests/rua-cuckoo-20l-v4-full-20261108.json").read_text(encoding="utf-8"))
META=REQUEST["metadata"]
TITLE=META["snippet"]["title"]
DESCRIPTION=META["snippet"]["description"]

def save(record):
    receipt_write(RECEIPT,record)

def main():
    if (REQUEST.get("id")!=PUB_ID or REQUEST.get("sha256")!=SHA256 or REQUEST.get("size_bytes")!=SIZE or
        REQUEST.get("voice")!="Supertonic 3 Sarah/F1, speed 1.1, 8 steps" or REQUEST.get("approval")!="publish" or REQUEST.get("channel_id")!=CHANNEL or
        REQUEST.get("source")!="uploads/CUCKOO_V4.mp4"):
        raise RuntimeError("The approved exact-video request differs from the locked Sarah release.")
    if len(TITLE)>100 or len(DESCRIPTION)>5000:
        raise RuntimeError("YouTube metadata length invalid.")
    if not MEDIA.is_file():
        raise RuntimeError("The exact approved CUCKOO V4 long-form MP4 is missing from uploads/.")
    video=MEDIA.read_bytes()
    digest=hashlib.sha256(video).hexdigest()
    if len(video)!=SIZE or digest!=SHA256:
        raise RuntimeError("Sarah MP4 differs from the exact owner-approved bytes; publishing blocked.")
    for required in (
        "https://link.coupang.com/a/ivyZMMNjOe",
        "2026-cuckoo-cmw-a201dw-buying-value.html#selection-reasons",
        "고객을 위해 검토하고 엄선한 구매 링크",
        "쿠팡 파트너스", "별도의 제휴 수수료", "31,890원",
    ):
        if required not in DESCRIPTION:
            raise RuntimeError("Missing affiliate URL, vetted selection rationale or disclosure: "+required)
    if META["status"].get("containsSyntheticMedia") is not False:
        raise RuntimeError("Expected owner-reviewed nonrealistic 3D cartoon AI disclosure setting")
    if not 308.60 < REQUEST.get("duration_seconds",0) < 308.70 or REQUEST.get("format")!="video":
        raise RuntimeError("Wrong exact CUCKOO V4 long-form runtime or format")
    if "#Shorts" in TITLE or META["status"].get("privacyStatus")!="public":
        raise RuntimeError("This must be long-form, public with no #Shorts label.")
    old,_=receipt_read(RECEIPT)
    if old and (old.get("sha256")!=digest or old.get("id")!=PUB_ID):
        raise RuntimeError("Conflicting prior YouTube publication; avoid duplicate.")
    if old and not old.get("video_id"):
        raise RuntimeError("Earlier upload started but final result uncertain. Inspect YouTube Studio.")
    creds={name:os.environ["YOUTUBE_"+name.upper()].strip() for name in ("client_id","client_secret","refresh_token")}
    if not all(creds.values()):raise RuntimeError("Missing YouTube OAuth secrets.")
    token=request_json("https://oauth2.googleapis.com/token",
        data=urllib.parse.urlencode({**creds,"grant_type":"refresh_token"}).encode())["access_token"]
    print("::add-mask::"+token,flush=True)
    rows=request_json("https://www.googleapis.com/youtube/v3/channels?part=id&mine=true",token=token).get("items",[])
    if [r.get("id") for r in rows]!=[CHANNEL]:raise RuntimeError("YouTube authorized channel mismatch.")
    rec=old
    if rec:
        video_id=rec["video_id"];print("Existing upload receipt; verifying without repost.",flush=True)
    else:
        rec={"id":PUB_ID,"sha256":digest,"channel_id":CHANNEL,"approval":"owner_approved_CUCKOO_V4_exact_video",
             "platform":"youtube","format":"video","language":"ko","lang":"ko",
             "guide":"/guides/2026-cuckoo-cmw-a201dw-buying-value.html",
             "status":"upload_initiated","run_id":os.environ.get("GITHUB_RUN_ID")}
        save(rec)
        _,headers=api("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
            "POST",json.dumps(META,ensure_ascii=False).encode(),token,
            {"Content-Type":"application/json; charset=UTF-8","X-Upload-Content-Length":str(len(video)),
             "X-Upload-Content-Type":"video/mp4"})
        session=headers.get("Location","")
        u=urllib.parse.urlparse(session)
        if u.scheme!="https" or u.hostname!="www.googleapis.com" or not u.path.startswith("/upload/youtube/"):
            raise RuntimeError("Unexpected video upload session; no blind retry.")
        result,_=api(session,"PUT",video,token,{"Content-Type":"video/mp4"})
        video_id=result.get("id","")
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}",video_id):
            raise RuntimeError("YouTube upload outcome uncertain; do not duplicate.")
        rec.update(video_id=video_id,url="https://www.youtube.com/watch?v="+video_id,status="uploaded_processing")
        save(rec)
    for _ in range(36):
        items=request_json("https://www.googleapis.com/youtube/v3/videos?part=snippet,status,processingDetails&id="+video_id,token=token).get("items",[])
        if items:
            v=items[0];status=v.get("status",{});snippet=v.get("snippet",{});processing=v.get("processingDetails",{}).get("processingStatus")
            if snippet.get("channelId")!=CHANNEL:raise RuntimeError("Uploaded video channel mismatch.")
            if status.get("uploadStatus") in ("failed","rejected","deleted") or processing in ("failed","terminated"):
                rec["status"]="processing_failed";save(rec);raise RuntimeError("YouTube video processing failed.")
            if status.get("uploadStatus")=="processed" and processing=="succeeded" and status.get("privacyStatus")=="public":
                if snippet.get("title")!=TITLE or snippet.get("description")!=DESCRIPTION:
                    raise RuntimeError("Public metadata differs from approved shopping copy.")
                rec.update(status="published_verified",format="video",language="ko",lang="ko",
                     title=TITLE,privacy="public",processing_status="succeeded",metadata_verified=True,
                     description_first_line=DESCRIPTION.splitlines()[0])
                save(rec)
                print("PUBLISHED_AND_VERIFIED "+rec["url"],flush=True)
                return
        time.sleep(10)
    rec["status"]="awaiting_processing_verification";save(rec)
    raise RuntimeError("Upload may have completed but public processing is unverified. No duplicate retry.")
if __name__=="__main__":
    try:main()
    except (RuntimeError,KeyError,ValueError,OSError) as e:
        print("CUCKOO_V4_FULL_FAIL_CLOSED: "+str(e),file=sys.stderr);sys.exit(1)
