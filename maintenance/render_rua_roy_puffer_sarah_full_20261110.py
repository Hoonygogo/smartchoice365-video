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
SRC=ROOT/"uploads/SmartChoice365_RUA_ROY_YouTube_Shorts_1080x1920.mp4"
OUT=ROOT/"renders/rua-roy-puffer-sarah-20261110"
BUILD=ROOT/"build/rua-roy-puffer-sarah-20261110"
OUT.mkdir(parents=True,exist_ok=True)
BUILD.mkdir(parents=True,exist_ok=True)
VIDEO=OUT/"RUA_ROY_Puffer_3Brand_Sarah_Focus_Full_1080p.mp4"
W,H=1920,1080
BG=(8,23,43); PANEL=(24,44,66); WHITE=(246,249,253)
GOLD=(250,194,82); SOFT=(174,194,215); GREEN=(104,225,179)
SCRIPT=json.loads((ROOT/"production/rua-roy-puffer-20261110-scenes.json").read_text(encoding="utf-8"))
SCENES=SCRIPT["scenes"]
CUES=SCRIPT["cues"]
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
    d.rounded_rectangle((82,18,450,125),radius=17,fill=(246,249,253))
    logo=Image.open(ROOT/"assets/smartchoice365-brand-logo-v1.png").convert("RGBA")
    logo.thumbnail((344,92))
    im.paste(logo,(94+(344-logo.width)//2,24+(92-logo.height)//2),logo)
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
    text(d,(96,1049),"2026.11.10 조사 기준 · 실제 결제·배송·쿠폰·재고는 변동 가능 · 영상은 제품 테스트가 아닌 설명 자료",19,SOFT,False)
    im.save(file,optimize=True)
def sidebar(path,ending=False):
    im=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
    for x0,x1 in [(12,643),(1277,1907)]:
        d.rounded_rectangle((x0,12,x1,1068),radius=25,fill=(9,25,45,242))
    text(d,(76,94),"SMART",64,GOLD)
    text(d,(76,171),"CHOICE 365",47,WHITE)
    text(d,(75,333),"루아와 로이의",50,WHITE)
    text(d,(75,420),"패딩 이야기" if not ending else "공식 엔딩",52,GOLD)
    text(d,(1340,124),"우리의 기준",52,GOLD)
    for i,phrase in enumerate(["기능과 한계","실제 결제금액","판매자·후기·A/S","엄선 구매처"]):
        text(d,(1340,270+i*95),phrase,37,WHITE)
    d.rounded_rectangle((1316,825,1853,970),radius=20,fill=(48,37,65,239))
    text(d,(1337,847),"창작 3D 애니메이션",29,WHITE)
    text(d,(1337,900),"실제 착용·보온 실험 아님",25,SOFT,False)
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
    if not SRC.is_file() or hashlib.sha256(SRC.read_bytes()).hexdigest()!="ad68dc22db5663af407ddbecf5ca4d29c0a2d87681d31d91fdc1b24f9196562e":raise RuntimeError("Approved RUA ROY source missing or hash mismatch")
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
    video_clip_from_source(story,0,20.05,story_overlay)
    files.append(story)
    t=20.05
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
    video_clip_from_source(ending,20.05,10.03,outro_overlay)
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
      "language":"ko","speed":1.1,"steps":8,"story_duration":20.05,
      "timeline":timeline,"total_seconds":float(probe["format"]["duration"]),
      "sha256":hashlib.sha256(VIDEO.read_bytes()).hexdigest(),
      "source_story":"owner-approved RUA ROY 2-part story","official_outro_reused":True,
      "notes":"Each cue's exact center-row focus box appears only during that cue's Sarah voice."
    },ensure_ascii=False,indent=2))
    (OUT/"Sarah_Focus_Captions.srt").write_text("\n\n".join(subs),encoding="utf-8")
    print("SUCCESS_SARAH_REVIEW",VIDEO,VIDEO.stat().st_size,probe["format"]["duration"],flush=True)
if __name__=="__main__":
    main()
