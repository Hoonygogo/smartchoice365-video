"""Korean Padding/Heattech visual standard, localised for reusable English guides."""
import math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from video_visual_core import place_full,focus_on_regions
ROOT=Path(__file__).resolve().parents[1]
W,H=1920,1080;NAVY='#13243a';GOLD='#d9a84e';BG='#f5f3ee';MUTED='#58677b'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
class Layout:
 def __init__(self,request):self.request=request;self.regions={}
 def draw(self,index,cue,path):
  s=self.request['scenes'][index];im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);regions={}
  def f(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
  def text(t,x,y,n=44,c=NAVY,b=False):d.text((x,y),t,font=f(n,b),fill=c)
  def wrap(t,x,y,n,width,c=NAVY,lines=3,b=False):
   rows=[];part=''
   for word in t.split():
    test=(part+' '+word).strip()
    if part and d.textlength(test,font=f(n,b))>width:rows.append(part);part=word
    else:part=test
   if part:rows.append(part)
   if len(rows)>lines:raise ValueError('Text overflow: '+t)
   for j,row in enumerate(rows):
    if d.textlength(row,font=f(n,b))>width:raise ValueError('Unbreakable text overflow')
    text(row,x,y+j*(n+11),n,c,b)
   return y+len(rows)*(n+11)
  def logo(rect):place_full(im,Image.open(ROOT/'assets/smartchoice365-brand-logo-v1.png'),rect)
  d.rectangle((0,0,W,92),fill=NAVY);text('SMART CHOICE 365',64,19,39,'white');text('AUSTRALIAN BUYING GUIDE',1260,28,29,'#ead1a0')
  mode=s['visual']
  if mode=='brand_intro':
   logo((185,135,1735,525));wrap('Air conditioning:',240,585,65,1450,b=True);wrap('compare the real cost',240,670,62,1450,b=True);text('smartchoice365-web.pages.dev',490,791,38,MUTED)
  elif mode=='quality_intro':
   text('Make the comparison easier to see',80,145,66,b=True)
   for j,label in enumerate(s['rows']):
    x=80+j*620;d.rounded_rectangle((x,330,x+510,690),25,fill=NAVY if j==2 else 'white');regions[f'row{j}']=(x,330,x+510,690)
    if j==0:
     cx=x+255;cy=440
     for k in range(8):
      a=k*math.pi/4;d.line((cx+38*math.cos(a),cy+38*math.sin(a),cx+63*math.cos(a),cy+63*math.sin(a)),fill=NAVY,width=17)
     d.ellipse((cx-45,cy-45,cx+45,cy+45),fill=NAVY);d.ellipse((cx-19,cy-19,cx+19,cy+19),fill='white')
    else:text('HD' if j==1 else '1080p',x+95,385,78,GOLD,b=True)
    wrap(label,x+35,555,39,440,'white' if j==2 else NAVY,lines=2,b=True)
    if j<2:
     d.line((x+533,485,x+588,485),fill=GOLD,width=10);d.polygon([(x+605,485),(x+574,466),(x+574,504)],fill=GOLD)
   text(s['note'],85,785,30,MUTED)
  else:
   wrap(s['heading'],65,127,61,1790,lines=1,b=True)
   if mode=='photo':
    source=ROOT/self.request['asset_dir']/f'{s["photo"]}.png';place_full(im,Image.open(source),(55,235,1115,775));text('Illustrative image for reference',70,799,27,MUTED)
    for j,row in enumerate(s['rows']):
     y=278+j*157;regions[f'row{j}']=(1170,y-10,1850,y+125);text(f'0{j+1}',1190,y,31,'#8b6426');wrap(row,1190,y+43,40,630,lines=2)
    if index==len(self.request['scenes'])-1:logo((1530,750,1840,815))
   elif mode=='energy_chart':
    text('Annual cooling energy × your electricity rate',80,244,43)
    for j,(label,energy,cost) in enumerate([('Option A',900,270),('Option B',600,180)]):
     y=350+j*168;regions[f'row{j}']=(70,y-15,1850,y+112);text(label,90,y+20,47,b=True)
     x=440;end=x+energy*1.1;d.rounded_rectangle((x,y,end,y+98),16,fill=NAVY if j==0 else '#92712e');text(f'{energy} kWh',x+25,y+20,46,'white',True);text(f'A${cost}/year',1500,y+22,43,b=True)
    regions['row2']=(70,716,1850,802);text('Difference: A$90/year at A$0.30/kWh',100,730,49,'#8b6426',True)
   elif mode=='payback_chart':
    text('Hypothetical extra installed cost: A$450',80,245,46)
    for j,(rate,saving,years) in enumerate([('A$0.30/kWh','A$90/year','5 years'),('A$0.40/kWh','A$120/year','3.75 years')]):
     x=70+j*915;d.rounded_rectangle((x,340,x+870,713),24,fill=NAVY if j==0 else '#e2e7ec');regions[f'row{j}']=(x,340,x+870,713);col='white' if j==0 else NAVY
     text(rate,x+35,380,46,col);text(saving+' saved',x+35,471,47,col);text(years,x+35,575,72,GOLD if j==0 else NAVY,True)
    text('Extra cost ÷ estimated annual savings',80,758,42)
   else:raise ValueError('Unsupported visual '+mode)
   text(s['note'],70,837,25,MUTED)
  focus_on_regions(im,regions,cue['targets'])
  d.rectangle((0,882,W,H),fill=NAVY);wrap(cue['text'],70,898,44,1780,'white',lines=3)
  d.rectangle((0,1072,int(W*(index+1)/len(self.request['scenes'])),1079),fill=GOLD)
  im.save(path);self.regions[index]=regions
  return regions
