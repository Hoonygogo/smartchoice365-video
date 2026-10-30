"""Render a sourced long-form comparison with sentence-timed Korean captions."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile
from datetime import datetime,timezone
import numpy as np
import soundfile as sf
from PIL import Image
from render import validate_request,font_path,timestamp,write_preview,MODEL_REVISION
from draw_analysis import draw_analysis

FPS=24

def run(args):
    data=validate_request(json.loads(Path(args.request).read_text()))
    if data.get('format')!='landscape': raise ValueError('Expected landscape request')
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    from supertonic import TTS
    engine=TTS(model='supertonic-3',model_dir=args.model_dir,auto_download=False,intra_op_num_threads=2,inter_op_num_threads=1)
    style=engine.get_voice_style(voice_name='F1');rate=engine.sample_rate
    speed=float(data.get('speech_speed',1.0))
    if not .8<=speed<=1.3: raise ValueError('Speech speed outside review range')
    brisk=data.get('pace')=='brisk'
    sounds=[];srt=[];chapters=[];elapsed=0.;counter=0;video_counter=0;visual_beats=0
    with tempfile.TemporaryDirectory() as td:
        tmp=Path(td);clips=[]
        for i,scene in enumerate(data['scenes'],1):
            chapters.append({'start_seconds':round(elapsed,3),'title':scene['heading'].replace('\n',' ')})
            sentences=[s.strip() for s in re.split(r'(?<=[.!?])\s+',scene['narration']) if s.strip()]
            for j,sentence in enumerate(sentences):
                counter+=1
                audio,_=engine.synthesize(sentence,voice_style=style,total_steps=8,speed=speed,lang='ko')
                audio=np.asarray(audio).reshape(-1)
                if not len(audio) or not np.isfinite(audio).all(): raise ValueError('Invalid synthesized audio')
                gap=(.18 if j==len(sentences)-1 else .08) if brisk else (.32 if j==len(sentences)-1 else .15)
                frames=math.ceil((len(audio)/rate+gap)*FPS)
                samples=round(frames/FPS*rate)
                padded=np.pad(audio,(0,samples-len(audio)))
                duration=frames/FPS;sounds.append(padded)
                srt.append(f'{counter}\n{timestamp(elapsed)} --> {timestamp(elapsed+duration)}\n{sentence}\n')
                beat_count=math.ceil(duration/3.0) if brisk else 1
                frame_parts=[frames//beat_count+(1 if k<frames%beat_count else 0) for k in range(beat_count)]
                for k,beat_frames in enumerate(frame_parts):
                    video_counter+=1
                    image=tmp/f'{video_counter:03}.png';clip=tmp/f'{video_counter:03}.mp4'
                    draw_analysis(scene,i,len(data['scenes']),sentence,image,font_path(),active=visual_beats if brisk else None)
                    visual_beats+=1
                    if video_counter==1: Image.open(image).save(out/'poster.jpg',quality=92)
                    vf='fade=t=in:st=0:d=0.10' if j==0 and k==0 else 'null'
                    subprocess.run(['ffmpeg','-y','-loglevel','error','-loop','1','-framerate',str(FPS),'-i',str(image),'-vf',vf,
                                    '-frames:v',str(beat_frames),'-an','-c:v','libx264','-preset','veryfast','-crf','21',
                                    '-profile:v','baseline','-level','4.0','-pix_fmt','yuv420p',str(clip)],check=True)
                    clips.append(clip)
                elapsed+=duration
                print(f'Scene {i}/{len(data["scenes"])} sentence {j+1}/{len(sentences)} rendered',flush=True)
        sf.write(out/'voice.wav',np.concatenate(sounds),rate)
        concat=tmp/'concat.txt';concat.write_text(''.join(f"file '{c.as_posix()}'\n" for c in clips))
        joined=tmp/'joined.mp4'
        subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(joined)],check=True)
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(joined),'-i',str(out/'voice.wav'),'-map','0:v:0','-map','1:a:0',
                        '-c:v','copy','-c:a','aac','-b:a','128k','-ar','44100','-movflags','+faststart',str(out/'draft.mp4')],check=True)
    video=out/'draft.mp4'
    if video.stat().st_size>90*1024*1024: raise ValueError('Preview exceeds size budget')
    manifest={'id':data['id'],'title':data['title'],'status':'awaiting_approval','published':False,'platform_posts':{},
              'voice':'Sarah','voice_style':'F1','model_revision':MODEL_REVISION,'format':'landscape','width':1280,'height':720,
              'guide_url':data['guide_url'],'created_at':datetime.now(timezone.utc).isoformat(),
              'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'duration_seconds':elapsed,'smoke_test_only':False,
              'sources':data['sources'],'disclosure':data['disclosure'],'chapters':chapters,'caption_segments':counter,'speech_speed':speed,'visual_beats':visual_beats,'pace':data.get('pace','standard')}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    (out/'script.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    (out/'captions.srt').write_text('\n'.join(srt))
    desc=[data['title'],'','히트텍의 보온 수치·소재·관리·사용환경을 나눠 비교합니다.',
          '단순한 보온력 순위보다 누구에게 어떤 선택이 맞는지 설명합니다.','',
          '자세한 비교표와 상황별 선택 도구: '+data['guide_url'],'',
          data['disclosure'],'','구간 안내']
    for c in chapters:
        sec=int(c['start_seconds']);desc.append(f'{sec//60}:{sec%60:02} {c["title"]}')
    desc.extend(['','공식 자료 확인: 2026-10-30',*data['sources'],'',
                 '업로드 전 확인: YouTube 고급 기능·외부 링크 작동, 사실적인 생성 장면의 AI 사용 표시, 제목·설명 및 이 파일 버전 승인.',
                 '이 파일은 검토용이며 아직 SNS에 발행하지 않았습니다.'])
    (out/'description.txt').write_text('\n'.join(desc))
    write_preview(out,data,manifest)
    preview=out/'index.html'
    preview.write_text(preview.read_text().replace('<h2>확인한 자료</h2>','<p><a href="description.txt" download>제목·설명·구간 안내 다운로드</a></p><h2>확인한 자료</h2>'))
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--request',default='requests/heattech-analysis-ko.json')
    p.add_argument('--output',default='output');p.add_argument('--model-dir',default='.models/supertonic-3')
    run(p.parse_args())
