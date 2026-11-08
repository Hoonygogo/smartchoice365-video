#!/usr/bin/env python3
"""One-time, exact-byte YouTube long-form upload for approved RUA Qrevo L Pro 16:9 buyer guide."""
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
MEDIA=ROOT/"uploads"/"RUA_Qrevo_L_Pro_Full_Buying_Guide_1080p.mp4"
SHA256="2fc8b5ce5d9294b4746437973e5732eec0ef8985e0ed81a1edc232ac8731b3dc"
SIZE=14587506
PUB_ID="rua-qrevo-l-pro-full-20261108"
RECEIPT=f"publications/receipts/{PUB_ID}-youtube.json"
META=json.loads("{\"snippet\":{\"title\":\"로보락 Qrevo L Pro 사기 전 꼭 확인! 실구매가·후기·A/S 비교 | 루아 본영상\",\"description\":\"🔎 로보락 Qrevo L Pro, 왜 이 구매처를 엄선했을까요?\\n📋 가격·판매자·후기·A/S 검토 근거: https://smartchoice365-web.pages.dev/guides/2026-roborock-qrevo-l-pro-buying-value.html#selection-reasons\\n\\n✅ 네이버 쇼핑커넥트 · 엄선 구매처: https://naver.me/F05el04Z\\n✅ G마켓 링크프라이스 · 카드 할인 조건부 대안: https://bestmore.net/click.php?m=gmarket&a=A100708938&l=9999&l_cd1=3&l_cd2=0&tu=https%3A%2F%2Fitem.gmarket.co.kr%2FItem%3FgoodsCode%3D4822243340\\n\\n[광고·제휴 안내] 위 구매처는 네이버 쇼핑커넥트와 링크프라이스의 공식 발급 제휴 링크입니다. 해당 링크를 통한 구매가 발생하면 스마트초이스365가 판매처 또는 제휴 프로그램으로부터 수수료를 지급받습니다. 고객에게 별도의 제휴 수수료가 청구되지는 않습니다. 상품가격·배송비·결제 수수료 등 일반 구매비용은 별도입니다.\\n\\n🤖 루아의 청소 지옥 탈출 이야기로 시작해, 실제 제품 선택에서 꼭 확인할 성능·관리 편의성·가격·판매자·후기·A/S를 정리했습니다. 우리가 비교합니다. 고객은 절약합니다.\\n\\n📅 가격 비교 기준: 2026년 11월 8일 조사 당시\\n• 네이버: 519,000원 일반 표시가 / 기본 배송비 무료(배송지역·옵션에 따라 추가비 가능)\\n• G마켓: 530,160원 행사 쿠폰가 / 493,050원은 행사·대상 카드·스마일페이 조건 충족 시에만 적용되는 결제 할인가\\n• 네이버 포인트 적립은 현금 결제할인과 다르며, 개인별 혜택·적립 가능 여부는 별도로 확인해야 합니다.\\n전국 최저가를 보증하지 않으며 가격·재고·카드·쿠폰 조건은 바뀔 수 있습니다. 결제 직전에 판매처에서 최종 금액을 다시 확인하세요.\\n\\n⏱️ 영상 목차\\n00:00 루아의 청소 지옥 탈출\\n00:26 구매 전 확인할 세 가지\\n00:34 제조사 기준 핵심 기능\\n00:46 내 집에 맞지 않을 수 있는 경우\\n00:58 네이버·G마켓 실구매 조건 비교\\n01:14 적립 포인트와 현금 결제의 차이\\n01:26 판매자·후기·A/S 확인\\n01:40 어떤 가정에 맞을까?\\n01:52 엄선한 판매처를 추천하는 이유\\n02:05 설명란에서 비교하고 구매하기\\n02:17 루아 공식 엔딩\\n\\n🔎 제품 장단점 자세히 보기: https://smartchoice365-web.pages.dev/guides/2026-roborock-robot-vacuum-l-pro-pros-cons.html\\n🎬 관련 루아 쇼츠: https://www.youtube.com/shorts/KwhM7d6u2RA\\n📺 스마트초이스365 유튜브 채널: https://www.youtube.com/channel/UC4DzAW-Hbd45bIECwGV7-uA\\n\\n영상의 루아·로봇청소기는 창작 3D 애니메이션으로 실제 제품 시연이 아니며, 로봇의 모습은 실물과 다를 수 있습니다. 성능 표시는 제조사 자료를 바탕으로 하며 직접 제품 테스트 결과가 아닙니다. 로봇 제품 개념도는 실제 제품 사진이 아닙니다.\\n\\n제조사 제품 정보: https://kr.roborock.com/pages/roborock-qrevo-l-pro\\n\\n#로보락 #QrevoLPro #루아 #RUA #로봇청소기 #SmartChoice365 #구매가이드\",\"categoryId\":\"28\",\"defaultLanguage\":\"ko\",\"defaultAudioLanguage\":\"ko\",\"tags\":[\"로보락\",\"Qrevo L Pro\",\"RUA\",\"루아\",\"로봇청소기\",\"가격비교\",\"구매가이드\",\"네이버 쇼핑커넥트\",\"Smart Choice 365\"]},\"status\":{\"privacyStatus\":\"public\",\"selfDeclaredMadeForKids\":false,\"containsSyntheticMedia\":false,\"embeddable\":true,\"license\":\"youtube\"}}")
TITLE=META["snippet"]["title"]
DESCRIPTION=META["snippet"]["description"]

def save(record):
    receipt_write(RECEIPT,record)

def main():
    if len(TITLE)>100 or len(DESCRIPTION)>5000:
        raise RuntimeError("YouTube metadata length invalid.")
    if not MEDIA.is_file():
        raise RuntimeError("Approved RUA Qrevo 16:9 MP4 not uploaded. Nothing posted.")
    video=MEDIA.read_bytes()
    digest=hashlib.sha256(video).hexdigest()
    if len(video)!=SIZE or digest!=SHA256:
        raise RuntimeError("MP4 differs from checked full-video SHA256/size; blocked.")
    for required in ("https://naver.me/F05el04Z","https://bestmore.net/click.php?m=gmarket",
                     "2026-roborock-qrevo-l-pro-buying-value.html#selection-reasons",
                     "광고","제휴 수수료"):
        if required not in DESCRIPTION:
            raise RuntimeError("Missing vetted-link, related-guide or advertising disclosure: "+required)
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
        rec={"id":PUB_ID,"sha256":digest,"channel_id":CHANNEL,"approval":"upload-of-exact-owner-approved-main-video",
             "platform":"youtube","format":"video","language":"ko","lang":"ko",
             "guide":"/guides/2026-roborock-qrevo-l-pro-buying-value.html",
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
        print("QREVO_FULL_FAIL_CLOSED: "+str(e),file=sys.stderr);sys.exit(1)
