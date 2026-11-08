#!/usr/bin/env python3
# Evidence: GS SHOP CMW-A201DW https://www.gsshop.com/prd/prd.gs?lsectid=1660668&lseq=405302&prdid=51842028 (284 reviews, 4.5/5; 79% design, 68% convenience, displayed 2026-11-08).
# Official manufacturer: https://www.cuckoo.co.kr/mall/productView?productNo=3902 (20L, 700W, dials, A/S).
# Product-level Coupang demand indicators are from the verified 2026-11-08 Smart Choice 365 published buying guide; user-specific prices must be verified at checkout.
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
OUT=ROOT/"renders/rua-cuckoo-sales-v2-20261108"
BUILD=ROOT/"build/rua-cuckoo-sales-v2-20261108"
OUT.mkdir(parents=True,exist_ok=True)
BUILD.mkdir(parents=True,exist_ok=True)
VIDEO=OUT/"RUA_Cuckoo_20L_Full_Convincing_Sarah_V2_1080p.mp4"
W,H=1920,1080
BG=(8,23,43); PANEL=(24,44,66); WHITE=(246,249,253)
GOLD=(250,194,82); SOFT=(174,194,215); GREEN=(104,225,179)
SCENES={
  "fit": [
    "이런 분께 자신 있게 추천",
    "기본 데우기용이라면 쿠쿠 20L부터",
    [
      [
        "자취·1인 가구에 잘 맞는 구성",
        "밥·반찬·음료 데우기와 기본 해동에 집중"
      ],
      [
        "조작은 간편하게, 기본은 탄탄하게",
        "20L · 다이얼 2개 · 고주파 출력 700W"
      ],
      [
        "쿠쿠전자 공식 모델 · A/S 경로 확인",
        "2019년 출시 · 공식 고객센터 1588-8899"
      ]
    ]
  ],
  "demand": [
    "많이 선택된 이유부터 확인",
    "쿠팡 페이지의 강력한 구매 지표",
    [
      [
        "최근 한 달 1만 명 이상 구매 표시",
        "2026.11.08 조사 당시 상품 페이지 기준"
      ],
      [
        "상품평 49,568개 표시",
        "여러 판매자 상품평을 포함할 수 있는 상품 단위 집계"
      ],
      [
        "선택 판매자 ‘쿠팡’ 확인",
        "로켓배송 표지만이 아닌 실제 판매자 항목 확인"
      ]
    ]
  ],
  "review": [
    "이번에는 실제 후기까지 확인",
    "다른 판매처의 사용자 평가도 검토",
    [
      [
        "GS SHOP 본사직영 페이지 · 284건",
        "해당 페이지의 같은 모델 리뷰 평점 4.5 / 5"
      ],
      [
        "디자인 긍정 79% · 편리성 긍정 68%",
        "리뷰 화면의 항목별 평가 지표"
      ],
      [
        "간편한 조작·화이트 디자인 호평",
        "실제 후기에는 초 단위 조절이 아쉽다는 의견도"
      ]
    ]
  ],
  "price": [
    "일반 구매가부터 비교했어요",
    "싸다는 말보다 결제 조건이 중요",
    [
      [
        "쿠팡 파트너스 표시 기준 61,000원",
        "모든 고객의 최종 결제금액은 아님"
      ],
      [
        "다나와 · 옥션 표시가 60,310원",
        "무료배송 표시 · 당시 검색 가격"
      ],
      [
        "가격이 비슷하다면 판매자도 확인",
        "동일 옵션·배송비·쿠폰 조건으로 비교"
      ]
    ]
  ],
  "wow": [
    "와우 가입 쿠폰을 받을 수 있다면",
    "이번 비교에서 가장 눈에 띄는 혜택",
    [
      [
        "대상자에게 표시된 상품 쿠폰가 24,000원",
        "신규 가입 쿠폰 대상 조건 · 모든 고객 적용 아님"
      ],
      [
        "와우 회비 한 달 7,890원",
        "이후 계속 가입하면 매월 청구될 수 있음"
      ],
      [
        "첫 달 계산 예시 31,890원",
        "상품 24,000원 + 월회비 7,890원"
      ]
    ]
  ],
  "choice": [
    "그래서 결론은?",
    "이 조건이라면 이 제품부터 추천합니다",
    [
      [
        "밥·반찬 데우기가 주 용도라면",
        "20L 다이얼 모델의 단순함이 장점"
      ],
      [
        "구매 지표·판매자·다른 몰 후기 검토",
        "구매량 표시와 실제 사용자 평가 확인"
      ],
      [
        "가입 쿠폰 대상이라면 더 매력적",
        "첫 달 회비 포함 총액을 보고 결정"
      ]
    ]
  ],
  "cta": [
    "선택은 편하게 · 링크는 검토해서",
    "스마트초이스365 엄선 구매추천",
    [
      [
        "설명란 맨 위 · 검증 근거 공개",
        "가격 비교·판매 주체·리뷰·와우 조건 정리"
      ],
      [
        "쿠팡 제휴 구매 링크도 준비",
        "동일 모델 확인 · 실제 쿠폰·결제조건 재확인"
      ],
      [
        "고객에게 추가 제휴 수수료 없음",
        "제휴 구매 시 운영자가 수수료를 받을 수 있음"
      ]
    ]
  ]
}
# Each spoken cue maps to exactly one matching, fixed-location highlight panel.
CUES=[
  [
    "fit",
    0,
    "밥이나 반찬 데우는 일이 주로 필요하다면, 저는 이 쿠쿠 이십 리터부터 비교해 보시라고 추천합니다. 쓰지 않을 복잡한 기능보다 꼭 필요한 데우기에 집중한 모델이니까요."
  ],
  [
    "fit",
    1,
    "다이얼 두 개로 조절하는 간편한 방식에, 이십 리터 용량과 칠백 와트 고주파 출력. 전자레인지를 복잡하게 사용하지 않는 분에게 특히 실용적입니다."
  ],
  [
    "fit",
    2,
    "쿠쿠전자가 안내하는 정식 모델이고, 이천십구 년부터 판매된 제품입니다. 공식 고객센터와 에이에스 안내가 명확한 것도 구매할 때 고려할 장점이죠."
  ],
  [
    "demand",
    0,
    "구매 인기도 눈여겨볼 만합니다. 십일월 팔일 확인한 쿠팡 상품 화면에는 최근 한 달 만 명 이상 구매했다는 표시가 있었습니다. 소수만 찾는 생소한 모델은 아니라는 뜻이죠."
  ],
  [
    "demand",
    1,
    "같은 화면의 상품평도 사만 구천오백육십팔 개로 표시됐습니다. 꾸준히 구매와 평가가 쌓여 온 제품을 찾는 분이라면 상당히 눈여겨볼 만한 수치입니다."
  ],
  [
    "demand",
    2,
    "더 중요한 건 판매 주체입니다. 저희는 로켓배송 문구만 본 게 아니라 선택된 판매자 항목에서 쿠팡을 직접 확인하고, 그 판매 옵션을 구매 추천 후보로 골랐습니다."
  ],
  [
    "review",
    0,
    "이번엔 리뷰 숫자만 읽지 않았습니다. 지에스샵의 본사직영 쿠쿠 동일 모델 상품 페이지에서 후기 이백팔십사 건, 평점 오 점 만점에 사 점 오 점을 추가 확인했습니다."
  ],
  [
    "review",
    1,
    "디자인을 좋게 평가한 응답은 칠십구 퍼센트, 사용이 편하다는 응답은 육십팔 퍼센트로 표시됩니다. 화이트 디자인과 단순한 조작에 만족했다는 실제 후기들도 있었습니다."
  ],
  [
    "review",
    2,
    "세밀하게 초 단위 시간을 맞추는 건 다이얼식의 아쉬운 점입니다. 하지만 평소 데우기 위주로 사용한다면, 버튼을 여러 번 누르지 않아도 되는 단순함을 장점으로 느낄 수 있겠죠."
  ],
  [
    "price",
    0,
    "가격도 확인했습니다. 십일월 팔일 조사 당시 쿠팡 파트너스의 비교 표시가는 육만 천 원, 다나와의 옥션 표시가는 육만 삼백십 원이었어요."
  ],
  [
    "price",
    1,
    "표시 가격 차이는 단 육백구십 원입니다. 그래서 무조건 쿠팡이 최저가라고 말하지 않습니다. 실제 결제할 때는 상품과 배송 조건을 맞춰 비교하는 게 정확하죠."
  ],
  [
    "price",
    2,
    "가격 차이가 크지 않다면 판매 주체와 구매 편의도 선택의 이유가 됩니다. 이번에 쿠팡 판매 옵션을 추천 후보로 고른 건 이런 조건까지 함께 봤기 때문입니다."
  ],
  [
    "wow",
    0,
    "가장 눈여겨볼 부분은 와우 가입 쿠폰입니다. 조사 당시 가입 쿠폰 대상 계정에는 이만 사천 원이라는 가격이 표시됐어요. 가입 쿠폰을 받을 수 있다면 꽤 매력적인 조건입니다."
  ],
  [
    "wow",
    1,
    "여기서 스마트 초이스 삼육오는 회비도 빼놓지 않았습니다. 월회비 칠천팔백구십 원은 정기 요금이기 때문에, 실제 부담을 계산할 때 함께 봐야 합니다."
  ],
  [
    "wow",
    2,
    "그렇게 계산하면 쿠폰 대상자의 첫 달 상품과 회비 합계는 삼만 천팔백구십 원입니다. 신규 가입 조건을 충족하신다면 주문 화면에서 꼭 이 혜택을 확인해 보세요."
  ],
  [
    "choice",
    0,
    "정리해 볼게요. 식사를 간단히 데우고, 복잡한 기능은 필요 없고, 쿠팡에서 판매하는 상품을 선호한다면 저는 쿠쿠 씨엠더블유 에이이공일 디더블유를 먼저 추천합니다."
  ],
  [
    "choice",
    1,
    "왜 추천하냐고요? 쿠팡 상품의 높은 구매 지표를 확인했고, 선택 판매자도 살폈고, 다른 쇼핑몰의 실제 사용자 후기까지 비교했기 때문입니다."
  ],
  [
    "choice",
    2,
    "특히 와우 신규 가입 쿠폰 대상자라면 첫 달 회비를 포함한 총액까지 계산해 보세요. 내게 필요한 기능과 결제 조건이 맞는다면, 이제 이 제품부터 확인하셔도 좋겠습니다."
  ],
  [
    "cta",
    0,
    "저희가 조사한 이유와 가격 비교는 설명란 맨 위 스마트 초이스 삼육오 구매가이드에서 확인하세요. 고민하는 시간을 줄이도록 핵심만 모아뒀습니다."
  ],
  [
    "cta",
    1,
    "구매하시기로 결정했다면 설명란의 쿠팡 제휴 링크에서 같은 모델과 실제 쿠폰 적용 금액을 확인해 보세요. 고객을 위해 조사하고 엄선한 구매 링크입니다."
  ],
  [
    "cta",
    2,
    "이 영상에는 쿠팡 파트너스 제휴 광고가 포함돼 있습니다. 구매가 발생하면 저희가 수수료를 받을 수 있지만, 고객님께 별도의 제휴 수수료는 청구되지 않습니다."
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

def draw_microwave(draw, x, y):
    # Product-shaped diagram, not an unlicensed claimed physical test photo.
    # Layout matches manufacturer front: white enclosure, black door, TWO right-hand dials.
    draw.rounded_rectangle((x,y,x+610,y+390),radius=27,fill=(235,238,240),outline=(170,181,189),width=6)
    draw.rounded_rectangle((x+35,y+36,x+446,y+335),radius=12,fill=(25,35,47),outline=(113,129,140),width=9)
    draw.rounded_rectangle((x+65,y+62,x+418,y+305),radius=6,fill=(35,45,55),outline=(47,59,71),width=2)
    for k in (130,273):
        cx=x+527; cy=y+k
        draw.ellipse((cx-36,cy-36,cx+36,cy+36),fill=(242,244,246),outline=(97,111,124),width=6)
        draw.line((cx,cy-9,cx,cy-29),fill=(64,77,88),width=5)
    draw.rounded_rectangle((x+482,y+334,x+568,y+365),radius=5,outline=(130,143,155),width=3)

def draw_left_panel(draw,im,scene):
    draw.rounded_rectangle((88,329,774,895),radius=27,fill=(245,249,252))
    draw.rounded_rectangle((102,343,758,881),radius=22,outline=(211,220,228),width=3)
    if scene=="demand":
        draw.text((164,410),"1만 명+",font=font(112),fill=(10,42,67))
        draw.text((168,535),"최근 한 달 구매 표시",font=font(33),fill=(59,83,103))
        draw.line((170,608,696,608),fill=(209,218,223),width=3)
        draw.text((164,654),"49,568개",font=font(82),fill=(10,42,67))
        draw.text((168,777),"쿠팡 상품평 · 11.08 확인",font=font(26,False),fill=(59,83,103))
    elif scene=="review":
        draw.text((154,425),"4.5 / 5",font=font(106),fill=(10,42,67))
        draw.text((167,550),"GS SHOP 동일 모델 · 284건",font=font(30),fill=(59,83,103))
        draw.line((170,620,690,620),fill=(209,218,223),width=3)
        draw.text((156,666),"79% / 68%",font=font(72),fill=(10,86,76))
        draw.text((167,778),"디자인 / 편리성 긍정 표시",font=font(26,False),fill=(59,83,103))
    elif scene=="wow":
        draw.text((145,404),"31,890원",font=font(92),fill=(10,70,59))
        draw.text((162,531),"대상자 첫 달 총액 예시",font=font(32),fill=(59,83,103))
        draw.line((170,598,690,598),fill=(209,218,223),width=3)
        draw.text((162,652),"24,000원",font=font(55),fill=(10,42,67))
        draw.text((162,723),"+ 회비 7,890원",font=font(37),fill=(59,83,103))
        draw.text((162,812),"신규 와우 가입 쿠폰 대상 조건",font=font(24,False),fill=(74,93,111))
    elif scene=="price":
        draw.text((159,407),"60,310원",font=font(77),fill=(10,42,67))
        draw.text((164,519),"다나와 당시 표시가",font=font(30),fill=(59,83,103))
        draw.line((170,604,691,604),fill=(209,218,223),width=3)
        draw.text((159,661),"61,000원",font=font(76),fill=(10,42,67))
        draw.text((164,777),"쿠팡 파트너스 비교 표시가",font=font(26,False),fill=(59,83,103))
    else:
        # Product visual: official design illustration, two rotary dials.
        draw_microwave(draw,126,392)
        draw.text((153,819),"쿠쿠 CMW-A201DW · 20L",font=font(29),fill=(21,46,65))
    draw.text((117,859),"비교 자료 · 제품 외관은 이해를 돕는 도식",font=font(16,False),fill=(116,131,145))

def slide(scene,focus,subtitle,file):
    eyebrow,title,items=SCENES[scene]
    im=Image.new("RGB",(W,H),BG)
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,16,H),fill=GOLD)
    d.rounded_rectangle((1250,-210,2180,445),radius=220,fill=(15,35,54))
    d.rounded_rectangle((80,18,451,116),radius=20,fill=(246,249,253))
    logo=Image.open(ROOT/"assets/smartchoice365-brand-logo-v1.png").convert("RGBA")
    logo.thumbnail((346,92))
    im.paste(logo,(92+(346-logo.width)//2,21+(92-logo.height)//2),logo)
    d.text((1530,64),"구매가이드 · 제휴광고",font=font(26,False),fill=SOFT)
    d.line((80,130,1842,130),fill=(69,87,108),width=3)
    d.text((87,160),eyebrow,font=font(28),fill=GOLD)
    d.text((85,220),title,font=font(54),fill=WHITE)
    draw_left_panel(d,im,scene)
    for idx,(headline,detail) in enumerate(items):
        y=340+idx*185
        active=idx==focus
        d.rounded_rectangle((808,y,1842,y+162),radius=24,fill=((34,62,78) if active else PANEL),
                            outline=(GOLD if active else (63,83,106)),width=7 if active else 2)
        if active:
            d.rounded_rectangle((824,y+24,835,y+138),radius=4,fill=GOLD)
        d.text((860,y+22),headline,font=font(35),fill=WHITE)
        d.text((864,y+95),detail,font=font(24,False),fill=(GOLD if active else SOFT))
    d.rounded_rectangle((85,914,1842,1016),radius=20,fill=(10,30,51),outline=(65,86,107),width=2)
    for n,line in enumerate(wrap(d,subtitle,29,1640,max_lines=2)):
        d.text((115,924+n*41),line,font=font(29,False),fill=WHITE)
    d.line((81,1042,1842,1042),fill=(55,76,97),width=2)
    d.text((92,1049),"구매·후기 지표는 표시 당시 자료 · 가격·할인 대상과 판매자는 변동 가능 · 광고·쿠팡 파트너스",font=font(19,False),fill=SOFT)
    im.save(file,optimize=True)


def sidebar(path,ending=False):
    im=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
    for x0,x1 in [(12,643),(1277,1907)]:
        d.rounded_rectangle((x0,12,x1,1068),radius=25,fill=(9,25,45,242))
    text(d,(76,95),"SMART",62,GOLD)
    text(d,(76,171),"CHOICE 365",46,WHITE)
    text(d,(76,333),"루아의",48,WHITE)
    text(d,(76,416),"구매 이야기" if not ending else "공식 엔딩",48,GOLD)
    text(d,(1340,123),"엄선 구매추천",48,GOLD)
    for i,phrase in enumerate(["실제 구매 지표","다른 쇼핑몰 후기","와우 회비까지","구매처 검증"]):
        text(d,(1340,277+i*95),phrase,35,WHITE)
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
    video_clip_from_source(story,0,9.95,story_overlay)
    files.append(story)
    t=9.95
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
      "language":"ko","speed":1.1,"steps":8,"story_duration":9.95,
      "timeline":timeline,"total_seconds":float(probe["format"]["duration"]),
      "sha256":hashlib.sha256(VIDEO.read_bytes()).hexdigest(),
      "source_story":"owner-approved CUCKOO cartoon opening 0-9.95 sec","official_outro_reused":True,
      "notes":"Each spoken Sarah cue highlights the exact matching card; claims are dated and qualified."
    },ensure_ascii=False,indent=2))
    (OUT/"Sarah_Focus_Captions.srt").write_text("\n\n".join(subs),encoding="utf-8")
    print("SUCCESS_SARAH_REVIEW",VIDEO,VIDEO.stat().st_size,probe["format"]["duration"],flush=True)
if __name__=="__main__":
    main()
