#!/usr/bin/env python3
"""Publish only the owner-approved 30s Omni Korean interview, cleaned captions.
Reuses tested hash-locked uploader, resumable transfer and duplicate protection.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"maintenance"))
import publish_rua_carbon_mats_short as p

p.ID="rua-heating-mat-interview-omni-cleaned-20261104"
p.MEDIA=ROOT/"uploads"/"SC365_RUA_HeatingMat_Interview_Omni_30s_Cleaned.mp4"
p.SHA="f725e6ac68353286a22f973a81371adae6361e8387ba43c9f04337efc68a8795"
p.SIZE=8854463
p.RECEIPT="publications/receipts/"+p.ID+"-youtube.json"
p.TITLE="루아의 난방매트 면접 대참사 😂 탄소매트·전기장판·온수매트 #Shorts"
p.DESCRIPTION=(
    "🎬 본편에서 탄소매트·전기장판·온수매트 비교하기: "+p.FULL+"\n"
    +"📊 스마트초이스365 상세 구매 가이드: "+p.GUIDE+"\n\n"
    +"난방매트 세 친구가 면접장에?! 루아의 한국어 코믹 애니메이션 😂\n"
    +"본편에서 난방 방식과 장단점을 비교해 보세요.\n\n"
    +"스마트초이스365 공식 채널: "+p.CHANNEL_URL+"\n"
    +"3D 애니메이션 연출 장면이며 실제 제품 시험 영상은 아닙니다.\n"
    +"연결된 홈페이지 가이드에는 제휴 광고가 포함될 수 있습니다.\n"
    +"#스마트초이스365 #루아 #탄소매트 #전기장판 #온수매트 #Shorts"
)
p.META["snippet"].update({"title":p.TITLE,"description":p.DESCRIPTION,
                           "defaultLanguage":"ko","defaultAudioLanguage":"ko"})
p.META["status"]["privacyStatus"]="public"
if __name__=="__main__":
    p.main()
