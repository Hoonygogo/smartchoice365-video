#!/usr/bin/env python3
"""ONE-TIME owner-approved carbon mat Korean full-video upload. Do not re-encode, edit, or replace existing uploads."""
import hashlib, json, os, re, sys, time, urllib.parse
from pathlib import Path
from publish_youtube_generic import api, receipt_read, receipt_write, CHANNEL
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from check_youtube import request_json

ID="carbon-mats-ko-full-20261104"
MEDIA=Path(__file__).resolve().parents[1]/"uploads"/"SC365_CarbonMat_Korean_Full_Preview.mp4"
SIZE=5616343
SHA256="d8195e3f02a8ecf39a0f8e9fe059167095b65fa2fc56b6810cc3b7108a6c0946"
RECEIPT="publications/receipts/"+ID+"-youtube.json"
TITLE="탄소매트 vs 전기장판 vs 온수매트｜비싼 게 정말 더 좋을까? 실제 시험·전기요금 비교"
DESCRIPTION="""👉 탄소매트·전기장판·온수매트 구매 비교표와 전기요금 계산: https://smartchoice365-web.pages.dev/guides/2026-electric-carbon-water-heating-mats.html?utm_source=youtube&utm_medium=video&utm_campaign=carbon_mats_korean

루아처럼 비싼 탄소매트를 보고 고민됐나요? 실제 발열 구조부터 한국소비자원 탄소매트 10종 시험 결과, 전기요금 가상 계산, 관리·안전까지 차근차근 비교합니다.

⏱ 영상 구성
00:00 루아 쇼츠와 오늘의 질문
00:08 스마트초이스365 인사·화질 안내
00:26 전기장판·탄소매트·온수매트 구조 비교
00:51 한국소비자원 탄소매트 시험 결과
01:24 전기요금 계산 예시
01:53 안전·세탁·관리 확인
02:17 상황별 최종 구매 기준

📌 한국소비자원 2025-12-11 탄소전기매트 10종 품질 비교를 설명합니다. 시험 결과를 다른 종류의 매트와 직접 비교한 수치로 해석하지 않았습니다. 영상의 전기요금 계산은 가상 예시이며 직접 구매·성능 시험을 수행한 영상이 아닙니다.

참고 자료:
- https://www.chungbuk.go.kr/sobi/selectBbsNttView.do?bbsNo=218&key=1575&nttNo=323956&pageIndex=11&searchCnd=all&searchCtgry=&searchKrwd=
- https://www.kfcf.or.kr/news/news/read.do?no=3362

더 많은 비교 영상: https://www.youtube.com/channel/UC4DzAW-Hbd45bIECwGV7-uA

영상과 연결된 구매 가이드에는 쿠팡 파트너스 제휴 광고가 포함되어 있습니다. 해당 제휴 광고에 따른 수수료를 제공받으며, 고객에게 별도 제휴 수수료가 부과되지 않습니다.

#스마트초이스365 #탄소매트 #전기장판 #온수매트 #난방매트 #전기요금"""
META={
  "snippet":{"title":TITLE,"description":DESCRIPTION,"categoryId":"26",
   "defaultLanguage":"ko","defaultAudioLanguage":"ko",
   "tags":["스마트초이스365","탄소매트","전기장판","온수매트","난방매트","전기요금","구매가이드","Smart Choice 365"]},
  "status":{"privacyStatus":"public","selfDeclaredMadeForKids":False,
            "containsSyntheticMedia":True,"embeddable":True,"license":"youtube"}
}
def save(r):receipt_write(RECEIPT,r)
def main():
    if not MEDIA.exists():raise RuntimeError("Approved MP4 missing from uploads/; no YouTube action.")
    b=MEDIA.read_bytes()
    digest=hashlib.sha256(b).hexdigest()
    if len(b)!=SIZE or digest!=SHA256:raise RuntimeError("MP4 differs from the exact chat-approved copy. Upload blocked.")
    if not DESCRIPTION.startswith("👉 탄소매트·전기장판·온수매트 구매 비교표"):
        raise RuntimeError("Missing first-line buying-guide link.")
    if len(TITLE)>100 or len(DESCRIPTION)>5000:raise RuntimeError("YouTube metadata too long.")
    existing,_=receipt_read(RECEIPT)
    if existing:
        if existing.get("sha256")!=digest or existing.get("id")!=ID:
            raise RuntimeError("Conflicting receipt; duplicate blocked.")
        if not existing.get("video_id"):
            raise RuntimeError("Earlier attempt uncertain; inspect YouTube Studio. No duplicate.")
    creds={k:os.environ["YOUTUBE_"+k.upper()].strip() for k in ("client_id","client_secret","refresh_token")}
    if not all(creds.values()):raise RuntimeError("Missing existing YouTube OAuth credentials.")
    token=request_json("https://oauth2.googleapis.com/token",
        data=urllib.parse.urlencode({**creds,"grant_type":"refresh_token"}).encode())["access_token"]
    print("::add-mask::"+token,flush=True)
    channels=request_json("https://www.googleapis.com/youtube/v3/channels?part=id&mine=true",token=token)["items"]
    if [x.get("id") for x in channels]!=[CHANNEL]:raise RuntimeError("Authenticated channel mismatch.")
    r=existing
    if r:
        video_id=r["video_id"]
    else:
        r={"id":ID,"sha256":digest,"channel_id":CHANNEL,"approval":"published by owner on 2026-11-04",
           "platform":"youtube","format":"video","language":"ko",
           "status":"upload_initiated","run_id":os.environ.get("GITHUB_RUN_ID"),
           "note":"Explicit chat approval of exact Korean MP4; user accepted graph-led first video. Do not delete/replace."}
        save(r)  # duplicate lock before upload
        _,headers=api("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
            "POST",json.dumps(META,ensure_ascii=False).encode(),token,
            {"Content-Type":"application/json; charset=UTF-8",
             "X-Upload-Content-Length":str(len(b)),"X-Upload-Content-Type":"video/mp4"})
        session=headers.get("Location","");u=urllib.parse.urlparse(session)
        if u.scheme!="https" or u.hostname!="www.googleapis.com" or not u.path.startswith("/upload/youtube/"):
            raise RuntimeError("Unexpected upload endpoint; possible outcome uncertain.")
        response,_=api(session,"PUT",b,token,{"Content-Type":"video/mp4"})
        video_id=response.get("id","")
        if not re.fullmatch(r"[a-zA-Z0-9_-]{11}",video_id):
            raise RuntimeError("YouTube upload outcome uncertain; inspect Studio, no blind retry.")
        r.update(video_id=video_id,url="https://www.youtube.com/watch?v="+video_id,status="uploaded_processing")
        save(r)
    for i in range(24):
        items=request_json("https://www.googleapis.com/youtube/v3/videos?part=snippet,status,processingDetails&id="+video_id,
                          token=token).get("items",[])
        if items:
            item=items[0];st=item.get("status",{});snippet=item.get("snippet",{})
            pr=item.get("processingDetails",{}).get("processingStatus")
            if snippet.get("channelId")!=CHANNEL:raise RuntimeError("Channel mismatch.")
            if st.get("uploadStatus") in ("failed","rejected","deleted") or pr in ("failed","terminated"):
                r["status"]="processing_failed";save(r)
                raise RuntimeError("YouTube processing failed; media preserved; no duplicate.")
            if st.get("uploadStatus")=="processed" and pr=="succeeded" and st.get("privacyStatus")=="public":
                if snippet.get("title")!=TITLE or snippet.get("description")!=DESCRIPTION:
                    raise RuntimeError("Uploaded metadata differs from approved version.")
                r.update(status="published_verified",title=TITLE,language="ko",format="video",
                         privacy="public",processing_status="succeeded",metadata_verified=True,
                         description_first_line=DESCRIPTION.splitlines()[0])
                save(r)
                print("PUBLISHED_AND_VERIFIED: "+r["url"],flush=True)
                return
        time.sleep(10)
    r["status"]="awaiting_processing_verification";save(r)
    raise RuntimeError("Upload might have succeeded but public processing not confirmed; no duplicate.")
if __name__=="__main__":
  try:main()
  except (RuntimeError,KeyError,ValueError,OSError) as e:
    print("CARBON_MATS_UPLOAD_BLOCKED: "+str(e),file=sys.stderr);sys.exit(1)
