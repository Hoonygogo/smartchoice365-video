"""Branded introduction and large illustrated YouTube quality instructions."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from render_readability import font_path

W,H=1920,1080
NAVY='#13243a';GOLD='#d9a84e';BG='#f5f3ee';MUTED='#58677b'

def draw_intro(scene,index,total,caption,active,path):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    def f(n):return ImageFont.truetype(font_path(),n)
    def text(s,x,y,n=50,c=NAVY):d.text((x,y),s,font=f(n),fill=c)
    def center(s,y,n=50,c=NAVY):text(s,(W-d.textlength(s,font=f(n)))/2,y,n,c)
    def card(box,fill,outline=None,width=3):d.rounded_rectangle(box,25,fill=fill,outline=outline,width=width)
    def arrow(x,y):
        d.line((x,y,x+65,y),fill=GOLD,width=10)
        d.polygon([(x+80,y),(x+52,y-20),(x+52,y+20)],fill=GOLD)
    def gear(cx,cy):
        for j in range(8):
            a=math.pi*j/4
            d.line((cx+35*math.cos(a),cy+35*math.sin(a),cx+57*math.cos(a),cy+57*math.sin(a)),fill=NAVY,width=17)
        d.ellipse((cx-41,cy-41,cx+41,cy+41),fill=NAVY)
        d.ellipse((cx-18,cy-18,cx+18,cy+18),fill=BG)
    d.rectangle((0,0,W,96),fill=NAVY)
    text('SMART CHOICE 365',64,20,42,'white')
    text('COMPARE SMARTER. BUY BETTER.',1180,28,30,'#ead1a0')
    mode=scene['visual'];targets=list(active or [])
    if mode=='brand_intro':
        logo=Image.open(Path(__file__).resolve().parents[1]/'assets/smartchoice365-brand-logo-v1.png').convert('RGBA')
        logo.thumbnail((1640,610),Image.Resampling.LANCZOS)
        im.paste(logo,((W-logo.width)//2,80),logo)
        center('비교는 똑똑하게, 선택은 내 생활에 맞게',540,42,'#24745a')
        card((360,610,1560,730),NAVY)
        center('히트텍, 가장 따뜻하면 가장 좋을까요?',626,54,'white')
        if 0 in targets:card((350,600,1570,740),None,GOLD,7)
        center('smartchoice365-web.pages.dev',760,38,MUTED)
    elif mode=='quality_intro':
        text('화면이 흐리게 보이나요?',80,145,72)
        text('설정에서 화질을 높여 보세요',80,248,46,MUTED)
        boxes=[(80,365,570,660),(700,365,1190,660),(1320,365,1810,660)]
        labels=['설정','화질','1080p']
        for j,box in enumerate(boxes):
            selected=j in targets
            card(box,'#fff' if j<2 else NAVY,GOLD if selected else '#d9dfe6',7 if selected else 3)
            x=(box[0]+box[2])/2
            if j==0:gear(x,446)
            elif j==1:
                for k,length in enumerate([130,95,60]):d.line((x-65,420+k*26,x-65+length,420+k*26),fill=NAVY,width=9)
            else:text('HD',x-48,400,62,GOLD)
            text(labels[j],x-d.textlength(labels[j],font=f(62))/2,540,62,'white' if j==2 else NAVY)
        arrow(595,510);arrow(1215,510)
        text('휴대폰: 화질 → 고급 → 1080p',90,710,42)
        text('기기에 따라 메뉴 위치가 다를 수 있습니다 · 설정 방법을 설명한 그림',90,775,29,MUTED)
    elif mode=='subscribe_intro':
        center('구매 전, 한 번 더 비교하세요',200,76)
        center('생활에 맞는 선택 기준을 함께 살펴봅니다',320,44,MUTED)
        card((640,455,1280,620),'#ba302e')
        d.polygon([(705,497),(705,574),(770,536)],fill='white')
        text('구독',850,475,82,'white')
        center('도움 되는 구매 비교가 필요하다면',670,42,MUTED)
        center('구독으로 다음 비교도 만나보세요',735,42)
    else:raise ValueError('Unknown introduction scene')
    d.rectangle((0,850,W,H),fill=NAVY)
    lines=[];line=''
    for ch in caption:
        if line and d.textlength(line+ch,font=f(49))>1760:lines.append(line);line=ch
        else:line+=ch
    if line:lines.append(line)
    if len(lines)>3:raise ValueError('Intro caption overflow')
    for j,line in enumerate(lines):text(line,72,867+j*63,49,'white')
    d.rectangle((0,1072,int(W*index/total),1079),fill=GOLD)
    im.save(path)
