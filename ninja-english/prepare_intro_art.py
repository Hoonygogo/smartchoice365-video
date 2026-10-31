#!/usr/bin/env python3
"""Prepare mandatory English brand/quality/subscription intro art BEFORE rendering.
All assets are original vector drawings made with Pillow; the approved brand PNG is reused.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'ninja-english'/'storyboard'; OUT.mkdir(parents=True,exist_ok=True)
W,H=1920,1080
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def f(n,b=True): return ImageFont.truetype(BOLD if b else FONT,n)
def t(d,s,x,y,n=55,c='#152946',bold=True):d.text((x,y),s,font=f(n,bold),fill=c)
def base():
 im=Image.new('RGB',(W,H),'#F8F4EC');d=ImageDraw.Draw(im)
 d.rectangle((0,0,W,15),fill='#D8AB47')
 d.rectangle((0,1022,W,H),fill='#102440')
 t(d,'SMART CHOICE 365  /  AUSTRALIAN BUYING GUIDES',90,1040,22,'#F1E9D7')
 return im
def pill(d,xy,txt,fill='#E9EEF3'):
 d.rounded_rectangle(xy,radius=27,fill=fill)
 t(d,txt,xy[0]+25,xy[1]+17,28)
def save(im,name,purpose):
 path=OUT/name;im.save(path,optimize=True)
 return {'file':name,'scene':purpose,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'width':W,'height':H,'source':'original Pillow illustration + approved logo','usage_approved':True}
assets=[]
logo=Image.open(ROOT/'assets/smartchoice365-brand-logo-v1.png').convert('RGBA')
im=base();d=ImageDraw.Draw(im)
small=logo.copy();small.thumbnail((860,220),Image.Resampling.LANCZOS)
im.paste(small,((W-small.width)//2,100),small)
t(d,'NINJA AIR FRYER BUYING GUIDE',185,420,89)
t(d,'AF141 vs AF400',410,560,114,'#A47620')
pill(d,(470,775,1450,865),'WHICH ONE FITS YOUR KITCHEN?')
assets.append(save(im,'intro_brand.png','spoken greeting and title'))
im=base();d=ImageDraw.Draw(im)
t(d,'VIDEO LOOKS BLURRY?',190,100,90)
t(d,'Choose the clearest available playback quality',190,220,48,'#4A6279',False)
cards=[(180,'1','Settings','GEAR'),(710,'2','Quality','MENU'),(1240,'3','1080p','HD')]
for x,n,head,sub in cards:
 d.rounded_rectangle((x,370,x+480,855),radius=38,fill='#E5ECF4',outline='#D5AC58',width=5)
 d.ellipse((x+168,425,x+312,569),fill='#12335A')
 t(d,n,x+213,455,72,'#FFFFFF')
 t(d,head,x+60,640,53)
 t(d,sub,x+60,736,33,'#52708A')
for x in (666,1196):
 d.line((x,605,x+30,605),fill='#AF8A38',width=11)
 d.polygon([(x+32,584),(x+67,605),(x+32,626)],fill='#AF8A38')
t(d,'On some phones, open Advanced before selecting 1080p.',235,924,36,'#425B77',False)
assets.append(save(im,'intro_quality.png','illustrated settings → quality → 1080p explanation'))
im=base();d=ImageDraw.Draw(im)
t(d,'GOOD COMPARISONS. BETTER DECISIONS.',120,150,73)
d.rounded_rectangle((460,420,1470,675),radius=54,fill='#D0A447')
t(d,'SUBSCRIBE',650,485,98,'#152946')
t(d,'Practical buying advice for Australian households',260,775,52,'#3F5670',False)
assets.append(save(im,'intro_subscribe.png','spoken subscription invitation'))
(OUT/'manifest.json').write_text(json.dumps({'version':'ninja-en-image-first-v3-intro','status':'INTRO_IMAGES_READY_PRODUCT_STORYBOARD_PENDING','assets':assets,'narration':[{'image':'intro_brand.png','text':'Hi, welcome to Smart Choice three sixty five. Today, we are comparing the Ninja AF141 and AF400 for Australian households.'},{'image':'intro_quality.png','text':'If the picture looks blurry, open Settings, choose Quality, and select 1080p when available.'},{'image':'intro_subscribe.png','text':'For clear, practical buying comparisons, please consider subscribing.'}]},indent=2))
print('Intro visuals complete; product scenes are a required separate gate, not fabricated.')
