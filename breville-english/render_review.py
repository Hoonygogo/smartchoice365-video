#!/usr/bin/env python3
"""Breville English mobile approval render: original photos + ORIGINAL logo + Kokoro af_heart.
Hard-fail before rendering if the photo pack or voice engine is absent. No espeak fallback.
"""
import hashlib,json,os,subprocess,sys
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont,ImageOps
from scripts.approved_voice import kokoro_english_pipeline,render_english_clause,approved_voice

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'breville-english'/'assets'
OUT=ROOT/'breville-english'/'out'
OUT.mkdir(parents=True,exist_ok=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
W,H=1920,1080
TOPICS=[
('BAMBINO vs BAMBINO PLUS','Welcome to Smart Choice 365. Today we compare the Breville Bambino and Bambino Plus. Is automatic milk steaming worth paying more for?'),
('TWO HOME ESPRESSO MACHINES','Both are hands-on espresso machines. Neither has a built-in grinder. The key difference is the milk routine.'),
('BAMBINO: MANUAL MILK','The regular Bambino has a manual steam wand. It suits people who enjoy learning to texture milk themselves.'),
('BAMBINO PLUS: AUTOMATIC MILK','The Plus offers automatic milk texturing with temperature and texture settings. Manual mode is still available.'),
('ESPRESSO IS NOT THE UPGRADE','Both share several espresso features. Paying extra for the Plus does not guarantee better-tasting espresso.'),
('YOUR MORNING ROUTINE','If you make flat whites every morning, automatic milk texturing may make the routine easier.'),
('AUSTRALIAN PRICE GAP','Our guide observed three hundred and ninety nine Australian dollars for Bambino, and five hundred and forty nine for Plus on October twenty ninth. Prices can change.'),
('ABOUT SEVEN CENTS PER COFFEE','A one hundred and fifty dollar difference across two milk coffees every day for three years works out to roughly seven cents per cup.'),
('DON\'T FORGET THE GRINDER','Neither machine has an integrated grinder. Include beans, milk, cleaning and grinder costs in your budget.'),
('CLEANING STILL MATTERS','Automatic milk is not automatic cleaning. The wand, portafilter and drip tray still need attention.'),
('WHO SHOULD CHOOSE WHICH','Choose Bambino for value, manual milk or black coffee. Consider Plus if you make many milk drinks and value convenience.'),
('READ OUR FULL BUYING GUIDE','Check today\'s final checkout price and read our full Australian buying guide linked in the video description.')
]
def font(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
def main():
    manifest_path=ASSETS/'approved_visual_manifest.json'
    if not manifest_path.exists():
        raise RuntimeError('NO PHOTO PACK: supply eight independently generated, visually reviewed AI photos before rendering.')
    manifest=json.loads(manifest_path.read_text())
    assets=manifest.get('assets',[])
    if len(assets)!=12:raise RuntimeError('12 scene image assignments required.')
    photos=0
    for i,a in enumerate(assets):
        if a.get('source_kind')=='single_full_frame_photo' and a.get('generation_method')=='individual_ai_generated':photos+=1
        if a.get('visual_review_passed') is not True or a.get('usage_approved') is not True:
            raise RuntimeError(f'Scene {i+1} lacks real photo approval.')
        if a.get('contact_sheet') or a.get('contains_crop_loss') or a.get('baked_in_storyboard_labels'):
            raise RuntimeError(f'Scene {i+1} has forbidden source imagery.')
        p=(ASSETS/a['file']).resolve()
        if not p.is_relative_to(ASSETS.resolve()) or not p.is_file():raise RuntimeError(f'Missing image {i+1}')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=a.get('sha256'):raise RuntimeError(f'Image hash mismatch {i+1}')
        with Image.open(p) as im:
            if im.width<1280 or im.height<720:raise RuntimeError(f'Low-resolution image {i+1}')
    if photos<8:raise RuntimeError(f'Only {photos}/8 generated photo scenes.')
    logo_path=ROOT/'assets'/'smartchoice365-brand-logo-v1.png'
    logo=Image.open(logo_path).convert('RGBA')
    pipeline=kokoro_english_pipeline()
    voice_receipts=[]
    parts=[];cues=[]
    for i,(title,narration) in enumerate(TOPICS):
        wav=OUT/f'voice_{i:02d}.wav'
        receipt=render_english_clause(pipeline,narration,wav)
        receipt['scene']=i+1
        voice_receipts.append(receipt)
        audio,sr=sf.read(wav,dtype='float32')
        rms=receipt['rms']
        source=ImageOps.exif_transpose(Image.open(ASSETS/assets[i]['file'])).convert('RGB')
        canvas=Image.new('RGB',(W,H),'#13243a')
        # Contain only, never crop any original image.
        fitted=ImageOps.contain(source,(W,680),Image.Resampling.LANCZOS)
        canvas.paste(fitted,((W-fitted.width)//2,160+(680-fitted.height)//2))
        d=ImageDraw.Draw(canvas)
        d.rectangle((0,0,W,160),fill='#10223D');d.rectangle((0,842,W,H),fill='#10223D')
        logo2=logo.copy();logo2.thumbnail((390,118),Image.Resampling.LANCZOS)
        canvas.paste(logo2,(55+(390-logo2.width)//2,18+(118-logo2.height)//2),logo2)
        d=ImageDraw.Draw(canvas)
        fs=42
        while d.textbbox((0,0),title,font=font(fs,True))[2]>1390:fs-=2
        d.text((480,50),title,font=font(fs,True),fill='#F1C35C')
        words=narration.split();rows=[];current=''
        for word in words:
            test=(current+' '+word).strip()
            if d.textbbox((0,0),test,font=font(33))[2]>1780 and current:
                rows.append(current);current=word
            else:current=test
        if current:rows.append(current)
        for line_no,row in enumerate(rows[:3]):
            d.text((70,860+line_no*45),row,font=font(33),fill='white')
        d.text((70,1034),'Illustrative image for reference   •   Independent desk research, not hands-on testing',
               font=font(21),fill='#CCD7E1')
        frame=OUT/f'frame_{i:02d}.png';canvas.save(frame)
        dur=len(audio)/sr + 0.2
        part=OUT/f'part_{i:02d}.mp4'
        subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-loop','1','-framerate','24','-i',str(frame),
                        '-i',str(wav),'-t',str(dur),'-c:v','libx264','-preset','veryfast','-crf','22',
                        '-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-ac','2','-b:a','192k',
                        '-movflags','+faststart',str(part)],check=True)
        parts.append(part);cues.append({'scene':i+1,'duration':dur,'voice':'kokoro af_heart 0.96','rms':rms})
    idx=OUT/'concat.txt';idx.write_text(''.join("file '"+p.name+"'\n" for p in parts))
    final=OUT/'breville_bambino_plus_english_review.mp4'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i',str(idx),
                    '-c','copy','-movflags','+faststart',str(final)],check=True)
    streams=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(final)]))['streams']
    if not any(x.get('codec_type')=='audio' and x.get('codec_name')=='aac' for x in streams):
        raise RuntimeError('No AAC audio in final video')
    if not any(x.get('codec_type')=='video' and x.get('width')==W and x.get('height')==H for x in streams):
        raise RuntimeError('Not full HD')
    (OUT/'voice_receipts.json').write_text(json.dumps({'voice_config_sha256':hashlib.sha256((ROOT/'config/approved_voices.json').read_bytes()).hexdigest(),'voice_files':voice_receipts},indent=2))
    (OUT/'manifest.json').write_text(json.dumps({'sha256':hashlib.sha256(final.read_bytes()).hexdigest(),
       'scenes':12,'photo_led':photos,'voice':'kokoro af_heart 0.96','logo':'official original uncropped',
       'status':'MOBILE_REVIEW_ONLY','cues':cues},indent=2))
    print('MOBILE REVIEW VIDEO COMPLETE',final,flush=True)
if __name__=='__main__':main()
