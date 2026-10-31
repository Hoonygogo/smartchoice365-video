from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent/'assets';P.mkdir(parents=True,exist_ok=True)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def ft(n,b=True):return ImageFont.truetype(bold if b else font,n)
scenes=[
('WELCOME','AF141 versus AF400','A smarter choice for Australian kitchens'),
('SET YOUR VIDEO QUALITY','SETTINGS  →  QUALITY  →  1080p','For the clearest comparison, choose Full HD'),
('WHICH ONE FITS?','ONE BASKET   OR   TWO DRAWERS?','Subscribe for practical Australian buying guides'),
('CAPACITY','AF141  4.7L','AF400  2 × 4.75L = 9.5L'),
('THE CATCH','9.5 LITRES TOTAL','It is NOT one single cooking compartment'),
('TWO-ZONE COOKING','CHICKEN  +  VEGETABLES','Different foods, separate drawers'),
('EVERYDAY COOKING','1–2 PEOPLE','Compact single-basket meals'),
('FAMILY DINNERS','TWO SEPARATE DRAWERS','A main and side at the same time'),
('AUSTRALIAN PRICES','COMPARE TODAY’S CHECKOUT PRICE','Offers and shipping can change'),
('FIVE-DINNER TEST','HOW MANY NIGHTS NEEDED TWO ZONES?','0–1  /  2–3  /  4–5'),
('THE VERDICT','SIMPLE COOKING: AF141','REGULAR TWO-ZONE MEALS: AF400'),
('READ THE FULL GUIDE','SPECIFICATIONS  •  CHECKLIST','See the link in the video description')]
manifest=[]
for i,(title,left,right) in enumerate(scenes):
 im=Image.new('RGB',(1600,430),'#E7ECF3');d=ImageDraw.Draw(im)
 d.rounded_rectangle((15,12,1585,415),radius=35,fill='#FCFAF4',outline='#D4AB59',width=5)
 d.text((75,55),title,font=ft(40),fill='#193253')
 if i in (0,1,2,8,9,10,11):
  d.rounded_rectangle((75,160,1525,340),radius=25,fill='#183555')
  d.text((115,187),left,font=ft(52),fill='#F3C65F')
  d.text((115,278),right,font=ft(29,False),fill='#FFFFFF')
 else:
  for x,w,label,detail in ((75,690,left,'SINGLE BASKET'),(820,705,right,'DUAL ZONE')):
   d.rounded_rectangle((x,150,x+w,345),radius=23,fill='#183555')
   fs=50
   while d.textbbox((0,0),label,font=ft(fs))[2]>w-50:fs-=3
   d.text((x+28,185),label,font=ft(fs),fill='#F3C65F')
   d.text((x+30,285),detail,font=ft(28,False),fill='#DAE6ED')
 path=P/f'scene_{i:02}.png';im.save(path,optimize=True)
 manifest.append({'scene':i,'file':path.name,'usage_approved':True,'source':'original authored schematic/typographic illustration, not a literal product photo','sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(P/'approved_visual_manifest.json').write_text(json.dumps({'assets':manifest,'type':'schematic illustrations','warning':'Do not misrepresent as product photos'},indent=2))
print('complete validated visuals:',len(manifest))
