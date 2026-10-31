"""Reusable, approval-only English guide renderer matching the approved Korean layout."""
import argparse,hashlib,html,json,math,os,subprocess,sys
from pathlib import Path
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from approved_voice import approved_voice,kokoro_english_pipeline,render_english_clause
from guide_video_layout import Layout
from video_visual_core import validate_original_scene
ROOT=Path(__file__).resolve().parents[1];FPS=24

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def stamp(t):return f'{int(t//3600):02}:{int(t//60)%60:02}:{int(t)%60:02},{round(t%1*1000):03}'
def validate(req,review_required=True):
 assert req['language']=='en' and len(req['scenes'])==12
 assert req['guide_url'].startswith('https://smartchoice365-web.pages.dev/guides/')
 photos=[s['photo'] for s in req['scenes'] if s['visual']=='photo'];assert len(photos)>=8 and len(set(photos))==len(photos)
 manifest=ROOT/req['asset_dir']/'visual_manifest.json'
 assets=json.loads(manifest.read_text())['assets'] if manifest.exists() else []
 for s in req['scenes']:
  targets={f'row{k}' for k in range(len(s['rows']))}
  for c in s['cues']:assert c['text'].strip() and set(c['targets'])<=targets
  if s['visual']=='photo':
   p=ROOT/req['asset_dir']/f'{s["photo"]}.png';im=Image.open(p);assert im.width>=1600 and im.height>=900
   if review_required:
    a=next(x for x in assets if x['file']==p.name);validate_original_scene(a);assert sha(p)==a['sha256']
 return req

def main():
 p=argparse.ArgumentParser();p.add_argument('--request',required=True);p.add_argument('--storyboard-only',action='store_true');args=p.parse_args()
 req=json.loads((ROOT/args.request).read_text());validate(req,not args.storyboard_only);out=ROOT/req['output_dir'];out.mkdir(parents=True,exist_ok=True);layout=Layout(req)
 # Build and inspect all scene compositions before final audio/video assembly.
 for si,s in enumerate(req['scenes']):
  for ci,c in enumerate(s['cues']):layout.draw(si,c,out/f'layout_check_{si:02}_{ci:02}.png')
  layout.draw(si,s['cues'][0],out/f'scene_{si:02}.png')
 if args.storyboard_only:
  sheet=Image.new('RGB',(1200,900),'white')
  for si in range(12):
   im=Image.open(out/f'scene_{si:02}.png');im.thumbnail((400,225));sheet.paste(im,(si%3*400,si//3*225))
  sheet.save(out/'storyboard.jpg');print('STORYBOARD_READY');return
 review=json.loads((ROOT/req['asset_dir']/'visual_manifest.json').read_text());assert review.get('composed_storyboard_reviewed') is True
 voice=approved_voice('english');assert (voice['voice'],voice['speed'],voice['sample_rate'])==('af_heart',0.96,24000)
 import torch
 torch.set_num_threads(2)
 pipeline=kokoro_english_pipeline();audio=[];timings=[];frame=0;receipts=[];cache=out/'audio';cache.mkdir(exist_ok=True)
 for si,s in enumerate(req['scenes']):
  for ci,c in enumerate(s['cues']):
   identity=hashlib.sha256(json.dumps({'text':c['text'],'voice':voice},sort_keys=True).encode()).hexdigest();wav=cache/f'{identity}.wav';receipt=wav.with_suffix('.json')
   if not wav.exists() or not receipt.exists():
    vr=render_english_clause(pipeline,c['text'],wav);vr['text']=c['text'];vr['identity']=identity;receipt.write_text(json.dumps(vr,indent=2))
   vr=json.loads(receipt.read_text());assert vr['identity']==identity and vr['sha256']==sha(wav)
   raw,sr=sf.read(wav,dtype='float32');assert sr==24000 and np.isfinite(raw).all();assert float(np.sqrt(np.mean(raw*raw)))>.008
   frames=math.ceil((len(raw)/sr+.12)*FPS);samples=round(frames/FPS*sr);audio.append(np.pad(raw,(0,samples-len(raw))))
   timings.append({'scene':si,'cue':ci,'start':frame/FPS,'end':(frame+frames)/FPS,'frames':frames,'narration':c['text'],'targets':c['targets'],'voice_sha256':vr['sha256']});frame+=frames;receipts.append(vr);print('VOICE',si,ci,round(len(raw)/sr,3),flush=True)
 sf.write(out/'voice.wav',np.concatenate(audio),24000);(out/'voice_receipts.json').write_text(json.dumps(receipts,indent=2));(out/'cue_timings.json').write_text(json.dumps(timings,indent=2))
 clips=[];frame_evidence=[]
 for n,t in enumerate(timings):
  si=t['scene'];cue=req['scenes'][si]['cues'][t['cue']];image=out/f'frame_{n:02}.png';regions=layout.draw(si,cue,image);clip=out/f'clip_{n:02}.mp4'
  subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-loop','1','-framerate',str(FPS),'-i',str(image),'-frames:v',str(t['frames']),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',str(clip)],check=True);clips.append(clip)
  frame_evidence.append({'scene':si,'cue':t['cue'],'frame_sha256':sha(image),'regions':regions,'targets':t['targets']});print('FRAME',n,flush=True)
 (out/'concat.txt').write_text(''.join(f"file '{c}'\n" for c in clips));final=out/req['output_name']
 subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-f','concat','-safe','0','-i',str(out/'concat.txt'),'-i',str(out/'voice.wav'),'-c:v','copy','-c:a','aac','-b:a','128k','-movflags','+faststart',str(final)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(final)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio');assert (v['width'],v['height'],v['codec_name'],a['codec_name'])==(1920,1080,'h264','aac');assert abs(float(probe['format']['duration'])-frame/FPS)<.2
 subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-i',str(final),'-vn','-ac','1','-ar','24000',str(out/'decoded_audio.wav')],check=True);decoded,sr=sf.read(out/'decoded_audio.wav');rms=float(np.sqrt(np.mean(decoded**2)));assert rms>.008
 (out/'captions.srt').write_text('\n\n'.join(f'{n+1}\n{stamp(t["start"])} --> {stamp(t["end"])}\n{t["narration"]}' for n,t in enumerate(timings)))
 (out/'frame_evidence.json').write_text(json.dumps(frame_evidence,indent=2));(out/'script.json').write_text(json.dumps(req,indent=2));chapters=[]
 for si,s in enumerate(req['scenes']):
  start=next(t['start'] for t in timings if t['scene']==si);chapters.append({'start':start,'title':s['heading']})
 m={'id':req['id'],'title':req['title'],'status':'awaiting_user_approval','published':False,'sha256':sha(final),'duration':frame/FPS,'width':1920,'height':1080,'voice':voice,'decoded_audio_rms':rms,'caption_segments':len(timings),'photo_led_scenes':8,'guide_url':req['guide_url'],'sources':req['sources'],'chapters':chapters,'visual_review':'Source images and all composed storyboard frames inspected; encoded frame inspection still required before delivery'}
 (out/'manifest.json').write_text(json.dumps(m,indent=2));desc='Full buying checklist and worked examples: '+req['guide_url']+'\n\nOfficial-source research and Smart Choice 365 editorial analysis; not hands-on testing. Generic AI-created illustrative scenes are not official manufacturer photographs. All cost examples are hypothetical, not real products, retail prices or electricity offers. The linked guide contains affiliate advertising.\n\n'+'\n'.join(req['sources']);(out/'description.txt').write_text(desc)
 title=html.escape(req['title']);filename=html.escape(req['output_name']);guide=html.escape(req['guide_url'],quote=True);(out/'index.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>body{{max-width:1100px;margin:25px auto;padding:15px;font-family:system-ui;background:#f5f3ee;color:#13243a}}video{{width:100%}}</style><h1>{title}</h1><p>1080p · Kokoro af_heart · Review copy, not published</p><video controls playsinline preload="metadata" src="{filename}"></video><p><a href="{filename}" download>Download MP4</a> · <a href="{guide}">Full buying guide</a></p></html>')
 print(json.dumps(m),flush=True)
if __name__=='__main__':main()
