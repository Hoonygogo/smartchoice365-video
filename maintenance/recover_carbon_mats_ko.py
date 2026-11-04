#!/usr/bin/env python3
"""One-time approved recovery for ambiguous YouTube HTTP 502 during Korean carbon mat upload.

Safety: exact-media hash, current-channel and uploaded-video preflight, one permitted
recovery attempt after owner checked YouTube Studio, resumable chunked upload with
status probes. Never create a second upload session after an uncertain attempt.
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from publish_carbon_mats_ko import ID, MEDIA, SIZE, SHA256, RECEIPT, META, TITLE, DESCRIPTION
from publish_youtube_generic import api, receipt_read, receipt_write, CHANNEL
from check_youtube import request_json

CHUNK_BYTES=1024*1024
def upload_request(session,data,range_value):
    parsed=urllib.parse.urlparse(session)
    if parsed.scheme!="https" or parsed.hostname!="www.googleapis.com" or not parsed.path.startswith("/upload/youtube/"):
        raise RuntimeError("Unsafe resumable upload location.")
    headers={"Content-Type":"video/mp4","Content-Length":str(len(data)),
             "Content-Range":range_value}
    request=urllib.request.Request(session,data=data,headers=headers,method="PUT")
    try:
        with urllib.request.urlopen(request,timeout=90) as response:
            body=response.read()
            payload=json.loads(body) if body else {}
            return response.status,dict(response.headers.items()),payload
    except urllib.error.HTTPError as exc:
        if exc.code==308:
            return 308,dict(exc.headers.items()),{}
        if exc.code in (500,502,503,504):
            return exc.code,{},{}
        raise RuntimeError("Resumable YouTube upload HTTP "+str(exc.code)+"; no new session created.") from None
    except (urllib.error.URLError,TimeoutError,ValueError) as exc:
        return 599,{},{}

def accepted_end(headers):
    val=headers.get("Range") or headers.get("range")
    if not val:
        return -1
    m=re.fullmatch(r"bytes=0-(\\d+)",val.strip())
    if not m:
        raise RuntimeError("Unexpected resumable status Range.")
    return int(m.group(1))

def probe(session,size):
    return upload_request(session,b"",f"bytes */{size}")

def send_in_chunks(session,media):
    length=len(media)
    offset=0
    for number in range(30):
        if offset>=length:  # Last chunk must return a video id, not just 308.
            status,headers,body=probe(session,length)
            if status in (200,201):
                return body
            raise RuntimeError("All bytes reported sent but YouTube video ID not confirmed; no new upload session.")
        end=min(offset+CHUNK_BYTES,length)-1
        status,headers,body=upload_request(session,media[offset:end+1],f"bytes {offset}-{end}/{length}")
        if status in (200,201):
            if not body.get("id"):
                raise RuntimeError("No YouTube video ID in completion; do not retry upload.")
            return body
        if status==308:
            confirmed=accepted_end(headers)
            new_offset=confirmed+1 if confirmed>=0 else 0
            if new_offset<=offset and offset>0:
                raise RuntimeError("YouTube did not advance bytes; avoid repeating uncertain transfer.")
            offset=new_offset
            print(f"UPLOAD_PROGRESS confirmed_bytes={offset}/{length}",flush=True)
            continue
        if status in (500,502,503,504,599):
            # Check same resumable session: do not create a second session.
            time.sleep(2)
            result,h,b=probe(session,length)
            if result in (200,201) and b.get("id"):
                return b
            if result==308:
                end_seen=accepted_end(h)
                offset=end_seen+1 if end_seen>=0 else 0
                print(f"UPLOAD_RESUME_AFTER_ERROR status={status} confirmed_bytes={offset}/{length}",flush=True)
                continue
            raise RuntimeError("YouTube transfer uncertain after "+str(status)+"; no duplicate or new session.")
        raise RuntimeError("Unexpected YouTube transfer status "+str(status))
    raise RuntimeError("Exceeded safe resumable-upload attempts; no duplicate.")

def oauth():
    cred={k:os.environ["YOUTUBE_"+k.upper()].strip() for k in ("client_id","client_secret","refresh_token")}
    if not all(cred.values()):
        raise RuntimeError("Missing YouTube credentials.")
    result=request_json("https://oauth2.googleapis.com/token",
         data=urllib.parse.urlencode({**cred,"grant_type":"refresh_token"}).encode())
    token=result.get("access_token")
    if not token:raise RuntimeError("No YouTube access token.")
    print("::add-mask::"+token,flush=True)
    return token

def youtube_preflight(token):
    channels=request_json("https://www.googleapis.com/youtube/v3/channels?part=id,contentDetails&mine=true",
                          token=token).get("items",[])
    if len(channels)!=1 or channels[0].get("id")!=CHANNEL:
        raise RuntimeError("YouTube channel mismatch.")
    playlist=channels[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    qs=urllib.parse.urlencode({"part":"snippet,contentDetails","playlistId":playlist,"maxResults":50})
    vids=request_json("https://www.googleapis.com/youtube/v3/playlistItems?"+qs,token=token).get("items",[])
    for v in vids:
        title=v.get("snippet",{}).get("title","")
        if title==TITLE or ("탄소매트" in title and "온수매트" in title):
            vid=v.get("snippet",{}).get("resourceId",{}).get("videoId")
            raise RuntimeError("A potentially matching YouTube video already exists: "+str(vid)+"; new upload blocked.")
    print("READ_ONLY_PREFLIGHT verified_channel=true scanned_recent="+str(len(vids))+" matches=0",flush=True)

def save(x):
    receipt_write(RECEIPT,x)

def main():
    if not MEDIA.is_file():
        raise RuntimeError("Approved Korean MP4 missing.")
    b=MEDIA.read_bytes()
    if len(b)!=SIZE or hashlib.sha256(b).hexdigest()!=SHA256:
        raise RuntimeError("Approved MP4 SHA256/size mismatch.")
    r,_=receipt_read(RECEIPT)
    if not r or r.get("id")!=ID or r.get("sha256")!=SHA256:
        raise RuntimeError("Expected original failed-upload receipt not found.")
    if r.get("video_id"):
        raise RuntimeError("Existing receipt already has video ID; do not upload a duplicate.")
    if r.get("status")!="upload_initiated" or str(r.get("run_id"))!="41809954727":
        raise RuntimeError("Recovery already attempted or original receipt changed; no further uploads.")
    token=oauth()
    youtube_preflight(token)  # User independently confirmed absent from Studio after original error.
    r.update(status="recovery_attempt_initiated",recovery_of_run_id="41809954727",
             recovery_run_id=os.getenv("GITHUB_RUN_ID"),original_error="HTTP 502",
             owner_verified_studio_absent=True,recovery_method="resumable_1MiB_chunks")
    save(r)  # One-time lock before creating a session.
    _,headers=api("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                  "POST",json.dumps(META,ensure_ascii=False).encode(),token,
                  {"Content-Type":"application/json; charset=UTF-8",
                   "X-Upload-Content-Length":str(SIZE),"X-Upload-Content-Type":"video/mp4"})
    session=headers.get("Location","")
    if not session:
        raise RuntimeError("No resumable-session URL; do not retry blindly.")
    result=send_in_chunks(session,b)
    vid=result.get("id","")
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}",vid):
        raise RuntimeError("No valid video ID; no duplicate.")
    r.update(video_id=vid,url="https://www.youtube.com/watch?v="+vid,status="uploaded_processing")
    save(r)
    for n in range(28):
        vids=request_json("https://www.googleapis.com/youtube/v3/videos?part=snippet,status,processingDetails&id="+vid,
                          token=token).get("items",[])
        if vids:
            v=vids[0]
            s=v.get("status",{});sn=v.get("snippet",{});p=v.get("processingDetails",{}).get("processingStatus")
            if sn.get("channelId")!=CHANNEL:
                raise RuntimeError("YouTube channel mismatch after upload.")
            if s.get("uploadStatus") in ("failed","rejected","deleted") or p in ("failed","terminated"):
                r["status"]="processing_failed";save(r)
                raise RuntimeError("YouTube rejected or failed processing. No duplicates.")
            if s.get("privacyStatus")=="public" and s.get("uploadStatus")=="processed" and p=="succeeded":
                if sn.get("title")!=TITLE or sn.get("description")!=DESCRIPTION:
                    raise RuntimeError("Saved public metadata differs from approved title/description.")
                r.update(status="published_verified",privacy="public",
                    title=TITLE,language="ko",format="video",processing_status="succeeded",
                    metadata_verified=True,description_first_line=DESCRIPTION.splitlines()[0])
                save(r)
                print("PUBLISHED_AND_VERIFIED "+r["url"],flush=True)
                return
        time.sleep(10)
    r["status"]="awaiting_processing_verification";save(r)
    raise RuntimeError("YouTube processing not yet verified; no duplicate.")
if __name__=="__main__":
    try:
        main()
    except (RuntimeError,KeyError,ValueError,OSError) as exc:
        print("RECOVERY_BLOCKED: "+str(exc),file=sys.stderr)
        sys.exit(1)
