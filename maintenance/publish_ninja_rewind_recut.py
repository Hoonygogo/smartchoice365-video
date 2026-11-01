#!/usr/bin/env python3
"""Replace exactly one earlier approved Ninja Short with approved 11.83s recut.

Upload new to public, verify its processing and metadata, only then delete
old Short JgKqCXIvbKI. Related video remains a Studio-only manual step.
"""
import hashlib, json, os, re, sys, time, urllib.parse
from pathlib import Path
from publish_youtube_generic import api, receipt_read, receipt_write, CHANNEL
from check_youtube import request_json

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"uploads"/"SmartChoice365_Ninja_Rewind_AnimationOnly_Preview.mp4"
DIGEST="57e53c20fba073bd16ee36e06aa0720602d23aa71e86252056c92bd46cef8a3b"
SIZE=9249009
OLD_ID="JgKqCXIvbKI"
FULL_ID="2R5Nyt42hRs"
PUB_ID="ninja-rewind-animation-only-short-20261101"
RECEIPT="publications/receipts/"+PUB_ID+"-youtube.json"
GUIDE="https://smartchoice365-web.pages.dev/guides/2026-ninja-af141-vs-af400-australia-single-dual-basket.html"
META={
  "snippet":{
     "title":"Air Fryer Mistake? ⏪ Rewind Before You Buy! | Ninja AF141 vs AF400 #Shorts",
     "description":(
        "One tiny basket. Four hungry people. Time to REWIND! ⏪😅\n\n"
        "AF141 or AF400? Want to compare them properly? "
        "Tap the Related video below our channel name to watch our full Ninja buying guide.\n\n"
        "Full comparison: https://www.youtube.com/watch?v="+FULL_ID+"\n"
        "Australian guide: "+GUIDE+"\n\n"
        "Playful illustrated scenario, not hands-on testing or actual Ninja product photography. "
        "Check official specifications before choosing. The guide may contain disclosed affiliate links.\n\n"
        "#AirFryer #NinjaAirFryer #AF141 #AF400 #Shorts #SmartChoice365"
      ),
      "categoryId":"26","defaultLanguage":"en","defaultAudioLanguage":"en",
      "tags":["Ninja AF141","Ninja AF400","air fryer rewind","Ninja air fryer comparison",
              "Smart Choice 365","Australia","air fryer capacity"]
  },
  "status":{"privacyStatus":"public","selfDeclaredMadeForKids":False,
            "containsSyntheticMedia":True,"embeddable":True,"license":"youtube"}
}
def token():
  p={k:os.environ["YOUTUBE_"+k.upper()].strip()
     for k in ("client_id","client_secret","refresh_token")}
  p["grant_type"]="refresh_token"
  t=request_json("https://oauth2.googleapis.com/token",
       data=urllib.parse.urlencode(p).encode())["access_token"]
  print("::add-mask::"+t,flush=True)
  owners=request_json("https://www.googleapis.com/youtube/v3/channels?part=id&mine=true",
       token=t).get("items",[])
  if [x["id"] for x in owners]!=[CHANNEL]:raise RuntimeError("Wrong YouTube channel; nothing replaced")
  return t

def info(video_id,t,parts="snippet,status,processingDetails"):
  v=request_json("https://www.googleapis.com/youtube/v3/videos?part="+parts+"&id="+video_id,
      token=t).get("items",[])
  return v[0] if v else None

def write(r):
  receipt_write(RECEIPT,r)

def publish(media,t,r):
  write(r)
  _,headers=api(
      "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
      "POST",json.dumps(META,ensure_ascii=False).encode(),t,
      {"Content-Type":"application/json; charset=UTF-8",
       "X-Upload-Content-Length":str(len(media)),
       "X-Upload-Content-Type":"video/mp4"})
  session=headers.get("Location","")
  u=urllib.parse.urlparse(session)
  if u.scheme!="https" or u.hostname!="www.googleapis.com" or not u.path.startswith("/upload/youtube/"):
      raise RuntimeError("Unexpected YouTube resumable endpoint")
  result,_=api(session,"PUT",media,t,{"Content-Type":"video/mp4"})
  vid=result.get("id")
  if not vid or not re.fullmatch(r"[A-Za-z0-9_-]{11}",vid):
      raise RuntimeError("YouTube upload status unknown: check Studio, duplicate locked")
  r.update(video_id=vid,url="https://www.youtube.com/shorts/"+vid,status="uploaded_processing")
  write(r)
  return vid

def verify(vid,t,r):
  for attempt in range(36):
      new=info(vid,t)
      if new:
          if new["snippet"].get("channelId")!=CHANNEL:
              raise RuntimeError("New video belongs to wrong channel; old retained")
          status=new["status"]
          p=new.get("processingDetails",{}).get("processingStatus")
          if status.get("uploadStatus") in ("rejected","failed","deleted") or p in ("failed","terminated"):
              r["status"]="processing_failed";write(r)
              raise RuntimeError("New Short processing failed; old retained")
          if (status.get("uploadStatus")=="processed" and p=="succeeded"
              and status.get("privacyStatus")=="public"):
              if (new["snippet"].get("title")!=META["snippet"]["title"] or
                  new["snippet"].get("description")!=META["snippet"]["description"]):
                  raise RuntimeError("New metadata differs from approved text; old retained")
              r.update(status="published_verified",metadata_verified=True,
                       privacy="public",processing_status="succeeded")
              write(r)
              return
      time.sleep(10)
  r["status"]="awaiting_processing_verification";write(r)
  raise RuntimeError("New Short not yet verified; old retained, retry safe")

def cleanup_old(vid,t,r):
  if r.get("old_short_cleanup",{}).get("status")=="deleted_verified":return
  assert vid!=OLD_ID and r["status"]=="published_verified" and r["metadata_verified"]
  new=info(vid,t)
  if not new or new["status"].get("privacyStatus")!="public" or new["snippet"].get("channelId")!=CHANNEL:
      raise RuntimeError("New Short is not public on correct channel; old retained")
  old=info(OLD_ID,t,"snippet")
  if old:
      title=old["snippet"].get("title","")
      if old["snippet"].get("channelId")!=CHANNEL or not ("AF141" in title.upper() and "AF400" in title.upper()):
          raise RuntimeError("Old Short identity unexpected; leave it intact")
      # Never delete a different Short and never delete before verified replacement
      try:
          api("https://www.googleapis.com/youtube/v3/videos?id="+OLD_ID,"DELETE",token=t)
      except RuntimeError as e:
          r["old_short_cleanup"]={"id":OLD_ID,"status":"deletion_uncertain","reason":str(e)}
          write(r)
          raise
  for attempt in range(8):
      if not info(OLD_ID,t,"id"):
          r["old_short_cleanup"]={"id":OLD_ID,"status":"deleted_verified"}
          write(r)
          print("NEW SHORT PUBLIC AND OLD SHORT DELETED: "+r["url"],flush=True)
          return
      time.sleep(5)
  r["old_short_cleanup"]={"id":OLD_ID,"status":"deletion_not_verified"}
  write(r)
  raise RuntimeError("Deletion of old Short could not yet be verified")

def main():
  if not FILE.is_file():raise RuntimeError("Approved recut MP4 missing from GitHub uploads/")
  media=FILE.read_bytes()
  if len(media)!=SIZE or hashlib.sha256(media).hexdigest()!=DIGEST:
      raise RuntimeError("Approved recut SHA-256/size mismatch: nothing published/deleted")
  t=token()
  r,_=receipt_read(RECEIPT)
  if r:
      if r.get("id")!=PUB_ID or r.get("sha256")!=DIGEST:
          raise RuntimeError("Conflicting receipt; no duplicate upload")
      vid=r.get("video_id")
      if not vid:raise RuntimeError("Prior upload outcome uncertain; inspect Studio")
  else:
      r={"id":PUB_ID,"sha256":DIGEST,"channel_id":CHANNEL,"platform":"youtube",
         "approval":"publish","approval_note":"Owner explicitly approved replacing prior Short with 11.83-second recut",
         "run_id":os.environ.get("GITHUB_RUN_ID"),
         "status":"upload_initiated","replaces_short_id":OLD_ID,
         "full_video_id":FULL_ID,
         "related_video_status":"requires_youtube_studio_manual_selection",
         "related_video_instruction":"In Studio choose Related video: Ninja AF141 vs AF400 V4 (2R5Nyt42hRs)"}
      vid=publish(media,t,r)
  if r.get("status")!="published_verified":verify(vid,t,r)
  cleanup_old(vid,t,r)

if __name__=="__main__":
  try:main()
  except (RuntimeError,KeyError,OSError,ValueError) as e:
      print(str(e) if isinstance(e,RuntimeError) else "Publication blocked, previous Short retained",file=sys.stderr)
      sys.exit(1)
