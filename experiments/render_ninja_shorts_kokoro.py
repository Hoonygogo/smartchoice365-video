#!/usr/bin/env python3
"""Ninja Shorts v2: Kokoro narration, six distinct fast-cut beats, no paid API.
Takes the two previously generated Wan clips and original user-supplied photo.
Does not publish to social media.
"""
from pathlib import Path
import json, subprocess
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from kokoro import KPipeline

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"out"/"ninja-shorts-kokoro"
OUT.mkdir(parents=True,exist_ok=True)
W,H=540,960
BG=(15,28,49); CREAM=(250,246,232); GOLD=(253,191,73)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(size): return ImageFont.truetype(FONT,size)
def ff(*args):
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",*map(str,args)],check=True)
def wrap(draw,text,f,maxw):
    words=text.split(); lines=[]; line=""
    for w in words:
        test=(line+" "+w).strip()
        if line and draw.textbbox((0,0),test,font=f)[2]>maxw:
            lines.append(line);line=w
        else:line=test
    if line:lines.append(line)
    return lines
def center(draw,text,y,size,color,maxw=480):
    f=font(size)
    lines=wrap(draw,text,f,maxw)
    for line in lines:
        b=draw.textbbox((0,0),line,font=f)
        draw.text(((W-(b[2]-b[0]))//2,y),line,font=f,fill=color,stroke_width=0)
        y+=size+12
def poster(title,body,kind,index):
    im=Image.new("RGB",(W,H),BG)
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((18,22,522,938),radius=32,outline=(75,113,136),width=3)
    d.text((35,44),"SMART CHOICE 365",font=font(23),fill=GOLD)
    d.rounded_rectangle((30,145,510,231),radius=18,fill=(34,64,87))
    center(d,title,162,33,CREAM)
    if kind=="solo":
        d.rounded_rectangle((120,300,420,610),radius=43,fill=(44,75,94),outline=GOLD,width=5)
        center(d,"1",326,115,GOLD)
        center(d,"DRAWER",499,33,CREAM)
    elif kind=="dual":
        for x in (55,285):
            d.rounded_rectangle((x,300,x+195,620),radius=25,fill=(46,79,100),outline=GOLD,width=5)
            d.ellipse((x+67,348,x+127,408),fill=GOLD)
            d.rounded_rectangle((x+75,535,x+121,581),radius=9,fill=CREAM)
        center(d,"2 SEPARATE ZONES",658,29,GOLD)
    else:
        for x,txt in [(35,"TOTAL"),(279,"USABLE")]:
            d.rounded_rectangle((x,305,x+225,580),radius=25,fill=(44,75,94),outline=GOLD,width=4)
            f=font(28)
            d.text((x+26,430),txt,font=f,fill=CREAM)
        center(d,"CAPACITY vs FIT",625,30,GOLD)
    center(d,body,770,29,CREAM)
    path=OUT/f"slide_{index:02}.png";im.save(path)
    return path
def overlay(index,title,caption):
    im=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((20,28,520,106),radius=20,fill=(15,28,49,215))
    center(d,title,47,27,GOLD)
    d.rounded_rectangle((20,788,520,910),radius=23,fill=(15,28,49,224))
    center(d,caption,810,25,CREAM,470)
    out=OUT/f"overlay_{index:02}.png"; im.save(out)
    return out

BEATS=[
    ("FRIES GONE WILD!", "Wait! My fries are flying!", "ai2", ""),
    ("NINJA TO THE RESCUE", "Okay, Ninja. Calm down.", "ai1", ""),
    ("COOKING FOR ONE?", "A single drawer may be all you need.", "solo", "LESS CAN BE MORE"),
    ("TWO FOODS AT ONCE?", "Separate drawers can make dinner easier.", "dual", "TWO FOODS. TWO SETTINGS."),
    ("THE REAL QUESTION", "Check basket space, not just total litres.", "compare", "MAKE SURE IT FITS"),
    ("SMART CHOICE 365", "Compare the Ninja A F one four one and A F four hundred on Smart Choice three sixty five.", "ai2", "FULL GUIDE ON OUR WEBSITE"),
]
pipeline=KPipeline(lang_code="a")
segments=[];meta=[]
for i,(headline,spoken,kind,sub) in enumerate(BEATS):
    chunks=[a for _,_,a in pipeline(spoken,voice="af_heart",speed=1.04)]
    if not chunks:raise RuntimeError("Kokoro did not return audio for beat "+str(i))
    audio=np.concatenate(chunks).astype(np.float32)
    audio=np.concatenate([audio,np.zeros(int(24000*0.16),dtype=np.float32)])
    wav=OUT/f"voice_{i:02}.wav";sf.write(wav,audio,24000)
    duration=len(audio)/24000
    dest=OUT/f"part_{i:02}.mp4"
    if kind.startswith("ai"):
        src=ROOT/"out"/"ninja-ai-sources"/("v2.mp4" if kind=="ai2" else "v1.mp4")
        if not src.exists():raise RuntimeError("Missing first AI animation: "+str(src))
        over=overlay(i,headline,spoken)
        # Original AI animation stays clearly visible, overlays vary with voice.
        ff("-stream_loop","-1","-i",src,"-loop","1","-i",over,"-i",wav,
           "-filter_complex",f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=30,format=yuv420p[base];[base][1:v]overlay=0:0:shortest=1[v]",
           "-map","[v]","-map","2:a","-t",duration,"-c:v","libx264","-preset","ultrafast",
           "-crf","25","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-shortest",dest)
    else:
        card=poster(headline,sub,kind,i)
        ff("-loop","1","-framerate","30","-i",card,"-i",wav,"-t",duration,
           "-vf",f"scale={W}:{H},format=yuv420p","-c:v","libx264","-preset","ultrafast",
           "-crf","23","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-shortest",dest)
    segments.append(dest)
    meta.append(dict(beat=i,visual=kind,spoken=spoken,duration=round(duration,2)))
index=OUT/"concat.txt";index.write_text("".join("file '"+s.name+"'\n" for s in segments))
final=OUT/"ninja_shorts_kokoro_v2.mp4"
ff("-f","concat","-safe","0","-i",index,"-c","copy","-movflags","+faststart",final)
(OUT/"manifest.json").write_text(json.dumps(dict(voice="Kokoro af_heart",status="AWAITING_USER_APPROVAL",beats=meta,source="Wan AI clips from prior verified runs",final=str(final)),indent=2))
print("COMPLETE",final,flush=True)
