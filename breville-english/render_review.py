#!/usr/bin/env python3
"""Breville English 12-scene renderer: six approved AI photos + six Python graphics.
Kokoro af_heart 0.96 only; a real synthesized WAV is the source of every focus cue.
Fails closed on missing artwork, unverifiable focus targets or TTS output.
"""
import hashlib,json,subprocess,sys,math
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont,ImageOps
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.approved_voice import kokoro_english_pipeline,render_english_clause
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'breville-english'/'assets'
OUT=ROOT/'breville-english'/'out'
LOGO=ROOT/'assets'/'smartchoice365-brand-logo-v1.png'
W,H,FPS=1920,1080,24
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
# 0-based coordinates: exactly six photo scenes, exactly six generated Python scenes.
SCENES=[
('SMART CHOICE 365','graphic',[('Welcome to Smart Choice 365.','brand'),('Today: Breville Bambino versus Bambino Plus.','title')]),
('TWO HOME ESPRESSO MACHINES','photo',[('Both are hands-on espresso machines.','machine'),('Neither has a built-in grinder.','machine')]),
('BAMBINO: MANUAL MILK','photo',[('The Bambino has a manual steam wand.','detail'),('It suits people who enjoy learning to texture milk.','machine')]),
('BAMBINO PLUS: AUTOMATIC MILK','photo',[('The Plus offers automatic milk texturing.','detail'),('You can select milk temperature and texture.','machine')]),
('MILK FEATURE COMPARISON','graphic',[('Bambino: manual steaming.','left'),('Bambino Plus: automatic or manual steaming.','right')]),
('YOUR MORNING ROUTINE','photo',[('The automatic milk option may simplify a busy morning.','detail'),('Consider how many milk coffees you make.','machine')]),
('PRICE EXAMPLE','graphic',[('In our October twenty ninth guide, Bambino was three hundred ninety nine Australian dollars.','left'),('Bambino Plus was five hundred forty nine Australian dollars.','right'),('That is a one hundred fifty dollar difference; prices change.','gap')]),
('COST PER COFFEE','graphic',[('Assuming two milk coffees a day for three years,','assumption'),('a one hundred fifty dollar premium is about seven cents per coffee.','result')]),
('BUDGET FOR THE GRINDER','photo',[('Neither machine has an integrated grinder.','machine'),('Remember to budget for a separate grinder.','detail')]),
('MAINTENANCE MATTERS','photo',[('Automatic milk does not mean automatic cleaning.','machine'),('The steam wand and drip tray still need attention.','detail')]),
('WHICH SHOULD YOU BUY?','graphic',[('Choose Bambino for manual milk and value.','left'),('Consider the Plus for regular milk coffees and convenience.','right')]),
('READ THE FULL GUIDE','graphic',[('Check the latest checkout price.','price'),('Read the full comparison on Smart Choice 365.','brand')]),
]
PHOTO_SCENES=[1,2,3,5,8,9]
GRAPHIC_SCENES=[0,4,6,7,10,11]
def font(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
def must(cond,message):
    if not cond:raise RuntimeError(message)
def fit_text(d,t,box,maximum=46):
    x1,y1,x2,y2=box
    for size in range(maximum,17,-1):
        fn=font(size,True)
        bb=d.textbbox((0,0),t,font=fn)
        if bb[2]-bb[0]<x2-x1-25:return fn
    raise RuntimeError('Text does not fit chart: '+t)
def validate():
    must(LOGO.is_file(),'Official logo missing')
    manifest=ASSETS/'approved_visual_manifest.json'
    must(manifest.is_file(),'No approved image manifest. No placeholder or collage fallback.')
    data=json.loads(manifest.read_text())
    photos=data.get('photos',[])
    must(len(photos)==6,'Require exactly 6 independent original photo entries')
    must([a.get('scene') for a in photos]==PHOTO_SCENES,'Photo scenes must be 2,3,4,6,9,10 in the manifest')
    images={}
    seen=set()
    for a in photos:
        i=a['scene'];path=(ASSETS/a.get('file','')).resolve()
        must(path.is_relative_to(ASSETS.resolve()) and path.is_file(),f'Photo {i} missing or path invalid')
        raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest()
        must(sha==a.get('sha256'),'Photo hash differs: '+str(i))
        must(sha not in seen,'Duplicate photo: '+str(i));seen.add(sha)
        must(a.get('independent_generation') is True and a.get('single_scene') is True and a.get('visually_checked') is True and a.get('storyboard_collage') is False,'Unapproved/collage photo: '+str(i))
        with Image.open(path) as im:
            must(im.width>=1280 and im.height>=720,'Photo too small: '+str(i))
        boxes=a.get('focus_regions',{})
        must(all(k in boxes for _,k in SCENES[i][2]),'Unverified photo focus region missing in scene '+str(i))
        for key,coords in boxes.items():
            must(len(coords)==4 and all(isinstance(n,(float,int)) and 0<=n<=1 for n in coords),'Focus region must be normalized box')
            must(coords[0]<coords[2] and coords[1]<coords[3],'Invalid focus box')
        images[i]=(path,boxes)
    return images
def draw_base(i,photos):
    title,kind,segments=SCENES[i]
    image=Image.new('RGB',(W,H),'#101e34');d=ImageDraw.Draw(image)
    if kind=='photo':
        path,boxes=photos[i]
        with Image.open(path) as raw:
            src=ImageOps.exif_transpose(raw).convert('RGB')
        fitted=ImageOps.contain(src,(W-80,H-320),Image.Resampling.LANCZOS)
        x=(W-fitted.width)//2;y=170+(H-340-fitted.height)//2
        image.paste(fitted,(x,y))
        regions={k:(x+int(v[0]*fitted.width),y+int(v[1]*fitted.height),
                    x+int(v[2]*fitted.width),y+int(v[3]*fitted.height)) for k,v in boxes.items()}
    else:
        regions={}
        cards={
            0:[('SMART CHOICE 365',(310,330,1610,570),'brand'),('BAMBINO  vs  BAMBINO PLUS',(260,610,1660,805),'title')],
            4:[('Manual steaming',(100,310,910,795),'left'),('Automatic + manual',(1010,310,1820,795),'right')],
            6:[('BAMBINO  A$399',(95,305,910,770),'left'),('BAMBINO PLUS  A$549',(1010,305,1825,770),'right'),('A$150 difference',(605,790,1315,885),'gap')],
            7:[('2 coffees/day × 3 years',(145,330,1770,590),'assumption'),('≈ A$0.07 PER COFFEE',(145,615,1770,840),'result')],
            10:[('BAMBINO: VALUE',(100,325,910,800),'left'),('PLUS: MILK CONVENIENCE',(1010,325,1820,800),'right')],
            11:[('CHECK LATEST PRICE',(240,325,1680,560),'price'),('SMART CHOICE 365',(240,605,1680,820),'brand')]
        }[i]
        for label,rect,key in cards:
            d.rounded_rectangle(rect,radius=26,fill='#1e3957',outline='#536c89',width=4)
            fn=fit_text(d,label,rect,62)
            bb=d.textbbox((0,0),label,font=fn)
            d.text(((rect[0]+rect[2]-(bb[2]-bb[0]))/2,(rect[1]+rect[3]-(bb[3]-bb[1]))/2-10),label,font=fn,fill='#f5f7fb')
            regions[key]=rect
    d.rectangle((0,0,W,150),fill='#0c182b')
    d.text((455,46),title,font=font(48,True),fill='#f9cc62')
    with Image.open(LOGO) as logo:
        mark=logo.convert('RGBA');mark.thumbnail((385,125),Image.Resampling.LANCZOS)
        image.paste(mark,(35+(385-mark.width)//2,12+(125-mark.height)//2),mark)
    d.rectangle((0,H-145,W,H),fill='#0c182b')
    d.text((50,1030),'Illustrative visuals • Independent buying guide • Verify current prices',font=font(22),fill='#aabfd5')
    return image,regions
def render():
    photos=validate()
    OUT.mkdir(parents=True,exist_ok=True)
    voice=kokoro_english_pipeline()
    parts=[];cues=[];receipts=[]
    for i,(title,kind,segments) in enumerate(SCENES):
        base,regions=draw_base(i,photos)
        for j,(spoken,target) in enumerate(segments):
            must(target in regions,f'Scene {i+1}: focus target {target} missing')
            wav=OUT/f'voice_{i:02d}_{j:02d}.wav'
            receipt=render_english_clause(voice,spoken,wav)
            audio,sr=sf.read(wav,dtype='float32')
            duration=len(audio)/sr
            must(duration>0.6,'Insufficient spoken audio')
            image=base.copy();d=ImageDraw.Draw(image)
            x1,y1,x2,y2=regions[target]
            d.rounded_rectangle((x1-12,y1-12,x2+12,y2+12),radius=20,outline='#ffda44',width=11)
            d.rounded_rectangle((x1-4,y1-4,x2+4,y2+4),radius=18,outline='#ffed99',width=3)
            # The exact spoken clause appears during its independently synthesized audio.
            ft=font(32,True)
            max_width=W-100
            words=spoken.split();lines=[];row=''
            for word in words:
                proposal=(row+' '+word).strip()
                if d.textbbox((0,0),proposal,font=ft)[2]>max_width and row:
                    lines.append(row);row=word
                else:row=proposal
            if row:lines.append(row)
            must(len(lines)<=2,'Spoken caption too long')
            for n,line in enumerate(lines):
                d.text((55,910+n*44),line,font=ft,fill='#ffffff',stroke_width=2,stroke_fill='#0c182b')
            frame=OUT/f'frame_{i:02d}_{j:02d}.jpg'
            image.save(frame,quality=91)
            part=OUT/f'part_{i:02d}_{j:02d}.mp4'
            subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-loop','1','-framerate',str(FPS),
                            '-i',str(frame),'-i',str(wav),'-t',str(duration),'-c:v','libx264',
                            '-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-c:a','aac',
                            '-ar','48000','-ac','2','-b:a','160k',str(part)],check=True)
            parts.append(part);receipts.append({**receipt,'scene':i+1,'segment':j+1})
            cues.append({'scene':i+1,'segment':j+1,'target':target,'spoken':spoken,'duration_seconds':duration,'audio_sha256':receipt['sha256']})
    concat=OUT/'concat.txt'
    concat.write_text(''.join("file '"+x.name+"'\n" for x in parts))
    final=OUT/'breville_bambino_plus_english_review.mp4'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i',str(concat),
                    '-c','copy','-movflags','+faststart',str(final)],check=True)
    streams=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(final)]))['streams']
    must(any(x.get('codec_type')=='audio' and x.get('codec_name')=='aac' for x in streams),'Missing AAC voice')
    must(any(x.get('codec_type')=='video' and x.get('width')==W and x.get('height')==H for x in streams),'Not 1080p')
    must(len({x['scene'] for x in cues})==12 and len(receipts)==len(cues),'Scene/voice mismatch')
    (OUT/'manifest.json').write_text(json.dumps({'status':'MOBILE_REVIEW_ONLY','photos':6,'python_graphics':6,'scenes':12,'cues':cues,'sha256':hashlib.sha256(final.read_bytes()).hexdigest()},indent=2))
    (OUT/'voice_receipts.json').write_text(json.dumps({'voice_files':receipts},indent=2))
    print('PASS: Kokoro voice, clause-synchronized focus boxes, 6 photos and 6 graphics',final)
if __name__=='__main__':render()
