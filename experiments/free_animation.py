#!/usr/bin/env python3
"""Free, CPU-only 5-second animated character proof of concept.
No paid services, API tokens, or generative video model. This is 2D motion,
not true AI-generated character motion.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import subprocess

W,H,FPS,DURATION=540,960,15,5
out=Path("out/free-animation")
frames=out/"frames"
frames.mkdir(parents=True,exist_ok=True)
font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=ImageFont.truetype(font_path,29)
for i in range(FPS*DURATION):
    t=i/FPS
    im=Image.new("RGB",(W,H),(248,244,234))
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((30,85,510,880),radius=44,fill=(255,251,244))
    d.text((65,115),"SMART CHOICE 365",font=font,fill=(30,61,91))
    bob=round(12*math.sin(t*2*math.pi/2))
    cx,cy=270,485+bob
    d.ellipse((cx-145,cy+168,cx+145,cy+193),fill=(217,216,212))
    d.rounded_rectangle((cx-155,cy-135,cx+155,cy+150),radius=50,fill=(48,55,65))
    d.rounded_rectangle((cx-132,cy-116,cx+132,cy+110),radius=39,fill=(70,78,90))
    d.rounded_rectangle((cx-120,cy+62,cx+120,cy+132),radius=18,fill=(33,37,43))
    blink=(i%43 in (0,1))
    for ex in (cx-57,cx+57):
        if blink:
            d.line((ex-21,cy-16,ex+21,cy-16),fill="white",width=7)
        else:
            d.ellipse((ex-24,cy-42,ex+24,cy+8),fill="white")
            d.ellipse((ex-8,cy-21,ex+10,cy+3),fill=(23,29,40))
    d.arc((cx-40,cy+13,cx+40,cy+68),0,180,fill=(255,206,102),width=8)
    wave=math.sin(t*2*math.pi*1.5)
    d.line((cx+148,cy-35,cx+198,cy-82+round(25*wave)),fill=(48,55,65),width=19)
    d.ellipse((cx+186,cy-96+round(25*wave),cx+211,cy-71+round(25*wave)),fill=(48,55,65))
    d.line((cx-148,cy-35,cx-192,cy+24),fill=(48,55,65),width=18)
    d.text((87,730),"Meet your shopping buddy!",font=font,fill=(30,61,91))
    im.save(frames/f"{i:04d}.png")
video=out/"free_character_test.mp4"
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-framerate",str(FPS),"-i",str(frames/"%04d.png"),"-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-t",str(DURATION),"-c:v","libx264","-pix_fmt","yuv420p","-preset","veryfast","-crf","23","-c:a","aac","-movflags","+faststart",str(video)],check=True)
print(video)
