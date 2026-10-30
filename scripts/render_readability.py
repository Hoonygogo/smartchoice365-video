"""Native 1080p readability experiment, reusing the approved audio and timing."""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

W,H=1920,1080
BG='#f6f3eb'; INK='#15283d'; GOLD='#d9a84e'
CARDS={
'hero':[('난방 실내 중심','일반부터 비교','가장 높은 등급이 정답은 아니에요'),('선택 기준','내 생활환경','소재 · 세탁 · 입는 횟수')],
 'temperature':[('일반','5 ~ 20°C','브랜드 안내 참고 구간'),('코튼 엑스트라웜','-5 ~ 15°C','서로 겹치는 구간에 주목'),('울트라웜','-20 ~ 10°C','개인 체감 · 안전기온 보장 아님')],
'warmth':[('코튼 엑스트라웜','1.5배','기본 소재 대비 제조사 CLO 시험'),('울트라웜','2.25배','체감 온도가 그 배수가 되는 뜻 아님')],
'cotton':[('피부에 닿는 면','코튼 100%','옷 전체의 혼용률과 구분'),('확인한 BLACK 타이즈 몸판','면 64%','아크릴 28% · 폴리우레탄 8%'),('구매 전 확인','모델 + 색상','제품마다 전체 소재표를 확인')],
'laundry':[('확인한 타이즈 두 종류','건조기 사용 불가','코튼 엑스트라웜 · 울트라웜'),('다른 모델은?','세탁표 확인','같은 조건이라고 가정하지 마세요')],
'office':[('가상 하루 패턴','통근 40분','난방 실내는 8시간'),('우리의 출발점','일반부터 비교','오래 머무는 환경을 먼저'),('추위를 많이 탄다면','중간 단계도 비교','난방 · 외투 · 개인 체감 고려')],
'outside':[('추운 야외 대기가 길다면','울트라웜 검토','자료를 참고한 편집 판단'),('바람이 강한 날','방풍 외투도 함께','내의만이 아닌 전체 옷 조합'),('많이 움직이는 날','땀과 답답함도 고려','보온력만으로 결정하지 않기')],
'cost':[('설명용 가상 가격','20,000원 ÷ 40회','1회당 500원'),('설명용 가상 가격','30,000원 ÷ 5회','1회당 6,000원'),('실제 판매가격 아님','자주 입을 환경인가?','가상 산술 예시 · 관리비 제외')],
'decision':[('난방 실내 중심','일반부터 비교','개인 체감과 외투에 따라 조정'),('쌀쌀한 실내외 이동','코튼 엑스트라웜','자료 기반 편집 추천'),('추운 야외 체류가 긴 날','울트라웜 검토','보온 · 안전 한계를 보장하지 않음'),('더 자세한 비교','설명란 구매가이드','직접 착용시험을 하지 않은 자료 비교')]
}

def font_path():
    p=os.getenv('SC365_FONT','/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
    if not Path(p).is_file():raise ValueError('Korean font missing')
    return p

def draw(scene,index,total,caption,card_index,path):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);font=font_path()
    def text(s,x,y,size,color=INK):d.text((x,y),s,font=ImageFont.truetype(font,size),fill=color)
    def block(s,x,y,size,width,max_lines,color=INK):
        lines=[];line='';f=ImageFont.truetype(font,size)
        for c in s.replace('\n',' '):
            if line and d.textlength(line+c,font=f)>width:lines.append(line.strip());line=c
            else:line+=c
        if line:lines.append(line.strip())
        if len(lines)>max_lines:raise ValueError('Text overflow: '+s)
        for n,line in enumerate(lines):text(line,x,y+n*(size+12),size,color)
    d.rectangle((0,0,W,100),fill=INK)
    text('SMART CHOICE 365',72,20,42,'white');text(f'{index:02} / {total:02}',1640,20,42,'white')
    block(scene['heading'],72,132,84,1776,2)
    label,value,note=CARDS[scene['visual']][card_index%len(CARDS[scene['visual']])]
    d.rounded_rectangle((64,370,1856,768),30,fill=INK)
    block(label,110,392,62,1700,1,'#ffe0a0')
    block(value,110,475,104,1700,1,'white')
    block(note,110,630,54,1700,2,'white')
    # Three large caption lines maximum; exact original narrated sentence.
    block(caption,72,800,54,1776,3)
    text('자료 기반 비교 · 직접 착용시험 아님 · 상세 출처는 설명란',72,1020,32,'#4f5966')
    im.save(path)


def stamp(s):
    h,m,sec=s.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(sec)

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',default='approved-source');p.add_argument('--output',default='output');args=p.parse_args()
    source=Path(args.source);out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    original=json.loads((source/'manifest.json').read_text());data=json.loads((source/'script.json').read_text())
    expected='dcc5e67cc8d450b5ae8a0e2f42147023b4a6a678c4e8cad4807a9ec342ff8229'
    if hashlib.sha256((source/'draft.mp4').read_bytes()).hexdigest()!=expected:raise ValueError('Reference source mismatch')
    segments=[]
    for b in (source/'captions.srt').read_text().strip().split('\n\n'):
        lines=b.splitlines();start,end=lines[1].split(' --> ')
        segments.append((stamp(start),stamp(end),' '.join(lines[2:])))
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp=Path(tmpdir);clips=[];counts={};last_frame=0
        for n,(start,end,caption) in enumerate(segments):
            idx=max(i for i,c in enumerate(original['chapters']) if c['start_seconds']<=start+.002)
            frames=round(end*24)-last_frame;last_frame+=frames
            k=counts.get(idx,0);counts[idx]=k+1
            image=tmp/f'{n}.png';clip=tmp/f'{n}.mp4'
            draw(data['scenes'][idx],idx+1,len(data['scenes']),caption,k,image)
            if n==0:Image.open(image).save(out/'poster.jpg',quality=95)
            subprocess.run(['ffmpeg','-y','-loglevel','error','-loop','1','-framerate','24','-i',str(image),'-frames:v',str(frames),'-an','-c:v','libx264','-preset','veryfast','-crf','18','-profile:v','high','-level','4.1','-pix_fmt','yuv420p',str(clip)],check=True)
            clips.append(clip);print(f'1080p sentence {n+1}/{len(segments)}',flush=True)
        concat=tmp/'concat.txt';concat.write_text(''.join(f"file '{c.as_posix()}'\n" for c in clips))
        subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-i',str(source/'voice.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','128k','-movflags','+faststart',str(out/'draft.mp4')],check=True)
    # Both low-resolution samples use the same codec and settings. This simulates, not reproduces, YouTube encoding.
    for name,video in [('old-240',source/'draft.mp4'),('new-240',out/'draft.mp4')]:
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(video),'-vf','scale=-2:240:flags=lanczos','-c:v','libx264','-crf','26','-preset','veryfast','-c:a','aac','-b:a','96k','-movflags','+faststart',str(out/f'{name}.mp4')],check=True)
    for name,video in [('old-240',out/'old-240.mp4'),('new-240',out/'new-240.mp4')]:
        subprocess.run(['ffmpeg','-y','-loglevel','error','-ss','16','-i',str(video),'-frames:v','1',str(out/f'{name}.png')],check=True)
    m={**original,'id':'heattech-readability-ko-v3','title':original['title']+' | 가독성 실험','width':W,'height':H,'created_at':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256((out/'draft.mp4').read_bytes()).hexdigest(),'audio_reused_from':original['sha256'],'status':'awaiting_approval','published':False,'platform_posts':{},'experiment':'Native 1080p, one key card per screen; equal-encoding 240p comparison'}
    (out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
    shutil.copy(source/'voice.wav',out/'voice.wav');shutil.copy(source/'captions.srt',out/'captions.srt')
    data['id']=m['id'];data['title']=m['title'];(out/'script.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    title=html.escape(m['title']);guide=html.escape(data['guide_url'],quote=True)
    (out/'index.html').write_text(f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>body{{font-family:system-ui;margin:24px auto;max-width:1200px;padding:0 16px;background:#f6f3eb;color:#15283d}}video,img{{width:100%;background:#15283d}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}@media(max-width:750px){{.grid{{grid-template-columns:1fr}}}}button,a{{display:inline-block;margin:10px 10px 10px 0;padding:12px;background:#15283d;color:white;border:0;border-radius:8px}}p{{line-height:1.7}}</style><h1>글자 크기와 화질 비교 실험</h1><p>목소리·대본·길이는 기존과 동일합니다. 새 영상은 1920×1080에서 직접 그렸고, 한 화면에 핵심 카드 하나를 크게 보여줍니다. SNS 미발행 · 확인 대기.</p><h2>새 1080p 원본</h2><video controls playsinline preload="metadata" src="draft.mp4" poster="poster.jpg"></video><a href="draft.mp4" download>1080p 영상 다운로드</a><a href="{guide}">구매가이드</a><h2>둘 다 240p로 낮추면?</h2><p>동일한 인코딩 설정으로 줄인 자체 실험입니다. 유튜브 실제 240p 화질이나 자동 선택을 보장하지 않습니다. 두 영상은 같은 내레이션 시점입니다.</p><button onclick="let v=document.querySelectorAll('.grid video');v.forEach(x=>{{x.currentTime=13;x.play()}})">13초부터 같이 비교 재생</button><div class="grid"><section><h3>기존 720p → 240p</h3><video controls playsinline preload="metadata" muted src="old-240.mp4"></video><img src="old-240.png" alt="기존 240p 16초 화면"></section><section><h3>큰 글자 1080p → 240p</h3><video controls playsinline preload="metadata" src="new-240.mp4"></video><img src="new-240.png" alt="개선 240p 16초 화면"></section></div><p>한 화면에 보여주는 정보량은 줄고, 비교 항목은 순서대로 나타납니다. 상세 제조사 출처: {html.escape(' / '.join(data['sources']))}</p><p>직접 착용 시험을 하지 않은 자료 기반 판단입니다. 연결된 가이드에는 제휴 광고가 포함되어 있습니다.</p></html>''')
    print(json.dumps(m,ensure_ascii=False))
if __name__=='__main__':main()
