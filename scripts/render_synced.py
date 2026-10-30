"""Build highlight timing directly from each narrated clause's generated audio."""
import argparse
from datetime import datetime,timezone
import hashlib
import html
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import numpy as np
import soundfile as sf
from PIL import Image
from supertonic import TTS
from render import validate_request,timestamp,MODEL_REVISION
from draw_graph_hd import draw
from draw_intro import draw_intro

FPS=24

def main():
    p=argparse.ArgumentParser();p.add_argument('--request',default='requests/heattech-full-photo-ko-v8.json');p.add_argument('--output',default='output');p.add_argument('--model-dir',default='.models/supertonic-3');args=p.parse_args()
    data=validate_request(json.loads(Path(args.request).read_text()))
    for scene in data['scenes']:
        if ' '.join(c['text'] for c in scene['cues'])!=scene['narration']:raise ValueError('Speech cues changed the approved script')
    engine=TTS(model='supertonic-3',model_dir=args.model_dir,auto_download=False,intra_op_num_threads=2,inter_op_num_threads=1)
    style=engine.get_voice_style(voice_name='F1');rate=engine.sample_rate
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    sounds=[];cues=[];chapters=[];srt=[];frame=0
    with tempfile.TemporaryDirectory() as td:
        tmp=Path(td);clips=[]
        for i,scene in enumerate(data['scenes']):
            chapters.append({'start_seconds':frame/FPS,'title':scene['heading'].replace('\n',' ')})
            for j,cue in enumerate(scene['cues']):
                raw,_=engine.synthesize(cue['text'],voice_style=style,total_steps=8,speed=data['speech_speed'],lang='ko')
                raw=np.asarray(raw).reshape(-1)
                if not len(raw) or not np.isfinite(raw).all():raise ValueError('Invalid generated speech')
                gap=.18 if j==len(scene['cues'])-1 else (.04 if cue['text'].endswith(',') else .08)
                frames=math.ceil((len(raw)/rate+gap)*FPS);samples=round(frames/FPS*rate)
                sounds.append(np.pad(raw,(0,samples-len(raw))))
                start=frame/FPS;frame+=frames;end=frame/FPS
                caption=cue.get('caption',cue['text'])
                item={'scene':i+1,'mode':scene['visual'],'text':cue['text'],'targets':cue['targets'],'start_seconds':start,'end_seconds':end,'speech_seconds':len(raw)/rate,'caption':caption}
                cues.append(item);n=len(cues)
                srt.append(f'{n}\n{timestamp(start)} --> {timestamp(end)}\n{caption}\n')
                image=tmp/f'{n}.png';clip=tmp/f'{n}.mp4'
                renderer=draw_intro if scene['visual'].endswith('_intro') else draw
                renderer(scene,i+1,len(data['scenes']),caption,cue['targets'],image)
                if n==1:Image.open(image).save(out/'poster.jpg',quality=95)
                subprocess.run(['ffmpeg','-y','-loglevel','error','-loop','1','-framerate',str(FPS),'-i',str(image),'-frames:v',str(frames),'-an','-c:v','libx264','-preset','veryfast','-crf','18','-profile:v','high','-level','4.1','-pix_fmt','yuv420p',str(clip)],check=True)
                clips.append(clip)
                print(f'Cue {n}: scene {i+1}, targets={cue["targets"]}, {start:.3f}-{end:.3f}s',flush=True)
        sf.write(out/'voice.wav',np.concatenate(sounds),rate)
        concat=tmp/'concat.txt';concat.write_text(''.join(f"file '{c.as_posix()}'\n" for c in clips))
        subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-i',str(out/'voice.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','128k','-movflags','+faststart',str(out/'draft.mp4')],check=True)
    m={'id':data['id'],'title':data['title'],'status':'awaiting_approval','published':False,'platform_posts':{},'voice':'Sarah','voice_style':'F1','speech_speed':data['speech_speed'],'model_revision':MODEL_REVISION,'format':'landscape','width':1920,'height':1080,'duration_seconds':frame/FPS,'sha256':hashlib.sha256((out/'draft.mp4').read_bytes()).hexdigest(),'created_at':datetime.now(timezone.utc).isoformat(),'guide_url':data['guide_url'],'sources':data['sources'],'disclosure':data['disclosure'],'chapters':chapters,'caption_segments':len(cues),'highlight_timing':'Explicit editorial targets bound to generated clause audio; no periodic cycling'}
    (out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));(out/'script.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));(out/'cue_timings.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2));(out/'captions.srt').write_text('\n'.join(srt))
    digest=m['sha256'][:12];title=html.escape(m['title']);guide=html.escape(data['guide_url'],quote=True)
    links=''.join(f'<li><a href="{html.escape(url,quote=True)}">{html.escape(url)}</a></li>' for url in data['sources'])
    (out/'index.html').write_text(f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>body{{font-family:system-ui;max-width:1100px;margin:30px auto;padding:0 18px;background:#f5f3ee;color:#13243a}}video{{width:100%;background:#13243a}}p{{line-height:1.7}}a{{overflow-wrap:anywhere}}.button{{display:inline-block;background:#13243a;color:white;padding:12px;margin:12px 12px 12px 0;border-radius:8px}}</style><h1>모델 사진 잘림을 고친 히트텍 비교</h1><p>1080p · Sarah 한국어 음성 · 새 버전 확인 대기 · SNS 미발행</p><video controls playsinline preload="metadata" src="draft.mp4?v={digest}" poster="poster.jpg?v={digest}"></video><a class="button" href="draft.mp4?v={digest}" download>영상 다운로드</a><a class="button" href="{guide}">구매가이드</a><p>로고와 인사, 화질 설정 그림, 구독 안내를 추가했습니다. 본문은 설명에 맞춰 비교 항목을 강조합니다.</p><h2>제작 및 자료 안내</h2><p>{html.escape(data['disclosure'])}</p><ul>{links}</ul></html>''')
    print(json.dumps(m,ensure_ascii=False))
if __name__=='__main__':main()
