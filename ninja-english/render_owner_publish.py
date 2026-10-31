#!/usr/bin/env python3
"""Owner-requested fresh native-HD English video rebuild. Original illustrations, not product photography."""
from pathlib import Path
import os,json,hashlib,subprocess,math,random,re
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont
from kokoro import KPipeline
from importlib.machinery import SourceFileLoader
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'ninja-english'/'out';OUT.mkdir(exist_ok=True)
W,H=1920,1080
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
scene=[
('WELCOME','Welcome to Smart Choice 365. Today we compare Ninja AF141 and AF400 for Australian kitchens.','NINJA AF141 vs AF400','welcome'),
('QUALITY','For the clearest viewing experience, choose 1080p video quality. And subscribe for more practical buying guides.','SMART CHOICE 365','quality'),
('CHOICE','Do you really need two air fryer drawers? Your cooking habits matter more than the biggest number on the box.','ONE DRAWER OR TWO?','choice'),
('CAPACITY','The AF141 has one 4.7 litre basket. The AF400 has two separate 4.75 litre drawers, making 9.5 litres in total.','4.7 L vs 2 x 4.75 L','capacity'),
('CATCH','Remember, nine point five litres is not one giant basket. Two separate drawers can limit very large single foods.','TWO DRAWERS, NOT ONE','catch'),
('DUAL','The AF400 makes sense when you cook two foods together, such as chicken in one drawer and vegetables in the other.','TWO FOODS, TWO ZONES','dual'),
('SMALL','For one or two people cooking chips, leftovers or just one item, the AF141 may be enough.','SMALL HOUSEHOLD','small'),
('FAMILY','For regular family meals, the AF400 gives you two independent cooking areas, if you actually use them.','FAMILY DINNER','family'),
('PRICE','Australian prices and offers change. Compare the final checkout price, including delivery, rather than trusting a headline discount.','CHECK THE ACTUAL PRICE','price'),
('TEST','Look at your last five dinners. On how many nights would two air fryer zones have saved you an extra cooking batch?','FIVE DINNER TEST','test'),
('VERDICT','Choose the AF141 for simpler compact cooking. Choose the AF400 if you regularly cook a main and a side at the same time.','WHICH SHOULD YOU BUY?','verdict'),
('GUIDE','For the full Australian product comparison and buying checklist, open the link at the top of the video description.','FULL GUIDE IN DESCRIPTION','guide')]
palette=[('#142139','#273E59'),('#10243B','#284C65'),('#142E37','#366371'),('#1A2941','#37405C')]
def ft(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
def text(d,s,x,y,size,color='#F7F5EF',maxwidth=1650):
    f=ft(size,True)
    while d.textbbox((0,0),s,font=f)[2]>maxwidth and size>25:size-=2;f=ft(size,True)
    d.text((x,y),s,font=f,fill=color)
def draw_fryer(d,x,y,w,h,kind,colour='#202B39'):
    d.rounded_rectangle((x,y,x+w,y+h),radius=58,fill=colour,outline='#7B8A98',width=7)
    d.rounded_rectangle((x+38,y+35,x+w-38,y+165),radius=23,fill='#2F465E')
    d.ellipse((x+w//2-27,y+70,x+w//2+27,y+124),fill='#63D6E8')
    for dx in range(x+65,x+w-60,76): d.ellipse((dx,y+92,dx+12,y+104),fill='#E4E9EB')
    if kind=='two':
       d.line((x+w//2,y+183,x+w//2,y+h-48),fill='#6F7D90',width=12)
       for xx in (x+w//4,x+w*3//4):d.rounded_rectangle((xx-55,y+h-116,xx+55,y+h-81),radius=12,fill='#D2D7DE')
    else:d.rounded_rectangle((x+w//2-65,y+h-113,x+w//2+65,y+h-78),radius=12,fill='#D2D7DE')
    return [x,y,x+w,y+h]
def food(d,cx,cy,kind):
    d.ellipse((cx-173,cy-65,cx+173,cy+81),fill='#D3D9D5',outline='#FDFBF5',width=15)
    rng=random.Random(cx+cy)
    colors={'chicken':['#CB713A','#DC8A44','#B45B25'],'veggies':['#7BA949','#3A843B','#E29E3A','#CC644B'],'chips':['#F2B63B','#F5D166','#DB9647'],'fish':['#F18D6D','#EA745B','#CC6349']}.get(kind,['#A2B55E'])
    for i in range(17):
       px=cx+rng.randint(-115,115);py=cy+rng.randint(-35,35)
       w=rng.randint(21,47);h=rng.randint(15,28)
       d.ellipse((px-w,py-h,px+w,py+h),fill=colors[i%len(colors)],outline='#F5E4B7',width=2)
def scene_frame(i,entry,logo):
    kind,spoken,heading,visual=entry
    im=Image.new('RGB',(W,H),'#162839');d=ImageDraw.Draw(im)
    for y in range(H):
       t=y/H;base=(17+int(15*t),34+int(15*t),55+int(15*t))
       d.line((0,y,W,y),fill=base)
    d.rectangle((0,0,W,15),fill='#F2C66D')
    d.rounded_rectangle((75,176,1845,873),radius=43,fill='#243E52',outline='#5A7886',width=3)
    # original coherent kitchen/food composition; not a cropped contact sheet
    d.rectangle((109,615,1810,813),fill='#9A7757')
    for x in range(140,1760,230):
       d.line((x,618,x+60,808),fill='#B28B67',width=2)
    if visual in ('welcome','choice','capacity','catch','verdict','quality'):
       draw_fryer(d,270,335,380,370,'one')
       draw_fryer(d,1090,310,525,395,'two')
       text(d,'AF141',350,730,42,'#F6D47A',500);text(d,'AF400',1240,730,42,'#F6D47A',500)
    elif visual in ('dual','family'):
       draw_fryer(d,650,298,610,385,'two')
       food(d,425,750,'chicken');food(d,1470,750,'veggies')
       text(d,'CHICKEN',280,558,37);text(d,'VEGETABLES',1380,558,37)
    elif visual=='small':
       draw_fryer(d,730,300,480,400,'one')
       food(d,435,730,'chips');food(d,1430,735,'veggies')
    elif visual=='price':
       draw_fryer(d,330,330,380,360,'one')
       draw_fryer(d,1190,330,440,360,'two')
       d.rounded_rectangle((745,478,1124,614),radius=24,fill='#E3BF67')
       text(d,'COMPARE',776,515,52,'#18334A',330)
    elif visual=='test':
       for j in range(5):
          x=270+j*280;d.ellipse((x,340,x+210,550),fill='#E3D5B8',outline='#FAEEE0',width=11)
          food(d,x+105,440,('chicken','fish','veggies','chips','chicken')[j])
          text(d,str(j+1),x+70,660,55,'#F2C66D',130)
    elif visual=='guide':
       draw_fryer(d,260,335,360,355,'one')
       draw_fryer(d,1240,330,415,365,'two')
       d.rounded_rectangle((705,375,1190,655),radius=25,fill='#E7ECE9')
       text(d,'BUYING',780,410,55,'#152A42',350);text(d,'GUIDE',795,485,65,'#152A42',350)
    if visual in ('welcome','family','dual','small','test'):
       d.ellipse((1640,215,1735,310),fill='#91B36D')
       d.rectangle((1672,299,1704,378),fill='#A9A295')
    brand=logo.copy();brand.thumbnail((460,125),Image.Resampling.LANCZOS);im.paste(brand,(85,27),brand)
    d=ImageDraw.Draw(im);text(d,heading,100,190,65,'#F7D278',1650)
    d.rounded_rectangle((110,900,1810,1015),radius=20,fill='#101F33')
    text(d,'Illustrative image for reference',135,935,28,'#DBE6EA',1260)
    text(d,'SMART CHOICE 365  |  AUSTRALIA',1250,1035,20,'#C3D1DC',580)
    return im
def run():
 logo=Image.open(ROOT/'assets/smartchoice365-brand-logo-v1.png').convert('RGBA')
 pipeline=KPipeline(lang_code='a')
 pieces=[];times=[];audio_files=[]
 for i,item in enumerate(scene):
    im=scene_frame(i,item,logo)
    png=OUT/f'scene_{i:02}.png';im.save(png)
    print('scene',i,png,flush=True)
    spoken=item[1]
    samples=[a for _,_,a in pipeline(spoken,voice='af_heart',speed=.96)]
    if not samples:raise RuntimeError('Speech missing '+str(i))
    audio=np.concatenate(samples+[np.zeros(4800,dtype=np.float32)])
    wav=OUT/f'voice_{i:02}.wav';sf.write(wav,audio,24000)
    dur=len(audio)/24000
    mp4=OUT/f'part_{i:02}.mp4'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-loop','1','-framerate','24','-i',str(png),'-i',str(wav),'-t',str(dur),'-c:v','libx264','-preset','veryfast','-crf','25','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',str(mp4)],check=True)
    pieces.append(mp4);times.append({'scene':i,'seconds':round(dur,2)})
 (OUT/'concat.txt').write_text(''.join("file '"+x.name+"'\n" for x in pieces))
 final=OUT/'draft.mp4'
 subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i',str(OUT/'concat.txt'),'-c','copy','-movflags','+faststart',str(final)],check=True)
 duration=sum(x['seconds'] for x in times)
 assert final.stat().st_size>500000 and len(pieces)==12
 print('BUILT',final,final.stat().st_size,duration)
 if os.environ.get('GITHUB_RUN_ID'):
    identity='ninja-af141-af400-en-github-rebuild-20261031'
    digest=hashlib.sha256(final.read_bytes()).hexdigest()
    (OUT/'manifest.json').write_text(json.dumps({'id':identity,'sha256':digest,'source_run_id':int(os.environ['GITHUB_RUN_ID']),'quality_verified':False,'owner_approved_visual_exception':True,'visual_source':'original programmatically authored explanatory illustrations; not product photos','scenes':12,'video_pixels':[1920,1080],'times':times},indent=2))
if __name__=='__main__':run()
