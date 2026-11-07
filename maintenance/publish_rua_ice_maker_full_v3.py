#!/usr/bin/env python3
"""Publish exact owner-approved RUA Ice Maker V3 full guide once. No duplicate insert."""
import hashlib, json, os, pathlib, re, sys, time, urllib.parse
from publish_youtube_generic import api, receipt_read, receipt_write, CHANNEL
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from check_youtube import request_json

ID="rua-ice-maker-kokoro-full-v3-20261107"
FILE=pathlib.Path(__file__).resolve().parents[1]/"uploads"/"RUA_IceMaker_Kokoro_PreciseFocus_Stable_V3_NameCorrected.mp4"
SIZE=23336886
SHA256="c6ef8a3e98c3ca6dfabaedf2057d70898e6d9940a3e554a79750f49815c198d5"
RECEIPT="publications/receipts/"+ID+"-youtube.json"
TITLE="Ice Maker Buying Guide Australia 2026 | Bullet vs Nugget Ice | RUA & Smart Choice 365"
GUIDE="https://smartchoice365-web.pages.dev/guides/2026-ice-maker-australia-summer-bullet-vs-dispenser.html"
DESCRIPTION=f"""🧊 Compare ice makers and buying tips: {GUIDE}?utm_source=youtube&utm_medium=video&utm_campaign=rua_ice_maker_2026

RUA is back! Which countertop ice maker is right for your home?
We explain bullet vs nugget ice, daily claimed output vs basket storage, batch cycle, cleaning and bench clearance, and compare retailer-listed Kogan, Devanti and Heller examples.

00:00 RUA's ice maker adventure
00:08 Meet RUA and the buying guide
00:27 The five checks
00:43 What 12 kg/day really means
01:04 Bullet vs nugget ice
01:23 Cycle time and storage
02:46 Australian product comparisons
04:01 Side-by-side buying considerations
05:01 Final practical tips and RUA outro

This is a specification-based consumer guide, NOT a hands-on test. Listed specifications and prices may change. The product graphics are explanatory illustrations, not official retailer photographs. Check the latest specifications, stock, prices, and offers with each retailer.

Some shopping links in our buying guides are affiliate links. We may earn a commission if you purchase through them, at NO extra cost to you.

More RUA videos: https://www.youtube.com/channel/UC4DzAW-Hbd45bIECwGV7-uA
Smart Choice 365: https://smartchoice365-web.pages.dev/

#IceMaker #RUA #BuyingGuide #SmartChoice365 #Australia #NuggetIce"""
META={"snippet":{"title":TITLE,"description":DESCRIPTION,"categoryId":"26",
  "defaultLanguage":"en","defaultAudioLanguage":"en",
  "tags":["RUA","ice maker","nugget ice","bullet ice","Kogan","Devanti","Heller","Australia","Smart Choice 365","buying guide"]},
  "status":{"privacyStatus":"public","selfDeclaredMadeForKids":False,"containsSyntheticMedia":True,"embeddable":True,"license":"youtube"}}

def save(value):
    receipt_write(RECEIPT,value)
def main():
    if not FILE.is_file():
        raise RuntimeError("Missing exact owner-approved V3 video; do not publish.")
    raw=FILE.read_bytes();digest=hashlib.sha256(raw).hexdigest()
    if len(raw)!=SIZE or digest!=SHA256:
        raise RuntimeError("Video not identical to approved V3; publishing blocked.")
    if len(TITLE)>100 or len(DESCRIPTION)>5000:
        raise RuntimeError("Metadata too long.")
    previous,_=receipt_read(RECEIPT)
    if previous and (previous.get("sha256")!=digest or previous.get("id")!=ID):
        raise RuntimeError("Conflicting receipt.")
    if previous and not previous.get("video_id"):
        raise RuntimeError("Previous upload status uncertain. Inspect Studio; no duplicate.")
    creds={k:os.environ["YOUTUBE_"+k.upper()].strip() for k in ("client_id","client_secret","refresh_token")}
    if not all(creds.values()):
        raise RuntimeError("Missing existing YouTube OAuth secrets.")
    token=request_json("https://oauth2.googleapis.com/token",
        data=urllib.parse.urlencode({**creds,"grant_type":"refresh_token"}).encode())["access_token"]
    print("::add-mask::"+token,flush=True)
    channels=request_json("https://www.googleapis.com/youtube/v3/channels?part=id&mine=true",token=token)["items"]
    if [x.get("id") for x in channels]!=[CHANNEL]:
        raise RuntimeError("YouTube account mismatch.")
    receipt=previous
    if receipt:
        vid=receipt["video_id"]
        print("Existing published video receipt: checking, not reposting",flush=True)
    else:
        receipt={"id":ID,"sha256":digest,"channel_id":CHANNEL,"approval":"owner-approved chat 2026-11-07",
                 "platform":"youtube","format":"video","language":"en","status":"upload_initiated",
                 "run_id":os.environ.get("GITHUB_RUN_ID")}
        save(receipt)
        _,headers=api("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
           "POST",json.dumps(META,ensure_ascii=False).encode(),token,
           {"Content-Type":"application/json; charset=UTF-8",
            "X-Upload-Content-Length":str(len(raw)),"X-Upload-Content-Type":"video/mp4"})
        session=headers.get("Location","");address=urllib.parse.urlparse(session)
        if address.scheme!="https" or address.hostname!="www.googleapis.com" or not address.path.startswith("/upload/youtube/"):
            raise RuntimeError("Unexpected upload session, no retry.")
        video,_=api(session,"PUT",raw,token,{"Content-Type":"video/mp4"})
        vid=video.get("id","")
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}",vid):
            raise RuntimeError("Upload outcome uncertain, no duplicate.")
        receipt.update(video_id=vid,url="https://www.youtube.com/watch?v="+vid,status="uploaded_processing")
        save(receipt)
    for _ in range(24):
        items=request_json("https://www.googleapis.com/youtube/v3/videos?part=snippet,status,processingDetails&id="+vid,token=token).get("items",[])
        if items:
            v=items[0];status=v.get("status",{});snippet=v.get("snippet",{})
            ps=v.get("processingDetails",{}).get("processingStatus")
            if snippet.get("channelId")!=CHANNEL: raise RuntimeError("Channel mismatch.")
            if status.get("uploadStatus") in ("failed","rejected","deleted") or ps in ("failed","terminated"):
                receipt["status"]="processing_failed";save(receipt);raise RuntimeError("YouTube processing failure.")
            if status.get("uploadStatus")=="processed" and ps=="succeeded" and status.get("privacyStatus")=="public":
                if snippet.get("title")!=TITLE or snippet.get("description")!=DESCRIPTION:
                    raise RuntimeError("Published metadata mismatch, inspect video.")
                receipt.update(status="published_verified",title=TITLE,privacy="public",format="video",
                               metadata_verified=True,processing_status="succeeded",
                               description_first_line=DESCRIPTION.splitlines()[0])
                save(receipt);print("PUBLISHED_AND_VERIFIED "+receipt["url"],flush=True)
                return
        time.sleep(10)
    receipt["status"]="awaiting_processing_verification";save(receipt)
    raise RuntimeError("Processing unverified; do not repost.")
if __name__=="__main__":
    try: main()
    except (RuntimeError,KeyError,ValueError,OSError) as e:
        print("RUA_V3_FULL_PUBLISH_BLOCKED: "+str(e),file=sys.stderr)
        sys.exit(1)
