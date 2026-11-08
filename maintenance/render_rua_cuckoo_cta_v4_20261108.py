#!/usr/bin/env python3
"""Render a targeted V4 CTA replacement only. No social/public posting.
Approved voice: Supertonic 3 Sarah/F1 ko speed=1.1 steps=8.
"""
from pathlib import Path
import json, hashlib, subprocess
import numpy as np
import soundfile as sf
from supertonic import TTS
from render_rua_cuckoo_sarah_sales_v2_20261108 import ROOT, Image, slide, SCENES

OUT=ROOT/"renders"/"rua-cuckoo-cta-v4-20261108"
OUT.mkdir(parents=True, exist_ok=True)
SCENES["cta"]=(
    "엄선 구매추천 · 스마트초이스365",
    "고객의 시간과 돈을 아끼는 구매 링크",
    [
        ("아무 제휴 상품이나 추천하지 않습니다","동일 모델·판매자·가격·고객 후기·쿠폰 조건 검토"),
        ("선정 이유를 공개합니다","검색 시간을 줄이고 불필요한 지출을 피하도록 도움"),
        ("구매하실 땐 엄선한 링크로 응원해 주세요","고객 추가 제휴 수수료 없음 · 다음 조사에 힘이 됩니다"),
    ]
)
CUES=[
    "스마트 초이스 삼육오의 제휴 링크는 아무 상품이나 올린 링크가 아닙니다. 같은 모델인지, 실제 판매자는 누구인지, 다른 판매처 가격과 고객 후기, 쿠폰 조건까지 확인하고 엄격한 기준으로 골랐습니다.",
    "고객님이 여러 쇼핑몰을 돌아다니지 않고도 현명하게 선택하도록, 비교 결과와 선정 이유를 공개합니다. 시간을 줄이고 불필요한 지출을 아끼실 수 있게 돕는 것이 저희의 목표입니다.",
    "오늘 정보가 도움이 되었고 구매를 결정하셨다면, 설명란의 엄선한 쿠팡 제휴 링크로 구매해 스마트 초이스 삼육오를 응원해 주세요. 구매 시 저희가 제휴 수수료를 받을 수 있지만, 고객님께 추가로 청구되는 비용은 없습니다. 여러분의 응원은 다음 제품 조사와 영상 제작에 큰 힘이 됩니다."
]
def main():
    config=json.loads((ROOT/"config/approved_voices.json").read_text())["korean"]
    if (config["engine"],config["voice"],config["language"],config["speed"],config["steps"]) != ("supertonic-3","Sarah/F1","ko",1.1,8):
        raise RuntimeError("Voice parameters mismatch. No substitution allowed.")
    engine=TTS(model="supertonic-3",model_dir=".models/supertonic-3",auto_download=False,intra_op_num_threads=2,inter_op_num_threads=1)
    voice=engine.get_voice_style(voice_name="F1")
    timeline=[]
    for i,spoken in enumerate(CUES,1):
        wave,_=engine.synthesize(spoken,voice_style=voice,total_steps=8,speed=1.1,lang="ko")
        a=np.asarray(wave,dtype=np.float32).reshape(-1)
        rms=float(np.sqrt(np.mean(a*a)))
        if not np.isfinite(a).all() or len(a)<engine.sample_rate//2 or rms<0.008:
            raise RuntimeError("Missing/invalid original Sarah Korean voice at cue "+str(i))
        a=np.concatenate((a, np.zeros(int(engine.sample_rate*0.28),dtype=np.float32)))
        duration=len(a)/engine.sample_rate
        wav=OUT/f"{i:02d}_Sarah.wav"
        img=OUT/f"{i:02d}_Focus.png"
        mp4=OUT/f"{i:02d}_Sarah_Focus.mp4"
        sf.write(wav,a,engine.sample_rate)
        slide("cta",i-1,spoken,img)
        subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error",
            "-loop","1","-framerate","24","-i",str(img),"-i",str(wav),
            "-t",str(duration),"-c:v","libx264","-preset","veryfast","-crf","20",
            "-pix_fmt","yuv420p","-r","24","-g","48","-keyint_min","48",
            "-c:a","aac","-ar","48000","-ac","2","-b:a","160k",
            "-movflags","+faststart",str(mp4)],check=True)
        timeline.append({"index":i,"spoken":spoken,"duration":duration,"rms":rms,"filename":mp4.name,
                         "sha256":hashlib.sha256(mp4.read_bytes()).hexdigest()})
        print("V4_SARAH_CTA",i,"secs",round(duration,3),"RMS",round(rms,5),flush=True)
    (OUT/"manifest.json").write_text(json.dumps({"status":"draft_unpublished","voice":"Sarah/F1","engine":"Supertonic-3",
        "speed":1.1,"steps":8,"language":"ko","timeline":timeline},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":
    main()
