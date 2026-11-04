#!/usr/bin/env python3
"""Publish exact owner-approved RUA carbon mat short + official V2 10s outro.
One upload, no deletions, verify public status, prevent uncertain duplicate inserts.
"""
import hashlib,json,os,re,sys,time,urllib.parse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"maintenance"))
sys.path.insert(0,str(ROOT/"scripts"))
from publish_youtube_generic import api,receipt_read,receipt_write,CHANNEL
from recover_carbon_mats_ko import send_in_chunks,oauth
from check_youtube import request_json

ID="rua-carbon-mats-outro-short-20261104"
MEDIA=ROOT/"uploads"/"SC365_RUA_CarbonMat_Short_With_Official_Outro.mp4"
SHA="df15acab62215044de5975ed4077a8950fd474ed162abf75c325c572a941cd75"
SIZE=8614924
RECEIPT="publications/receipts/"+ID+"-youtube.json"
FULL_ID="fqM-5HCCRck"
FULL="https://www.youtube.com/watch?v="+FULL_ID
GUIDE="https://smartchoice365-web.pages.dev/guides/2026-electric-carbon-water-heating-mats.html?utm_source=youtube&utm_medium=shorts&utm_campaign=rua_carbon_mats"
CHANNEL_URL="https://www.youtube.com/channel/"+CHANNEL
TITLE="탄소매트 가격에 얼어버린 루아 😂｜비싼 게 정말 좋을까? #Shorts"
DESCRIPTION=(
    "🎬 탄소매트 vs 전기장판 vs 온수매트 본편: "+FULL+"\n"
    +"📊 상세 구매 비교 가이드: "+GUIDE+"\n\n"
    +"탄소매트 가격을 본 루아의 반응은? 🥶😂\n"
    +"재미있는 루아 쇼츠와 공식 Smart Choice 365 엔딩을 함께 즐겨주세요.\n"
    +"원본 쇼츠 음성은 영어이며, 자세한 구매 비교 본편은 한국어입니다.\n\n"
    +"스마트초이스365 공식 유튜브 채널: "+CHANNEL_URL+"\n\n"
    +"캐릭터·장면은 연출된 3D 애니메이션이며, 실제 제품 시험 영상은 아닙니다.\n"
    +"연결된 홈페이지 가이드에는 제휴 광고가 포함될 수 있습니다.\n"
    +"#스마트초이스365 #루아 #탄소매트 #전기장판 #온수매트 #Shorts"
)
META={
"snippet":{"title":TITLE,"description":DESCRIPTION,"categoryId":"26",
           "defaultLanguage":"ko","defaultAudioLanguage":"en",
           "tags":["스마트초이스365","루아","탄소매트","전기장판","온수매트","RUA","Smart Choice 365","Shorts"]},
"status":{"privacyStatus":"public","selfDeclaredMadeForKids":False,
          "containsSyntheticMedia":False,"embeddable":True,"license":"youtube"}
}
def save(r):receipt_write(RECEIPT,r)
def uploaded_preflight(token):
    channels=request_json("https://www.googleapis.com/youtube/v3/channels?part=id,contentDetails&mine=true",
                          token=token).get("items",[])
    if len(channels)!=1 or channels[0].get("id")!=CHANNEL:raise RuntimeError("Authenticated YouTube channel mismatch")
    playlist=channels[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    q=urllib.parse.urlencode({"part":"snippet,contentDetails","playlistId":playlist,"maxResults":50})
    items=request_json("https://www.googleapis.com/youtube/v3/playlistItems?"+q,token=token).get("items",[])
    for x in items:
        title=x.get("snippet",{}).get("title","")
        if title==TITLE:
            vid=x.get("snippet",{}).get("resourceId",{}).get("videoId","")
            raise RuntimeError("Matching short already exists, no duplicate: "+vid)
    print("SAFE_PREFLIGHT matched_channel=true recent_videos="+str(len(items))+" same_title=0",flush=True)
def main():
    if not MEDIA.is_file():raise RuntimeError("Approved composite MP4 not uploaded")
    raw=MEDIA.read_bytes()
    if len(raw)!=SIZE or hashlib.sha256(raw).hexdigest()!=SHA:
        raise RuntimeError("Composite MP4 differs from approved original/outro, refused")
    if len(TITLE)>100 or len(DESCRIPTION)>5000:raise RuntimeError("Metadata length overflow")
    current,_=receipt_read(RECEIPT)
    if current:
        if current.get("id")!=ID or current.get("sha256")!=SHA:
            raise RuntimeError("Conflicting receipt; duplicate stopped")
        vid=current.get("video_id")
        if not vid:
            raise RuntimeError("Previous upload uncertain; investigate before retrying")
    token=oauth()
    if not current:
        uploaded_preflight(token)
        current={"id":ID,"sha256":SHA,"platform":"youtube","approval":"owner requested RUA short with V2 signature ending before upload",
                 "channel_id":CHANNEL,"status":"upload_initiated","run_id":os.getenv("GITHUB_RUN_ID"),
                 "related_full_video_id":FULL_ID,"related_video_studio_status":"PENDING_MANUAL_BINDING",
                 "outro_sha256":"ae161a9dc3d34f705d67ca081cbb708d03e1a2778a4753e2a2ee413ce768b495"}
        save(current)
        _,headers=api("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                      "POST",json.dumps(META,ensure_ascii=False).encode(),token,
                      {"Content-Type":"application/json; charset=UTF-8",
                       "X-Upload-Content-Length":str(SIZE),"X-Upload-Content-Type":"video/mp4"})
        session=headers.get("Location","")
        parsed=urllib.parse.urlparse(session)
        if parsed.scheme!="https" or parsed.hostname!="www.googleapis.com" or not parsed.path.startswith("/upload/youtube/"):
            raise RuntimeError("Invalid resumable URL; possible upload pending, no new session")
        result=send_in_chunks(session,raw)
        vid=result.get("id","")
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}",vid):
            raise RuntimeError("Upload result uncertain; do not upload again")
        current.update(video_id=vid,url="https://www.youtube.com/shorts/"+vid,status="uploaded_processing")
        save(current)
    for _ in range(26):
        videos=request_json("https://www.googleapis.com/youtube/v3/videos?part=snippet,status,processingDetails&id="+vid,token=token).get("items",[])
        if videos:
            v=videos[0];st=v.get("status",{});s=v.get("snippet",{});p=v.get("processingDetails",{}).get("processingStatus")
            if s.get("channelId")!=CHANNEL:raise RuntimeError("Uploaded wrong channel")
            if st.get("uploadStatus") in ("failed","deleted","rejected") or p in ("failed","terminated"):
                current["status"]="processing_failed";save(current)
                raise RuntimeError("YouTube processing failed")
            if st.get("privacyStatus")=="public" and st.get("uploadStatus")=="processed" and p=="succeeded":
                if s.get("title")!=TITLE or s.get("description")!=DESCRIPTION:
                    raise RuntimeError("Saved title/description mismatch")
                current.update(status="published_verified",privacy="public",processing_status="succeeded",
                               metadata_verified=True,title=TITLE,language="en",format="shorts",
                               description_first_line=DESCRIPTION.splitlines()[0])
                save(current)
                print("PUBLISHED_VERIFIED "+current["url"],flush=True)
                print("RELATED_VIDEO_PENDING_YOUTUBE_STUDIO "+FULL,flush=True)
                return
        time.sleep(10)
    current["status"]="awaiting_processing_verification";save(current)
    raise RuntimeError("Public processing not verified, do not upload duplicate")
if __name__=="__main__":
    try:main()
    except (RuntimeError,ValueError,KeyError,OSError) as e:
        print("RUA_CARBON_MATS_SHORT_UPLOAD_BLOCKED: "+str(e),file=sys.stderr)
        sys.exit(1)
