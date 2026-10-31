#!/usr/bin/env python3
"""Ninja Australia editorial video — voiced, exact audio-segment timing, review only."""
import io,json,os,re,subprocess,urllib.request
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont
from kokoro import KPipeline
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'ninja-english'/'out';OUT.mkdir(parents=True,exist_ok=True)
W,H=1920,1080
NAVY='#10203C';GOLD='#F3C65F';CREAM='#F8F4EA';BLUE='#A9D4E8'
GUIDE='https://smartchoice365-web.pages.dev/guides/2026-ninja-af141-vs-af400-australia-single-dual-basket.html?utm_source=youtube&utm_medium=video&utm_campaign=ninja_af141_af400_english'
F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(n,b=False):return ImageFont.truetype(FB if b else F,n)
def txt(d,s,xy,n=48,color=CREAM,b=False,maxwidth=1690):
 f=font(n,b)
 while d.textbbox((0,0),s,font=f)[2]>maxwidth and n>26:
  n-=2;f=font(n,b)
 d.text(xy,s,font=f,fill=color)
def wrap(d,s,x,y,n=45,color=CREAM,maxw=1680,gap=14):
 words=s.split();rows=[];part=''
 for word in words:
  test=(part+' '+word).strip()
  if d.textbbox((0,0),test,font=font(n))[2]>maxw and part:rows.append(part);part=word
  else:part=test
 rows.append(part)
 for line in rows:txt(d,line,(x,y),n,color);y+=n+gap
 return y
def box(d,rect,fill='#1C3455',outline='#37516D'):
 d.rounded_rectangle(rect,radius=34,fill=fill,outline=outline,width=3)
def photo(url):
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  html=urllib.request.urlopen(req,timeout=20).read().decode('utf8','ignore')
  m=re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',html)
  if not m:m=re.search(r'<meta[^>]+content=["\']([^"\']+)[^>]+property=["\']og:image',html)
  if not m:return None
  image_url=m.group(1).replace('&amp;','&')
  if image_url.startswith('//'):image_url='https:'+image_url
  b=urllib.request.urlopen(urllib.request.Request(image_url,headers={'User-Agent':'Mozilla/5.0'}),timeout=20).read()
  return Image.open(io.BytesIO(b)).convert('RGBA')
 except Exception as e:print('Image source unavailable',url,str(e));return None
def paste_contain(canvas,im,rect):
 if im is None:return False
 x0,y0,x1,y1=rect;im=im.copy();im.thumbnail((x1-x0-36,y1-y0-36),Image.Resampling.LANCZOS)
 canvas.paste(im,(x0+(x1-x0-im.width)//2,y0+(y1-y0-im.height)//2),im if im.mode=='RGBA' else None)
 return True
scene=[
('HELLO','Hi, welcome to Smart Choice three sixty five. Today, we are comparing two Ninja air fryers in Australia: the AF141 and the AF400.','NINJA AF141  versus  AF400'),
('QUALITY','If the video looks blurry, select 1080p in your video quality settings. Subscribe for practical comparisons that help you buy smarter.','Clear comparisons. Smarter decisions.'),
('QUESTION','Do you really need two air fryer drawers? The answer depends on the dinners you actually cook, not the biggest number printed on the box.','DO YOU NEED TWO DRAWERS?'),
('PRODUCTS','The Ninja AF141 has one 4.7 litre basket. The AF400 has two separate 4.75 litre drawers: 9.5 litres altogether.','4.7 L   versus   2 x 4.75 L'),
('TRAP','Here is the catch. The AF400 is not one enormous cooking space. Its 9.5 litres are split between two baskets, so a large single item may not fit.','9.5 L DOES NOT MEAN ONE BIG BASKET'),
('TWO-ZONE','The AF400 becomes useful when you regularly cook two different foods. Imagine chicken in one drawer and vegetables in the other, with different settings.','TWO FOODS. TWO SETTINGS.'),
('SMALL-HOUSEHOLD','If you usually reheat leftovers, cook chips, or prepare one item for one or two people, the AF141 may be all you need.','SMALL HOUSEHOLD? THINK AF141'),
('FAMILY','For busy family dinners, the AF400 offers separate zones and timing features. But those benefits matter only if you will genuinely use both drawers.','FAMILY MEALS? CONSIDER AF400'),
('PRICE','Our source article recorded Australian prices on the thirtieth of October. Prices and offers change, so compare the final checkout price today, not just a headline discount.','CHECK TODAY\'S AUSTRALIAN PRICE'),
('COST','Try our five dinner test. Look at your last five normal dinners. How often would a second drawer actually have saved you a separate cooking batch?','THE FIVE-DINNER TEST'),
('VERDICT','Our verdict: choose the AF141 for simpler, compact everyday cooking. Choose the AF400 if you regularly cook a main and a hot side at once.','CHOOSE FOR YOUR ACTUAL ROUTINE'),
('LINK','For the full Australian comparison, specifications, and buying checklist, open the Ninja AF141 versus AF400 article linked first in the description.','FULL PRODUCT COMPARISON IN DESCRIPTION')]
urls=['https://ninjakitchen.com.au/products/ninja-air-fryer-4-7l-pro','https://ninjakitchen.com.au/products/ninja-foodi-max-xxxl-dual-zone-air-fryer']
# Image-first hard gate: do not render a video if a required licensed photo is missing.
# Remote manufacturer images must NOT be assumed to have editorial reuse permission.
# Provide a verified local visual pack and an explicit rights/scene manifest first.
visual_pack=ROOT/'ninja-english'/'assets'/'approved_visual_manifest.json'
if not visual_pack.exists():
 raise RuntimeError('IMAGE_FIRST_BLOCK: approved visual storyboard and rights manifest missing. Do not render silent/blank product cards.')
pack=json.loads(visual_pack.read_text(encoding='utf-8'))
required=pack.get('assets',[])
if len(required)<len(scene):
 raise RuntimeError('IMAGE_FIRST_BLOCK: each narration scene needs a verified visual asset')
for item in required:
 p=(ROOT/'ninja-english'/'assets'/item.get('file','')).resolve()
 root=(ROOT/'ninja-english'/'assets').resolve()
 if not p.is_relative_to(root) or not p.is_file() or item.get('usage_approved') is not True:
  raise RuntimeError('IMAGE_FIRST_BLOCK: missing or unapproved scene image: '+repr(item))
 with Image.open(p) as test:
  test.verify()
imgs=[photo(u) for u in urls]
if any(im is None for im in imgs):
 raise RuntimeError('IMAGE_FIRST_BLOCK: real Ninja product images missing; no placeholders permitted')
logo=Image.open(ROOT/'assets'/'smartchoice365-brand-logo-v1.png').convert('RGBA')
pipeline=KPipeline(lang_code='a')
segments=[];meta=[]
for i,(kind,speech,headline) in enumerate(scene):
 pieces=[audio for _,_,audio in pipeline(speech,voice='af_heart',speed=0.96)]
 if not pieces:raise RuntimeError('Kokoro produced no speech for '+str(i))
 a=np.concatenate(pieces);a=np.concatenate([a,np.zeros(int(24000*.25),dtype=np.float32)])
 wav=OUT/f'voice_{i:02}.wav';sf.write(wav,a,24000)
 dur=len(a)/24000
 im=Image.new('RGB',(W,H),NAVY);d=ImageDraw.Draw(im)
 d.rectangle((0,0,W,17),fill=GOLD);d.rectangle((0,1040,W,1080),fill='#081629')
 logo2=logo.copy();logo2.thumbnail((490,145),Image.Resampling.LANCZOS)
 im.paste(logo2,(90,55),logo2)
 d=ImageDraw.Draw(im)
 txt(d,'AUSTRALIAN BUYING GUIDE',(1450,72),25,BLUE,True,maxwidth=400)
 txt(d,headline,(95,235),68,GOLD,True,maxwidth=1740)
 if kind in ('PRODUCTS','TRAP','TWO-ZONE','SMALL-HOUSEHOLD','FAMILY','QUESTION','VERDICT'):
  box(d,(100,340,930,830));box(d,(990,340,1820,830))
  ok1=paste_contain(im,imgs[0],(130,368,900,758))
  ok2=paste_contain(im,imgs[1],(1020,368,1790,758))
  d=ImageDraw.Draw(im)
  if not (ok1 and ok2):
   txt(d,'PRODUCT PHOTO UNAVAILABLE',(170,540),33,'#CFD7E4',True)
   txt(d,'PRODUCT PHOTO UNAVAILABLE',(1040,540),33,'#CFD7E4',True)
  txt(d,'AF141  |  SINGLE',(240,776),34,CREAM,True,maxwidth=580)
  txt(d,'AF400  |  DUAL ZONE',(1110,776),34,CREAM,True,maxwidth=630)
 elif kind=='COST':
  for j,(label,value) in enumerate([('0 OR 1','AF141 MAY BE ENOUGH'),('2 OR 3','COMPARE THE EXTRA COST'),('4 OR 5','AF400 MAY PAY OFF IN CONVENIENCE')]):
   x=110+j*575;box(d,(x,365,x+530,790))
   txt(d,label,(x+60,455),80,GOLD,True,maxwidth=400);wrap(d,value,x+45,600,35)
 else:
  box(d,(110,360,1800,810));wrap(d,speech,170,465,51,CREAM,maxw=1540)
 txt(d,'SMART CHOICE 365  •  INDEPENDENT BUYING ANALYSIS',(90,1050),19,'#A4B7D1')
 txt(d,f'{i+1:02} / {len(scene):02}',(1740,1050),18,GOLD,True)
 png=OUT/f'scene_{i:02}.png';im.save(png)
 mp4=OUT/f'part_{i:02}.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-loop','1','-framerate','24','-i',str(png),'-i',str(wav),'-t',str(dur),'-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(mp4)],check=True)
 segments.append(mp4);meta.append({'scene':i,'kind':kind,'duration':dur,'narration':speech})
idx=OUT/'concat.txt';idx.write_text(''.join("file '"+f.name+"'\n" for f in segments))
out=OUT/'ninja_af141_af400_en_review.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(idx),'-c','copy','-movflags','+faststart',str(out)],check=True)
subprocess.run(['ffprobe','-v','error','-show_entries','stream=codec_type,codec_name','-of','json',str(out)],check=True)
(OUT/'description.txt').write_text('👉 Full Ninja AF141 vs AF400 buying guide: '+GUIDE+'\n\nAustralian specifications, use cases, and independent buying analysis. Manufacturer information, not hands-on testing. Observed prices may change.\n\nProduct images: Ninja Kitchen Australia (manufacturer imagery, editorial comparison). Affiliate links may appear in the linked guide.\n')
(OUT/'manifest.json').write_text(json.dumps({'status':'AWAITING_USER_APPROVAL','voice':'kokoro af_heart 0.96','images_fetched':[v is not None for v in imgs],'parts':meta,'guide':GUIDE},indent=2))
print('COMPLETED',out)
