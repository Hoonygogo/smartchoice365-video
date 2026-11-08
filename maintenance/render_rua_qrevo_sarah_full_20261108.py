#!/usr/bin/env python3
"""Render RUA Qrevo Korean buyer's guide with locked Sarah/F1 narration and cue-accurate focus rectangles.
REVIEW DRAFT ONLY: never uploads to YouTube/Meta. Free Supertonic 3, fixed Korean F1 voice.
"""
from pathlib import Path
import hashlib, json, math, os, subprocess
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont
from supertonic import TTS

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"uploads/RUA_Qrevo_L_Pro_3Parts_OfficialOutro_Affiliate_Ready_1080x1920.mp4"
OUT=ROOT/"renders/rua-qrevo-sarah-20261108"
BUILD=ROOT/"build/rua-qrevo-sarah-20261108"
OUT.mkdir(parents=True,exist_ok=True)
BUILD.mkdir(parents=True,exist_ok=True)
VIDEO=OUT/"RUA_Qrevo_L_Pro_Full_Sarah_Focus_1080p.mp4"
W,H=1920,1080
BG=(8,23,43); PANEL=(24,44,66); WHITE=(246,249,253)
GOLD=(250,194,82); SOFT=(174,194,215); GREEN=(104,225,179)
SCENES={
 "intro":("본영상 구매가이드","로보락 Qrevo L Pro, 살 만할까?",[
   ("기능 확인","내 집에서 필요한 자동화인지 먼저 확인"),
   ("실구매가 비교","결제액과 조건부 카드 할인을 구분"),
   ("판매자 검토","후기·A/S·반품 조건까지 살피기")]),
 "features":("기능은 제조사 표기 기준","청소보다 청소 후 관리가 핵심",[
   ("최대 18,500 Pa","제조사 흡입력 수치 · 실사용 성능 보증 아님"),
   ("최대 75℃ 걸레 세척 · 45℃ 건조","위생 관리 부담을 줄이는 자동 관리"),
   ("자동 먼지 비움 · 다기능 도크","편리하지만 물통과 브러시 관리는 필요")]),
 "limits":("구매 전 필수 체크","할인이 커도 우리 집에 맞아야 합니다",[
   ("러그·문턱·가구 높이","진입 가능한 높이와 장애물 구조 확인"),
   ("벽 모서리·좁은 틈","모든 구석이 완벽하게 청소된다고 보장 못 함"),
   ("도크 설치와 물통 동선","콘센트·정수·오수통 관리 공간까지 확인")]),
 "prices":("11월 8일 조사 가격","일반가와 조건부 할인가를 나눠 보세요",[
   ("네이버 519,000원","일반 표시가 · 기본 무료배송 조건 확인"),
   ("G마켓 530,160원","행사 쿠폰 적용 표시가 · 카드 할인 전"),
   ("G마켓 493,050원 · 조건부","대상 카드 + 스마일페이 등 결제 조건 충족 시만")]),
 "rewards":("실제 결제와 포인트","적립 포인트는 현금 즉시 할인과 다릅니다",[
   ("결제액 519,000원","네이버 일반 구매가로 결제하는 금액"),
   ("포인트는 별도","멤버십·머니·리뷰 조건을 충족한 후 적립"),
   ("최종 결제 화면 확인","적립률·배송지·쿠폰은 고객마다 다름")]),
 "seller":("신뢰까지 비교","가격보다 중요한 판매자와 A/S",[
   ("평점 4.9 / 5","2026년 11월 8일 확인 당시 상품 표시"),
   ("4~5점 후기 939 / 946건","당시 표시된 리뷰 분포, 긍정 비중 99.3%"),
   ("판매자와 국내 A/S","판매 법인·수입사·고객지원 경로 검토")]),
 "fit":("이런 집에 적합할까?","좋은 제품도 모든 집의 정답은 아닙니다",[
   ("매일 바닥 청소를 줄이고 싶다면","예약 청소와 도크 자동화의 가치 확인"),
   ("직접 물통 관리는 할 수 있다면","완전 무관리 제품이라고 생각하지 않기"),
   ("두꺼운 러그·높은 문턱이 많다면","해당 집에 적합한 대안을 먼저 비교")]),
 "vetted":("엄선 구매추천의 원칙","아무 제휴 링크나 추천하지 않습니다",[
   ("네이버 · 엄선 구매처","일반 구매조건과 판매자 지표를 검토한 우선 비교처"),
   ("G마켓 · 카드 할인 조건부","대상 카드 혜택을 쓰는 분에게만 비교 대안"),
   ("선정 근거는 홈페이지에 공개","가격·후기·판매자·A/S 조사 과정 확인")]),
 "cta":("클릭 가능한 설명란 링크","비교는 저희가, 선택은 편하게",[
   ("설명란 첫 번째 링크","상세 조사와 판매처 선정 근거 확인"),
   ("네이버 · 엄선 구매처","해당 상품 다이렉트 제휴 링크"),
   ("G마켓 · 카드 할인 조건부","결제 혜택이 맞는 분만 가격 비교")])
}
# Each spoken cue maps to exactly one matching, fixed-location highlight panel.
CUES=[
("intro",0,"안녕하세요. 스마트 초이스 삼육오입니다. 루아의 청소 이야기를 보셨나요? 이제 실제 구매가치를 따져보겠습니다."),
("intro",1,"먼저 실제로 얼마를 결제해야 하는지, 할인과 적립이 어떤 조건에서 적용되는지 구분해 볼게요."),
("intro",2,"오늘은 제품 기능만이 아니라 판매자 후기와 국내 에이에스까지 확인한 결과를 안내합니다."),
("features",0,"로보락 큐레보 엘 프로의 제조사 최대 흡입력 표기는 만 팔천오백 파스칼입니다. 이 숫자만으로 실사용 청소력이 몇 배 좋다고 말할 수는 없어요."),
("features",1,"물걸레는 최대 칠십오 도로 세척하고, 사십오 도 온풍으로 건조하는 기능이 소개됩니다. 청소 후 손이 가는 일을 줄이는 게 핵심이죠."),
("features",2,"자동 먼지 비움과 다기능 도크도 편리합니다. 다만 먼지통과 물통, 브러시 관리까지 완전히 사라지는 건 아닙니다."),
("limits",0,"구매 전에는 문턱과 두꺼운 러그, 그리고 가구 밑 공간을 꼭 확인하세요. 집 구조에 따라 로봇이 들어가지 못하는 곳이 있습니다."),
("limits",1,"벽 모서리나 좁은 틈을 항상 완벽하게 청소한다고 기대하기보다, 내 집에서 중요한 부분을 먼저 비교하는 게 좋습니다."),
("limits",2,"도크 설치 공간과 콘센트도 중요하죠. 정수통과 오수통을 꺼내서 관리할 수 있는지도 확인하세요."),
("prices",0,"이제 가장 중요한 가격입니다. 십일월 팔일 조사 당시, 네이버의 일반 표시 구매가는 오십일만 구천 원이었습니다. 기본 배송비는 무료로 표시됐습니다."),
("prices",1,"같은 모델의 지마켓 행사 쿠폰 적용가는 오십삼만 백육십 원으로 표시됐습니다."),
("prices",2,"사십구만 삼천오십 원은 누구나 받는 가격이 아닙니다. 대상 카드와 스마일페이 등 결제 조건을 충족해야 하는 별도의 할인가입니다."),
("rewards",0,"네이버에서 실제 결제하는 금액은 오십일만 구천 원으로 보아야 합니다."),
("rewards",1,"나중에 받을 네이버 포인트를 미리 현금 할인처럼 빼서 비교하면 오해하기 쉬워요. 적립은 멤버십과 결제수단, 리뷰 조건에 따라 다릅니다."),
("rewards",2,"최종 결제 화면에서 배송비와 카드 쿠폰, 적립 가능 여부를 확인한 뒤 비교하세요."),
("seller",0,"우리는 단순히 싼 판매처만 찾지 않았습니다. 조사 당시 해당 상품 평점은 오 점 만점에 사 점 구 점으로 표시됐어요."),
("seller",1,"사 점에서 오 점 후기가 구백사십육 건 중 구백삼십구 건이었습니다. 다만 공개 후기 숫자만으로 모든 구매 경험을 보증할 수는 없어요."),
("seller",2,"판매 법인과 수입사 정보, 국내 고객지원과 에이에스 경로도 확인했어요. 반품 조건은 구매 전에 판매페이지에서 다시 살펴보세요."),
("fit",0,"이 제품은 청소를 자주 미루게 되고, 예약 청소와 자동 관리로 시간을 줄이고 싶은 분에게 검토할 가치가 있습니다."),
("fit",1,"물통과 소모품 관리를 가끔 직접 할 수 있다면 자동화의 장점을 활용하기가 더 좋겠죠."),
("fit",2,"반대로 문턱이 높거나 두꺼운 러그가 많다면, 할인에 끌려 바로 구매하기보다 다른 모델도 비교해 보세요."),
("vetted",0,"스마트 초이스 삼육오는 고객을 위해 검토하고 엄선한 다이렉트 구매 링크만 추천합니다. 일반 구매조건에서는 네이버 판매처부터 비교해 보세요."),
("vetted",1,"대상 카드와 스마일페이 할인 조건이 맞는 분이라면 지마켓도 확인할 가치가 있습니다. 어떤 경우에도 전국 최저가를 보장하는 건 아닙니다."),
("vetted",2,"왜 이 구매처를 선정했는지 궁금하신가요? 가격과 판매자, 후기, 에이에스 근거는 홈페이지 엄선 구매추천 글에 공개했습니다."),
("cta",0,"이 영상 설명란 맨 위 첫 번째 링크에서 조사한 내용을 자세히 확인할 수 있습니다."),
("cta",1,"네이버 쇼핑커넥트는 엄선 구매처, 지마켓 링크프라이스는 카드 할인 조건부 대안으로 구분해 두었습니다."),
("cta",2,"이 영상에는 광고 제휴 링크가 포함되어 있으며 판매 시 스마트 초이스 삼육오가 수수료를 받습니다. 고객에게 별도의 제휴 수수료는 청구되지 않습니다. 구매 시점의 실제 결제 조건을 확인하세요.")
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
    text(d,(85,56),"SMART CHOICE 365",40,GOLD)
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
    text(d,(96,1049),"2026.11.08 조사 기준 · 실제 결제·배송·쿠폰·재고는 변동 가능 · 영상은 제품 테스트가 아닌 설명 자료",19,SOFT,False)
    im.save(file,optimize=True)
def sidebar(path,ending=False):
    im=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
    for x0,x1 in [(12,643),(1277,1907)]:
        d.rounded_rectangle((x0,12,x1,1068),radius=25,fill=(9,25,45,242))
    text(d,(76,94),"SMART",64,GOLD)
    text(d,(76,171),"CHOICE 365",47,WHITE)
    text(d,(75,333),"루아의",50,WHITE)
    text(d,(75,420),"청소 이야기" if not ending else "공식 엔딩",52,GOLD)
    text(d,(1340,124),"우리의 기준",52,GOLD)
    for i,phrase in enumerate(["기능과 한계","실제 결제금액","판매자·후기·A/S","엄선 구매처"]):
        text(d,(1340,270+i*95),phrase,37,WHITE)
    d.rounded_rectangle((1316,825,1853,970),radius=20,fill=(48,37,65,239))
    text(d,(1337,847),"창작 3D 애니메이션",29,WHITE)
    text(d,(1337,900),"실제 로보락 제품 시연 아님",25,SOFT,False)
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
    video_clip_from_source(story,0,25.65,story_overlay)
    files.append(story)
    t=25.65
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
    video_clip_from_source(ending,27.82,10.035,outro_overlay)
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
      "language":"ko","speed":1.1,"steps":8,"story_duration":25.65,
      "timeline":timeline,"total_seconds":float(probe["format"]["duration"]),
      "sha256":hashlib.sha256(VIDEO.read_bytes()).hexdigest(),
      "source_story":"owner-approved RUA 3-part final","official_outro_reused":True,
      "notes":"Each cue's exact center-row focus box appears only during that cue's Sarah voice."
    },ensure_ascii=False,indent=2))
    (OUT/"Sarah_Focus_Captions.srt").write_text("\n\n".join(subs),encoding="utf-8")
    print("SUCCESS_SARAH_REVIEW",VIDEO,VIDEO.stat().st_size,probe["format"]["duration"],flush=True)
if __name__=="__main__":
    main()
