#!/usr/bin/env python3
"""Smart Choice 365: approved cross-posting to Instagram and Facebook Reels.

Runs on the existing GitHub Actions runner, using a public commit-pinned media
URL and Meta's official Graph API. Never uses paid services, unofficial scraping,
browser passwords, token printing, or blind retries of ambiguous publications.

A publication request does NOT authorize posts until META_PUBLISH_ENABLED=true
and the channel-specific secrets are provisioned by the account owner.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from publish_youtube_generic import receipt_read, receipt_write

ROOT = Path(__file__).resolve().parents[1]
REPO = "Hoonygogo/smartchoice365-video"
API = "https://graph.facebook.com/v26.0"
CHANNEL = "UC4DzAW-Hbd45bIECwGV7-uA"
EXPECTED_PLATFORMS = {"instagram", "facebook"}

def fail(message):
    raise RuntimeError(message)

def json_request(url, *, method="GET", form=None, headers=None, data=None):
    if data is None and form is not None:
        data = urllib.parse.urlencode(form).encode("utf-8")
    h = {"Accept": "application/json", "User-Agent": "SmartChoice365-Meta-Reels/1.0"}
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=85) as res:
            raw = res.read()
            answer = json.loads(raw) if raw else {}
            if isinstance(answer, dict) and answer.get("error"):
                fail("Meta returned an error; no blind retry.")
            return answer
    except urllib.error.HTTPError as exc:
        fail(f"Meta API HTTP {exc.code}; inspect the platform receipt, never retry blindly")
    except (urllib.error.URLError, TimeoutError, ValueError):
        fail("Meta request outcome uncertain; inspect destination before any retry")

def checked_file(req):
    relative = Path(req["media_path"])
    if (relative.is_absolute() or ".." in relative.parts
            or not relative.parts or relative.parts[0] != "uploads"
            or relative.suffix.lower() != ".mp4"):
        fail("Only approved MP4 files under uploads/ may be distributed.")
    file = (ROOT / relative).resolve()
    if not file.is_relative_to(ROOT) or not file.is_file():
        fail("Approved public MP4 is missing from GitHub.")
    raw = file.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if req.get("sha256") != digest:
        fail("Media SHA-256 does not match the approved publication request.")
    if not 100000 < len(raw) <= 1024 * 1024 * 1024:
        fail("Unexpected video size.")
    ffprobe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams",
         "-of", "json", str(file)], check=True, capture_output=True,
        text=True, timeout=35)
    data = json.loads(ffprobe.stdout)
    vids = [s for s in data["streams"] if s.get("codec_type") == "video"]
    auds = [s for s in data["streams"] if s.get("codec_type") == "audio"]
    if len(vids) != 1 or len(auds) != 1 or vids[0].get("codec_name") != "h264" or auds[0].get("codec_name") != "aac":
        fail("Meta publishing requires a validated H264/AAC MP4.")
    w, h = vids[0]["width"], vids[0]["height"]
    duration = float(data["format"]["duration"])
    if w < 540 or h < 960 or abs(w / h - 9/16) > 0.015 or not (4 <= duration <= 60):
        fail("File must be 9:16 portrait, >=540x960, 4-60 sec for both platforms.")
    if not 23 <= float(vids[0].get("avg_frame_rate", "0/1").split("/")[0]) / max(1,float(vids[0].get("avg_frame_rate","0/1").split("/")[-1])) <= 60:
        fail("Unsupported frame rate.")
    commit = os.environ.get("GITHUB_SHA", "")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        fail("A GitHub commit SHA is required for stable public media URL.")
    url = f"https://raw.githubusercontent.com/{REPO}/{commit}/{relative.as_posix()}"
    # Meta fetches a URL itself, not the local GitHub Actions runner.
    # Verify the URL is globally accessible without authentication.
    probe = urllib.request.Request(url, method="HEAD",
       headers={"User-Agent": "SmartChoice365-Public-Asset-Check/1.0"})
    try:
        with urllib.request.urlopen(probe, timeout=35) as r:
            if r.status != 200:
                fail("Media is not publicly accessible to Meta.")
            length = r.headers.get("Content-Length")
            if length is not None and int(length) != len(raw):
                fail("Public media bytes differ from approved MP4.")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        fail("Public media URL unavailable; no publication attempted.")
    return url, {"duration":round(duration,3),"width":w,"height":h,"size":len(raw)}

def validate_request():
    p = Path(os.environ.get("META_REQUEST_FILE", ""))
    if (not p.parts or p.parts[:2] != ("publications", "meta-requests")
            or p.suffix != ".json" or ".." in p.parts):
        fail("Provide a request under publications/meta-requests/ only.")
    req = json.loads((ROOT / p).read_text(encoding="utf-8"))
    identity = req.get("id")
    if not isinstance(identity, str) or not re.fullmatch(r"[a-z0-9-]{5,96}", identity):
        fail("Invalid media publication ID.")
    if req.get("approval") not in ("prepare", "publish") or req.get("channel_id") != CHANNEL:
        fail("Approval must be prepare/publish and destination must match Smart Choice 365.")
    target = req.get("platforms")
    if not isinstance(target, list) or not target or len(target) != len(set(target)) or not set(target) <= EXPECTED_PLATFORMS:
        fail("Specify Instagram/Facebook destination platforms explicitly.")
    for name in target:
        caption = req.get("captions", {}).get(name, "")
        if not isinstance(caption, str) or not 10 <= len(caption) <= 1800:
            fail("Missing or overlong platform-specific caption.")
        if "smartchoice365-web.pages.dev" not in caption:
            fail("Each caption must mention the related Smart Choice 365 guide.")
    full_id = req.get("full_video_id", "")
    if not isinstance(full_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{11}", full_id):
        fail("The exact approved full-length YouTube video ID is required.")
    for platform in target:
        if "https://www.youtube.com/watch?v=" + full_id not in req["captions"][platform]:
            fail("Each platform caption must reference the approved matching YouTube video.")
    return req

def token_for(platform):
    key = "META_PAGE_ACCESS_TOKEN"
    value = os.environ.get(key, "").strip()
    if not value:
        fail("Missing META_PAGE_ACCESS_TOKEN GitHub Actions secret.")
    return value

def preflight_identity(req, token):
    page = os.environ.get("META_FACEBOOK_PAGE_ID", "").strip()
    ig = os.environ.get("META_INSTAGRAM_ACCOUNT_ID", "").strip()
    if not page.isdigit():
        fail("Missing META_FACEBOOK_PAGE_ID (the Facebook Page, not your personal profile).")
    if "instagram" in req["platforms"] and not ig.isdigit():
        fail("Missing META_INSTAGRAM_ACCOUNT_ID (professional Instagram account).")
    fields = "id,name" + (",instagram_business_account" if "instagram" in req["platforms"] else "")
    info = json_request(
        API+"/"+page+"?"+urllib.parse.urlencode({"fields":fields}),
        headers={"Authorization":"Bearer "+token})
    if str(info.get("id")) != page:
        fail("Page token does not identify the approved Facebook Page.")
    if "instagram" in req["platforms"] and str((info.get("instagram_business_account") or {}).get("id","")) != ig:
        fail("Instagram professional account is not linked to the approved Facebook Page.")
    return page, ig

def request_record(req, platform, digest, *, url, size):
    path = f"publications/meta-receipts/{req['id']}-{platform}.json"
    old, _ = receipt_read(path)
    if old:
        if old.get("sha256") != digest or old.get("platform") != platform:
            fail("Conflicting existing receipt; no duplicate publication.")
    else:
        old = {"id":req["id"],"platform":platform,"sha256":digest,
               "video_source_url":url,"video_size":size,
               "status":"ready","approval":"publish",
               "channel_id":CHANNEL,"run_id":os.environ.get("GITHUB_RUN_ID")}
        receipt_write(path,old)
    return path, old

def update(path, record, **kwargs):
    record.update(kwargs)
    receipt_write(path, record)

def instagram(req, page_token, account_id, media_url, path, r):
    if r.get("status") == "published_verified":
        return
    container = r.get("container_id")
    if not container:
        if r.get("status") != "ready":
            fail("Instagram container creation previously uncertain; no blind retry.")
        update(path,r,status="container_creation_initiated")
        created = json_request(API+"/"+account_id+"/media",method="POST",form={
            "media_type":"REELS", "video_url":media_url,
            "caption":req["captions"]["instagram"],
            "share_to_feed":"true",
            "access_token":page_token})
        container=str(created.get("id",""))
        if not container.isdigit():
            fail("Instagram container creation uncertain; check the receipt.")
        update(path,r,status="container_processing",container_id=container)
    for _ in range(30):
        state=json_request(API+"/"+container+"?fields=status_code,status",
                           headers={"Authorization":"Bearer "+page_token})
        status=state.get("status_code")
        if status=="FINISHED":break
        if status in ("ERROR","EXPIRED"):
            update(path,r,status="container_failed")
            fail("Instagram container processing failed; no publish.")
        time.sleep(8)
    else:
        fail("Instagram container still processing; safe retry may resume status polling.")
    if r.get("media_id"):
        media_id=r["media_id"]
    else:
        if r.get("status") == "media_publish_initiated":
            fail("Instagram publish outcome uncertain. Inspect account before retry.")
        update(path,r,status="media_publish_initiated")
        result=json_request(API+"/"+account_id+"/media_publish",method="POST",form={
            "creation_id":container,"access_token":page_token})
        media_id=str(result.get("id",""))
        if not media_id.isdigit():
            fail("Instagram publish uncertain; inspect account before retry.")
        update(path,r,status="published_unverified",media_id=media_id)
    item=json_request(API+"/"+media_id+"?fields=id,media_type,permalink,caption",
                      headers={"Authorization":"Bearer "+page_token})
    if str(item.get("id")) != media_id or item.get("media_type") != "VIDEO" or not item.get("permalink"):
        fail("Instagram post not yet fully verified.")
    if item.get("caption","").strip() != req["captions"]["instagram"].strip():
        fail("Instagram published caption differs from approved content.")
    update(path,r,status="published_verified",permalink=item["permalink"])
    print("IG_REEL_VERIFIED "+item["permalink"],flush=True)

def facebook(req, page_token, page_id, url, path, r):
    if r.get("status") == "published_verified":return
    video_id=r.get("video_id")
    if not video_id:
        if r.get("status") != "ready":
            fail("Facebook upload session earlier uncertain; do not start a second.")
        update(path,r,status="start_initiated")
        session=json_request(API+"/"+page_id+"/video_reels",method="POST",form={
            "upload_phase":"start","access_token":page_token})
        video_id=str(session.get("video_id",""))
        upload_url=session.get("upload_url","")
        parsed=urllib.parse.urlparse(upload_url)
        if not video_id.isdigit() or parsed.scheme!="https" or parsed.hostname!="rupload.facebook.com":
            fail("Unexpected Facebook Reel upload endpoint.")
        update(path,r,status="session_created",video_id=video_id,upload_url=upload_url)
    if r.get("status")=="session_created":
        update(path,r,status="transfer_initiated")
        result=json_request(r["upload_url"],method="POST",headers={
            "Authorization":"OAuth "+page_token,"file_url":url})
        if result.get("success") is not True:
            fail("Facebook hosted Reel transfer response uncertain.")
        update(path,r,status="transfer_complete")
    if r.get("status")=="transfer_initiated":
        fail("Facebook upload transfer uncertain; inspect before retry.")
    if r.get("status")=="transfer_complete":
        update(path,r,status="finish_initiated")
        result=json_request(API+"/"+page_id+"/video_reels",method="POST",form={
            "upload_phase":"finish","video_id":video_id,
            "video_state":"PUBLISHED",
            "description":req["captions"]["facebook"],
            "title":req.get("facebook_title","Smart Choice 365"),
            "access_token":page_token})
        if result.get("success") is not True:
            fail("Facebook Reel publish outcome uncertain.")
        update(path,r,status="published_unverified")
    if r.get("status")=="finish_initiated":
        fail("Facebook Reel publish response was uncertain. Inspect before retry.")
    for _ in range(20):
        item=json_request(API+"/"+video_id+"?fields=id,status,permalink_url",
                          headers={"Authorization":"Bearer "+page_token})
        status=item.get("status",{})
        if str(item.get("id"))==video_id and isinstance(status,dict):
            processing=(status.get("processing_phase") or {}).get("status","")
            posting=(status.get("publishing_phase") or {}).get("status","")
            state=status.get("video_status","")
            if processing=="error" or posting=="error":
                update(path,r,status="processing_failed")
                fail("Facebook video processing failed.")
            if (processing=="complete" and posting=="complete") or state in ("ready","published"):
                link=item.get("permalink_url")
                update(path,r,status="published_verified",permalink=link or "",
                       platform_video_id=video_id)
                print("FB_REEL_VERIFIED "+str(link or video_id),flush=True)
                return
        time.sleep(8)
    update(path,r,status="published_unverified")
    fail("Facebook upload finished but final public status not yet verified.")

def main():
    req=validate_request()
    url,stats=checked_file(req)
    if os.environ.get("META_PUBLISH_ENABLED","").lower()!="true":
        print(json.dumps({"dry_run":True,"validation":"PASSED",
                          "platforms":req["platforms"],"media":stats,
                          "note":"META_PUBLISH_ENABLED not true. Nothing posted."},ensure_ascii=False))
        return
    if req.get("approval") != "publish":
        fail("Publishing not owner-approved: request is prepare-only.")
    token=token_for("facebook")
    page_id, ig_account=preflight_identity(req,token)
    media_digest=req["sha256"]
    for platform in req["platforms"]:
        receipt_path,record=request_record(req,platform,media_digest,url=url,size=stats["size"])
        if platform=="instagram":
            instagram(req,token,ig_account,url,receipt_path,record)
        else:
            facebook(req,token,page_id,url,receipt_path,record)

if __name__=="__main__":
    try:
        main()
    except (RuntimeError,KeyError,ValueError,OSError,subprocess.CalledProcessError) as e:
        print("META_CROSSPOST_FAIL_CLOSED: "+(str(e) if isinstance(e,RuntimeError) else "media/config error"),file=sys.stderr)
        sys.exit(1)
