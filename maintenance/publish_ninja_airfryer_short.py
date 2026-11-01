#!/usr/bin/env python3
"""Upload the owner-approved Ninja short with CTA; do not claim Related Video is set.

YouTube Data API does not expose the Shorts Related Video Studio field.
Requires a one-time manual Studio selection after verified publication.
"""
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
MP4=ROOT/"uploads"/"SmartChoice365_Ninja_Shorts_RelatedVideo_CTA.mp4"
SHA256="57a0721fc4381bb5f60071fa9c3a529d963d08ff9d3c7629e3e679001ee1c0ce"
SHORT_ID="ninja-airfryer-tiny-basket-short-cta-20261101"
RECEIPT="publications/receipts/"+SHORT_ID+"-youtube.json"
FULL="https://www.youtube.com/watch?v=2R5Nyt42hRs"
GUIDE="https://smartchoice365-web.pages.dev/guides/2026-ninja-af141-vs-af400-australia-single-dual-basket.html"
METADATA={
    "snippet":{
        "title":"Air Fryer Too Small? 4 People, 1 Tiny Basket 😂 | Ninja AF141 vs AF400 #Shorts",
        "description":(
            "One small basket. Four hungry people. Too many batches! 😅\n\n"
            "Want the real Ninja AF141 vs AF400 comparison? "
            "Tap RELATED VIDEO below our channel name to watch our full buying guide.\n\n"
            "Full video: "+FULL+"\n"
            "Australian buying guide: "+GUIDE+"\n\n"
            "This short is a playful illustrated scenario, not hands-on product testing. "
            "Product specifications, capacity and prices should be verified before purchasing. "
            "The guide may contain clearly disclosed affiliate links.\n\n"
            "#AirFryer #NinjaAirFryer #AF141 #AF400 #Shorts #SmartChoice365"
        ),
        "categoryId":"26",
        "defaultLanguage":"en",
        "defaultAudioLanguage":"en",
        "tags":["Ninja AF141","Ninja AF400","air fryer capacity","air fryer mistakes",
                "Smart Choice 365","Australia","air fryer short"],
    },
    "status":{
        "privacyStatus":"public",
        "selfDeclaredMadeForKids":False,
        "embeddable":True,
        "license":"youtube",
    }
}

def token_and_channel():
    info={key:os.environ["YOUTUBE_"+key.upper()].strip()
          for key in ("client_id","client_secret","refresh_token")}
    info["grant_type"]="refresh_token"
    tok=request_json("https://oauth2.googleapis.com/token",
                     data=urllib.parse.urlencode(info).encode())["access_token"]
    print("::add-mask::"+tok,flush=True)
    channels=request_json("https://www.googleapis.com/youtube/v3/channels?part=id&mine=true",
                          token=tok).get("items",[])
    if [item["id"] for item in channels]!=[CHANNEL]:
        raise RuntimeError("OAuth channel is not Smart Choice 365")
    return tok

def video_info(token,vid):
    rows=request_json("https://www.googleapis.com/youtube/v3/videos?part=snippet,status,processingDetails&id="+vid,
                      token=token).get("items",[])
    return rows[0] if rows else None

def main():
    if not MP4.is_file():raise RuntimeError("Approved short MP4 has not been uploaded to GitHub yet.")
    data=MP4.read_bytes()
    if len(data)!=7939869 or hashlib.sha256(data).hexdigest()!=SHA256:
        raise RuntimeError("Approved short video SHA-256/size mismatch; do not upload alternate version")
    tok=token_and_channel()
    record,_=receipt_read(RECEIPT)
    if record:
        if record.get("sha256")!=SHA256:
            raise RuntimeError("Existing publication receipt refers to a different short")
        vid=record.get("video_id")
        if not vid:
            raise RuntimeError("Earlier YouTube insert outcome uncertain; inspect Studio; duplicate blocked")
    else:
        record={
            "id":SHORT_ID,"sha256":SHA256,"channel_id":CHANNEL,
            "approval":"publish","status":"upload_initiated","platform":"youtube",
            "run_id":os.environ.get("GITHUB_RUN_ID"),
            "full_video_id":"2R5Nyt42hRs",
            "related_video_status":"requires_youtube_studio_manual_selection",
            "related_video_instruction":"YouTube Studio > Content > Shorts > Short > Related video > Ninja AF141 vs AF400 (2R5Nyt42hRs) > Save"
        }
        receipt_write(RECEIPT,record)
        _,headers=api("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                      "POST",json.dumps(METADATA,ensure_ascii=False).encode(),tok,
                      {"Content-Type":"application/json; charset=UTF-8",
                       "X-Upload-Content-Length":str(len(data)),
                       "X-Upload-Content-Type":"video/mp4"})
        url=headers.get("Location","")
        parsed=urllib.parse.urlparse(url)
        if parsed.scheme!="https" or parsed.hostname!="www.googleapis.com" or not parsed.path.startswith("/upload/youtube/"):
            raise RuntimeError("Unexpected YouTube upload endpoint")
        result,_=api(url,"PUT",data,tok,{"Content-Type":"video/mp4"})
        vid=result.get("id")
        if not vid or not re.fullmatch(r"[A-Za-z0-9_-]{11}",vid):
            raise RuntimeError("YouTube upload result uncertain; receipt prevents duplicates")
        record.update(video_id=vid,url="https://www.youtube.com/shorts/"+vid,status="uploaded_processing")
        receipt_write(RECEIPT,record)
    for attempt in range(36):
        v=video_info(tok,vid)
        if v:
            if v["snippet"].get("channelId")!=CHANNEL:
                raise RuntimeError("Short published to wrong YouTube channel")
            status=v["status"]
            processing=v.get("processingDetails",{}).get("processingStatus")
            if status.get("uploadStatus") in ("failed","rejected","deleted") or processing in ("failed","terminated"):
                record["status"]="processing_failed"
                receipt_write(RECEIPT,record)
                raise RuntimeError("YouTube shorts processing failed")
            if (status.get("uploadStatus")=="processed" and processing=="succeeded"
                    and status.get("privacyStatus")=="public"):
                if (v["snippet"].get("title")!=METADATA["snippet"]["title"]
                        or v["snippet"].get("description")!=METADATA["snippet"]["description"]):
                    raise RuntimeError("YouTube saved metadata mismatch")
                record.update(status="published_verified",processing_status="succeeded",
                              privacy="public",metadata_verified=True,
                              related_video_status="requires_youtube_studio_manual_selection")
                receipt_write(RECEIPT,record)
                print(json.dumps(record,ensure_ascii=False),flush=True)
                return
        time.sleep(10)
    record["status"]="awaiting_processing_verification"
    receipt_write(RECEIPT,record)
    raise RuntimeError("Short uploaded but processing unconfirmed; do not upload duplicate")

if __name__=="__main__":
    try:main()
    except (RuntimeError,KeyError,OSError) as e:
        print(str(e) if isinstance(e,RuntimeError) else "Shorts publishing failed",file=sys.stderr)
        sys.exit(1)
