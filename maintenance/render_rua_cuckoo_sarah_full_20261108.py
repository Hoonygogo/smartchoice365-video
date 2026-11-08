#!/usr/bin/env python3
"""Render RUA Cuckoo Korean buyer's guide with locked Sarah/F1 narration and cue-accurate focus rectangles.
REVIEW DRAFT ONLY: never uploads to YouTube/Meta. Free Supertonic 3, fixed Korean F1 voice.
"""
from pathlib import Path
import hashlib, json, math, os, subprocess
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont
from supertonic import TTS

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"uploads/RUA_Cuckoo_20L_OfficialOutro_CuratedAffiliate_1080x1920.mp4"
OUT=ROOT/"renders/rua-cuckoo-sarah-20261108"
BUILD=ROOT/"build/rua-cuckoo-sarah-20261108"
OUT.mkdir(parents=True,exist_ok=True)
BUILD.mkdir(parents=True,exist_ok=True)
VIDEO=OUT/"RUA_Cuckoo_20L_Full_Sarah_Focus_1080p.mp4"
W,H=1920,1080
BG=(8,23,43); PANEL=(24,44,66); WHITE=(246,249,253)
GOLD=(250,194,82); SOFT=(174,194,215); GREEN=(104,225,179)
SCENES={
  "intro": [
    "스마트초이스365 구매가이드",
    "쿠쿠 20L, 가격만 보고 사도 될까?",
    [
      [
        "오늘의 핵심",
        "기본 데우기와 와우 가입 조건을 비교"
      ],
      [
        "1080p 화질 안내",
        "재생 설정에서 1080p 선택 가능 시 권장"
      ],
      [
        "구독 부탁드립니다",
        "고객의 구매 검색 시간을 줄이는 정보"
      ]
    ]
  ],
  "verdict": [
    "먼저 드리는 결론",
    "단순한 데우기 중심이라면 추천 후보",
    [
      [
        "1인 가구 · 기본 데우기",
        "밥·반찬·음료·기본 해동에 어울리는 20L"
      ],
      [
        "쉬운 다이얼 조작",
        "고주파 출력 700W · 기본형 전자레인지"
      ],
      [
        "큰 용기를 자주 쓴다면",
        "23~25L와 디지털 버튼식도 함께 비교"
      ]
    ]
  ],
  "specs": [
    "쿠쿠 공식 모델 사양",
    "출력과 크기까지 확인했어요",
    [
      [
        "고주파 출력 700W",
        "소비전력 1,050W와는 다른 수치"
      ],
      [
        "바깥 크기 440 × 341 × 258mm",
        "가로 × 깊이 × 높이 · 통풍 공간도 필요"
      ],
      [
        "조리실 305 × 297 × 215mm",
        "용기 폭·높이·회전 여유를 확인"
      ]
    ]
  ],
  "prices": [
    "2026년 11월 8일 가격 조사",
    "검색 표시가와 실제 결제액은 달라요",
    [
      [
        "쿠팡 검색 표시가 61,000원",
        "모든 고객의 최종 결제액으로 확정되지 않음"
      ],
      [
        "다나와 · 옥션 60,310원",
        "무료배송 표시 · 결제화면 실구매가 미검증"
      ],
      [
        "일반 구매자 확인할 것",
        "동일 옵션·판매자·배송비·할인 조건"
      ]
    ]
  ],
  "wow": [
    "와우 신규 가입 쿠폰",
    "조건부 혜택, 월회비까지 계산",
    [
      [
        "가입 쿠폰 표시가 24,000원",
        "확인 계정에 표시 · 누구나 적용되는 금액 아님"
      ],
      [
        "월회비 한 달 7,890원",
        "한 번만 내는 가입비가 아닌 정기요금"
      ],
      [
        "첫 달 부담 예시 31,890원",
        "24,000 + 7,890 · 쿠폰 대상자 가정"
      ]
    ]
  ],
  "seller": [
    "쿠팡 판매 상품을 확인한 이유",
    "가격뿐 아니라 판매 주체도 살폈어요",
    [
      [
        "판매 주체 ‘쿠팡’ 확인",
        "로켓배송 로고만으로 직접 판매 판단 안 함"
      ],
      [
        "최근 한 달 1만 명 이상 구매 표시",
        "상품 전체 화면 지표 · 판매자별 구분 안 됨"
      ],
      [
        "상품평 49,568개 표시",
        "조사 당시 기준 · 품질·고장률 보장 아님"
      ]
    ]
  ],
  "reviews": [
    "리뷰를 해석하는 기준",
    "확인하지 못한 부분도 공개합니다",
    [
      [
        "5점 81% · 4점 13%",
        "표시 비중 합계 94% · 반올림된 비율"
      ],
      [
        "개별 후기 본문 0건 읽음",
        "불만·장기 내구성·보상 후기 확인 못 함"
      ],
      [
        "제조사 A/S 1588-8899",
        "보증기간·반품 비용은 주문서에서 재확인"
      ]
    ]
  ],
  "vetted": [
    "고객을 위해 검토하고 엄선한 링크",
    "아무 제휴 상품이나 추천하지 않습니다",
    [
      [
        "동일 모델 · 옵션 연결 확인",
        "쿠팡 직접 발급 제휴 URL과 상품번호 확인"
      ],
      [
        "가격·판매 주체·리뷰 함께 검토",
        "일반가·가입 쿠폰가를 명확히 구분"
      ],
      [
        "선정 이유를 홈페이지에 공개",
        "확인 근거와 미확인 항목도 함께 안내"
      ]
    ]
  ],
  "cta": [
    "설명란에서 구매조건 확인",
    "검색은 저희가, 결정은 고객님이",
    [
      [
        "첫 번째 링크 · 자세한 구매가이드",
        "판매처를 고른 이유와 조건까지 정리"
      ],
      [
        "쿠팡 발급 제휴 구매 링크",
        "쿠폰 자격·배송비·최종 결제금액 재확인"
      ],
      [
        "광고 안내 · 고객 추가 수수료 없음",
        "구매 시 저희가 수수료를 받을 수 있음"
      ]
    ]
  ]
}
# Each spoken cue maps to exactly one matching, fixed-location highlight panel.
CUES=[
  [
    "intro",
    0,
    "안녕하세요, 스마트 초이스 삼육오입니다. 루아의 말하는 전자레인지 이야기를 보셨나요? 이제 쿠쿠 이십 리터 모델을 실제로 살 만한지 살펴보겠습니다."
  ],
  [
    "intro",
    1,
    "이 영상은 천팔십 피 화질로 제작했습니다. 재생 환경에서 지원하면 화질을 높여 보세요. 루아와 전자레인지는 실제 사용 장면이 아닌 창작 애니메이션입니다."
  ],
  [
    "intro",
    2,
    "가격과 판매자를 함께 비교한 구매가이드를 계속 보시려면 구독도 부탁드립니다. 이번엔 가입 쿠폰에 숨은 조건까지 살펴볼게요."
  ],
  [
    "verdict",
    0,
    "먼저 결론입니다. 밥이나 반찬, 음료를 데우고 기본 해동을 하는 것이 주목적이라면 이 쿠쿠 이십 리터 모델을 비교할 만합니다."
  ],
  [
    "verdict",
    1,
    "화려한 메뉴보다는 다이얼을 손으로 돌리는 간편한 방식이고, 제조사 안내 고주파 출력은 칠백 와트입니다."
  ],
  [
    "verdict",
    2,
    "하지만 큰 도시락이나 접시를 자주 쓰거나 시간을 초 단위로 입력하고 싶다면, 이십삼 리터 이상 버튼식 모델도 비교해 보세요."
  ],
  [
    "specs",
    0,
    "칠백 와트는 고주파 출력이고, 소비전력은 천오십 와트입니다. 서로 다른 숫자이니 더 큰 쪽을 조리 출력으로 착각하면 안 됩니다."
  ],
  [
    "specs",
    1,
    "공식 모델 안내에서 바깥 크기는 가로 사백사십, 깊이 삼백사십일, 높이 이백오십팔 밀리미터입니다. 설치할 때는 통풍 공간까지 확보하세요."
  ],
  [
    "specs",
    2,
    "조리실은 가로 삼백오, 깊이 이백구십칠, 높이 이백십오 밀리미터입니다. 평소 쓰는 용기가 회전하면서 들어가는지도 확인해 주세요."
  ],
  [
    "prices",
    0,
    "가격을 볼게요. 쿠팡 파트너스 검색에서 나온 육만 천 원은 일반 구매자 모두의 실제 결제금액으로 확인한 가격은 아닙니다."
  ],
  [
    "prices",
    1,
    "다나와에 표시된 옥션 가격은 육만 삼백십 원이었습니다. 무료배송으로 안내됐지만, 실제 주문서까지 검증한 가격은 아닙니다."
  ],
  [
    "prices",
    2,
    "그러니 일반 구매자라면 표시된 할인액만 믿지 말고, 동일 모델과 옵션의 실제 결제금액, 배송비, 판매자 정보를 다시 비교하세요."
  ],
  [
    "wow",
    0,
    "이제 와우 가입 쿠폰입니다. 조사 당시 이만 사천 원이 표시됐지만, 특정 가입 쿠폰 대상자만 받을 수 있는 조건부 가격입니다."
  ],
  [
    "wow",
    1,
    "월회비 칠천팔백구십 원도 봐야 합니다. 일회성 가입비가 아니라, 가입을 유지하면 이후에도 매달 청구될 수 있습니다."
  ],
  [
    "wow",
    2,
    "쿠폰 대상자가 첫 달 구매한다면 상품가 이만 사천 원에 한 달 회비를 더해 삼만 천팔백구십 원이 계산 예시입니다. 기존 와우 회원의 일반 할인가는 아닙니다."
  ],
  [
    "seller",
    0,
    "판매처도 확인했어요. 로켓배송이라고 무조건 쿠팡이 직접 판매하는 것은 아닙니다. 실제 선택 판매자 항목에서 쿠팡을 확인했습니다."
  ],
  [
    "seller",
    1,
    "해당 상품에는 최근 한 달 만 명 이상 구매했다는 표시가 있었어요. 다만 판매자별로 분리해 조사한 판매 수치는 아닙니다."
  ],
  [
    "seller",
    2,
    "상품평은 당시 사만 구천오백육십팔 개로 표시됐습니다. 규모가 큰 참고자료이지만, 서비스와 품질까지 보장하는 숫자는 아닙니다."
  ],
  [
    "reviews",
    0,
    "리뷰 화면의 분포는 오 점이 팔십일 퍼센트, 사 점이 십삼 퍼센트였습니다. 합계 구십사 퍼센트지만 반올림된 표시 비율입니다."
  ],
  [
    "reviews",
    1,
    "중요한 한계도 있습니다. 리뷰 본문을 불러오지 못해서 실제로 읽은 개별 후기는 영 건입니다. 고장 원인이나 내구성을 검증했다고 주장하지 않겠습니다."
  ],
  [
    "reviews",
    2,
    "쿠쿠전자 에이에스 연락처는 일오팔팔에 팔팔구구입니다. 보증기간과 실제 반품비, 사용 후 반품 가능 조건은 구매 화면에서 꼭 확인해 주세요."
  ],
  [
    "vetted",
    0,
    "스마트 초이스 삼육오는 아무 제휴 상품이나 추천하지 않습니다. 이번에도 쿠쿠 동일 모델과 옵션으로 연결되는 발급된 쿠팡 제휴 링크를 확인했습니다."
  ],
  [
    "vetted",
    1,
    "다른 판매처의 표시 가격과 비교하고, 판매 주체와 구매 기록, 리뷰 분포, 배송 조건을 확인했습니다. 그렇지만 전국 최저가를 보장하지 않습니다."
  ],
  [
    "vetted",
    2,
    "왜 이 구매처를 선정했는지 궁금하시다면 설명란의 엄선 구매추천 글을 확인하세요. 비교 근거뿐 아니라 못 확인한 항목도 적었습니다."
  ],
  [
    "cta",
    0,
    "영상 설명란 첫 번째 링크에서 가격 비교와 와우 가입 조건을 자세히 확인할 수 있습니다. 고객님의 검색 시간을 줄이도록 정리했어요."
  ],
  [
    "cta",
    1,
    "쿠팡 제품 제휴 링크도 설명란에 있습니다. 구매 전 쿠폰 대상 여부와 실제 판매자, 배송비, 최종 결제액을 확인해 주세요."
  ],
  [
    "cta",
    2,
    "이 영상은 쿠팡 파트너스 제휴 광고를 포함합니다. 구매가 발생하면 저희가 수수료를 받을 수 있지만, 고객님께 별도의 제휴 수수료는 청구되지 않습니다."
  ]
]
font_path="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
regular_path="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
def font(size,bold=True):
    return ImageFont.truetype(font_path if bold else regular_path,size)
def text(draw,xy,string,size,color=WHITE,bold=True):
    draw.text(xy,string,font=font(size,bold),fill=color)
def wrap(draw,s,size,max_width,max_lines=3):
    words=s.split(" ")
    lines=[];line=""
    for word in words:
        candidate=(line+" "+word).strip()
        if draw.textlength(candidate,font=font(size,False))<=max_width:
            line=candidate
        else:
            if line:lines.append(line)
            line=word
    if line:lines.append(line)
    return lines[:max_lines]
def slide(scene,focus,subtitle,file):
    eyebrow,title,items=SCENES[scene]
    im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
    d.rectangle((0,0,16,H),fill=GOLD)
    d.rounded_rectangle((1240,-230,2150,440),radius=200,fill=(17,34,54))
    d.rounded_rectangle((80,17,449,119),radius=20,fill=(246,249,253))
    logo=Image.open(ROOT/"assets/smartchoice365-brand-logo-v1.png").convert("RGBA")
    logo.thumbnail((348,95))
    im.paste(logo,(91+(348-logo.width)//2,20+(95-logo.height)//2),logo)
    text(d,(1480,65),"우리가 비교합니다. 고객은 절약합니다.",26,SOFT)
    d.line((83,129,1830,129),fill=(69,87,108),width=3)
    text(d,(92,163),eyebrow,28,GOLD)
    text(d,(91,220),title,64,WHITE)
    # Constant, precise row positions. Focus follows cue target, never ungrounded interpolation.
    for i,(heading,body) in enumerate(items):
        y=355+i*174
        active=(i==focus)
        d.rounded_rectangle((91,y,1828,y+148),radius=24,fill=((32,62,82) if active else PANEL),
                             outline=(GOLD if active else (65,84,103)),width=(7 if active else 2))
        if active:d.rounded_rectangle((107,y+20,117,y+127),radius=4,fill=GOLD)
        text(d,(151,y+15),heading,43,WHITE)
        text(d,(155,y+88),body,27,(GOLD if active else SOFT),False)
    d.rounded_rectangle((92,918,1828,1018),radius=19,fill=(10,30,51),outline=(57,78,100),width=2)
    for n,line in enumerate(wrap(d,subtitle,30,1645,max_lines=2)):
        text(d,(126,926+n*40),line,30,WHITE,False)
    d.line((82,1041,1840,1041),fill=(55,76,97),width=2)
    text(d,(96,1049),"2026.11.08 조사 기준 · 가격·판매자·쿠폰·회원비는 변동 가능 · 영상은 실물 시연 아닌 설명 자료",19,SOFT,False)
    im.save(file,optimize=True)
def sidebar(path,ending=False):
    im=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
    for x0,x1 in [(12,643),(1277,1907)]:
        d.rounded_rectangle((x0,12,x1,1068),radius=25,fill=(9,25,45,242))
    text(d,(76,94),"SMART",64,GOLD)
    text(d,(76,171),"CHOICE 365",47,WHITE)
    text(d,(75,333),"루아의",50,WHITE)
    text(d,(75,420),"구매 이야기" if not ending else "공식 엔딩",52,GOLD)
    text(d,(1340,124),"우리의 기준",52,GOLD)
    for i,phrase in enumerate(["기능과 한계","실제 결제금액","판매자·후기·A/S","엄선 구매처"]):
        text(d,(1340,270+i*95),phrase,37,WHITE)
    d.rounded_rectangle((1316,825,1853,970),radius=20,fill=(48,37,65,239))
    text(d,(1337,847),"창작 3D 애니메이션",29,WHITE)
    text(d,(1337,900),"실제 쿠쿠 제품 시연 아님",25,SOFT,False)
    im.save(path)
def run(cmd):
    subprocess.run(cmd,check=True)
def video_clip_from_source(out,ss,duration,overlay):
    cmd=["ffmpeg","-y","-hide_banner","-loglevel","error","-threads","2"]
    if ss:cmd.extend(["-ss",str(ss)])
    cmd.extend(["-i",str(SRC),"-loop","1","-i",str(overlay),"-f","lavfi","-i",
      "color=c=0x08172b:s=1920x1080:r=24",
      "-filter_complex","[0:v]scale=608:1080:flags=bicubic,setsar=1,format=yuv420p[v];[2:v][v]overlay=656:0:shortest=1[x];[x][1:v]overlay=0:0:shortest=1,format=yuv420p[out]",
      "-map","[out]","-map","0:a","-t",str(duration),"-c:v","libx264","-preset","veryfast","-crf","22",
      "-pix_fmt","yuv420p","-r","24","-g","48","-c:a","aac","-ar","48000","-ac","2",
      "-b:a","160k","-video_track_timescale","12288","-movflags","+faststart",str(out)])
    run(cmd)
def main():
    if not SRC.is_file():raise RuntimeError("Owner-approved original RUA cartoon not found")
    config=json.loads((ROOT/"config/approved_voices.json").read_text())["korean"]
    if (config["engine"],config["voice"],config["language"],config["speed"],config["steps"])!=("supertonic-3","Sarah/F1","ko",1.1,8):
        raise RuntimeError("Approved Sarah voice configuration differs; no fallback permitted")
    engine=TTS(model="supertonic-3",model_dir=".models/supertonic-3",auto_download=False,
               intra_op_num_threads=2,inter_op_num_threads=1)
    voice=engine.get_voice_style(voice_name="F1")
    sr=engine.sample_rate
    timeline=[];files=[]
    story_overlay=BUILD/"story_sidebar.png";outro_overlay=BUILD/"ending_sidebar.png"
    sidebar(story_overlay);sidebar(outro_overlay,True)
    story=BUILD/"000_story.mp4"
    video_clip_from_source(story,0,19.2,story_overlay)
    files.append(story)
    t=19.2
    subs=[]
    def stamp(sec):
        h=int(sec//3600);m=int(sec%3600//60);s=int(sec%60);ms=round((sec%1)*1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"
    for i,(scene,focus,spoken) in enumerate(CUES,1):
        wav,_=engine.synthesize(spoken,voice_style=voice,total_steps=8,speed=1.1,lang="ko")
        audio=np.asarray(wav,dtype=np.float32).reshape(-1)
        rms=float(np.sqrt(np.mean(audio**2)))
        if len(audio)<sr//2 or not np.isfinite(audio).all() or rms<0.008:
            raise RuntimeError(f"Sarah voice synthesis failed at cue {i}: RMS={rms}")
        gap=np.zeros(int(sr*0.28),dtype=np.float32)
        cue=np.concatenate((audio,gap))
        duration=len(cue)/sr
        image=BUILD/f"{i:03d}_{scene}.png";wave=BUILD/f"{i:03d}_{scene}.wav";clip=BUILD/f"{i:03d}_{scene}.mp4"
        slide(scene,focus,spoken,image);sf.write(wave,cue,sr)
        run(["ffmpeg","-y","-hide_banner","-loglevel","error","-threads","2",
             "-loop","1","-framerate","24","-i",str(image),"-i",str(wave),"-t",str(duration),
             "-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-r","24",
             "-g","48","-c:a","aac","-ar","48000","-ac","2","-b:a","160k",
             "-video_track_timescale","12288","-movflags","+faststart",str(clip)])
        files.append(clip)
        timeline.append({"cue":i,"scene":scene,"focus_card":focus+1,"start":round(t,3),
                         "end":round(t+duration,3),"spoken":spoken,"rms":round(rms,5)})
        subs.append(f"{i}\n{stamp(t)} --> {stamp(t+duration-0.1)}\n{spoken}")
        t+=duration
        print("SARAH_CUE",i,scene,focus+1,round(t,2),"s",flush=True)
    ending=BUILD/"999_official_outro.mp4"
    video_clip_from_source(ending,21.50,10.025,outro_overlay)
    files.append(ending)
    concat=BUILD/"concat.txt"
    concat.write_text("\n".join("file '"+str(f)+"'" for f in files)+"\n")
    run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",
         str(concat),"-c","copy","-movflags","+faststart",str(VIDEO)])
    probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(VIDEO)]))
    vs=[s for s in probe["streams"] if s["codec_type"]=="video"]
    au=[s for s in probe["streams"] if s["codec_type"]=="audio"]
    if len(vs)!=1 or len(au)!=1 or (vs[0]["width"],vs[0]["height"])!=(1920,1080):
        raise RuntimeError("Invalid final MP4 video/audio streams or dimensions")
    (OUT/"Sarah_Focus_Timings.json").write_text(json.dumps({
      "status":"review_only_unpublished","model":"Supertonic-3","voice":"Sarah/F1",
      "language":"ko","speed":1.1,"steps":8,"story_duration":19.2,
      "timeline":timeline,"total_seconds":float(probe["format"]["duration"]),
      "sha256":hashlib.sha256(VIDEO.read_bytes()).hexdigest(),
      "source_story":"owner-approved RUA CUCKOO two-part cartoon without bridge or outro","official_outro_reused":True,
      "notes":"Each cue's exact center-row focus box appears only during that cue's Sarah voice."
    },ensure_ascii=False,indent=2))
    (OUT/"Sarah_Focus_Captions.srt").write_text("\n\n".join(subs),encoding="utf-8")
    print("SUCCESS_SARAH_REVIEW",VIDEO,VIDEO.stat().st_size,probe["format"]["duration"],flush=True)
if __name__=="__main__":
    main()
