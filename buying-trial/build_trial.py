import sys,os,json,math,hashlib,subprocess,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw,ImageFont,ImageOps
from supertonic import TTS
ROOT=Path(__file__).resolve().parent; OUT=ROOT/'output';OUT.mkdir(exist_ok=True)
FONT=str(ROOT/'NotoSansCJK-Regular.ttc'); FPS=24
S=[]
def scene(title,kind,photo,rows,cues,note='가상의 생활 사례 · Smart Choice 365 편집 판단'):
 S.append(dict(title=title,kind=kind,photo=photo,rows=rows,cues=[dict(text=t,target=k) for t,k in cues],note=note))
scene('두 칸이면, 편리함도 두 배일까?','photo',1,['구매욕: 두 칸이면 편하겠지!','현실: 씻는 건 누가 하는데?','오늘의 안건: 에어프라이어'],[('서랍이 두 개면, 저녁 준비도 두 배로 편해질까요?',0),('잠깐. 씻을 때도 그 생각일까요?',1),('스마트초이스 구매재판, 지금 시작합니다.',2)])
scene('스마트초이스 구매재판','intro',None,[],[('안녕하세요, 스마트 초이스 삼육오입니다.',-1),('오늘의 안건은 에어프라이어 두 서랍, 우리 집에도 필요한가입니다.',-1)])
scene('화면이 흐리게 보이나요?','quality',None,['설정','화질 · 고급','1080p'],[('화면이 흐리게 보이면 설정을 열어 주세요.',0),('화질 메뉴에서 고급을 선택하고,',1),('천팔십 피로 높여 주세요. 기기에 따라 메뉴는 다를 수 있습니다.',2),('재미있는 구매 비교가 필요하다면 구독도 부탁드립니다.',-1)])
scene('주장: 두 개면 무조건 편하잖아?','photo',2,['구매욕: 한 번에 두 가지!','질문: 평소에도 두 가지 굽나요?','제품보다 식사 습관부터'],[('구매 희망자의 주장입니다. 두 칸이면 한 번에 두 가지를 만들 수 있잖아요?',0),('좋습니다. 그런데 평소에도 두 가지 음식을 따로 굽나요?',1),('이 재판의 증거는 광고 문구가 아니라, 우리 집 저녁 메뉴입니다.',2)])
scene('증인 A: 오늘도 한 가지만 데웠다','photo',3,['어제: 남은 피자','오늘: 감자 한 접시','가상 사례: 한 메뉴 중심'],[('가상의 첫 번째 집을 보겠습니다. 어제는 남은 피자, 오늘은 감자 한 접시.',0),('이렇게 대부분 한 가지를 데운다면, 두 번째 서랍은 출근할 일이 적을 수 있겠죠.',1),('이 경우에는 필요한 음식이 잘 들어가는 단일 서랍부터 비교하겠습니다.',2)])
scene('증인 B: 메인과 사이드를 같이!','photo',4,['한쪽은 치킨, 한쪽은 채소','서로 다른 설정이 필요할 때','기능은 정확한 모델별 확인'],[('반대로 고기와 채소를 자주 함께 준비하는 집이라면 이야기가 달라집니다.',0),('두 구역의 시간과 온도를 따로 설정할 수 있는 모델은 이런 조합에 도움이 될 수 있습니다.',1),('다만 모든 제품의 기능이 같지는 않으니, 정확한 모델의 안내를 확인하세요.',2)])
scene('반전: 큰 통 하나가 아닙니다','photo',5,['분리된 두 바구니','합계 용량과 한 칸 크기는 다름','자주 굽는 음식이 들어가나요?'],[('여기서 반전입니다. 바구니가 분리된 모델의 합계 용량은, 하나의 큰 조리 공간이 아닙니다.',0),('전체 숫자가 커도 내가 자주 굽는 음식이 한 칸에 들어가는지는 별개의 문제죠.',1),('큰 용량이라는 말보다 각 바구니의 실제 크기부터 확인하세요.',2)],'분리 바구니형 기준 · 칸막이 제거형 등 다른 구조는 별도 확인')
scene('이의 있습니다! 설거지 담당입니다','photo',6,['사용한 바구니는 세척도 필요','세척 안내는 모델별 확인','관리할 사람도 구매 회의에!'],[('이의 있습니다. 설거지 담당입니다!',0),('두 서랍을 활용하면 사용한 바구니의 세척도 생각해야 합니다. 세척 방법은 제품 안내를 따르세요.',1),('설거지가 무조건 두 배라는 뜻은 아닙니다. 다만 관리할 사람도 구매 회의에 참여시켜 주세요.',2)])
scene('추가 증거: 우리 집 주방 공간','photo',7,['본체 폭과 깊이 확인','제조사 권장 여유 공간 확인','놓을 자리까지 계산했나요?'],[('구매 직전에는 주방도 증인으로 불러야 합니다. 본체의 폭과 깊이를 확인하세요.',0),('제조사가 안내하는 설치 여유 공간도 필요합니다.',1),('물건은 마음에 드는데 놓을 곳이 없다면, 그건 아직 구매 준비가 덜 된 겁니다.',2)])
scene('판결 전에, 우리 집 저녁을 복기!','photo',8,['가족 수만으로 결정하지 않기','동시에 굽는 메뉴가 핵심','최근 다섯 번의 저녁을 생각'],[('가족 수만으로 판결하지 않겠습니다. 중요한 것은 동시에 굽는 메뉴입니다.',0),('두 사람이 살아도 두 메뉴를 자주 만들 수 있고, 여러 명이 살아도 한 종류만 구울 수 있죠.',1),('이제 여러분 차례입니다. 최근 다섯 번의 저녁을 떠올려 보세요.',2)])
scene('배심원 질문: 두 칸이 몇 번 필요했나요?','test',None,['0~1번: 단일 서랍부터','2~3번: 가격·공간까지 비교','4~5번: 두 서랍의 활용도 검토'],[('그중 두 음식을 따로 굽는 일이 몇 번 있었나요? 잠깐 멈추고 세어보셔도 좋습니다.',-1),('영 번에서 한 번 정도라면, 단일 서랍부터 비교하겠습니다.',0),('두 번에서 세 번이라면, 추가 가격과 주방 공간까지 따져보세요.',1),('네 번에서 다섯 번이라면, 두 서랍을 활용할 기회가 많을 수 있습니다.',2)],'스마트초이스의 편집용 자가 점검 · 과학적 성능 점수나 절약 보장 아님')
scene('최종 판결: 생활에 맞으면 조건부 허가!','verdict',None,['한 메뉴 위주 → 단일 서랍부터','두 메뉴 자주 → 두 서랍 검토','결정 기준은 내가 실제로 쓸 기능'],[('최종 판결입니다. 한 메뉴 위주라면 단일 서랍부터 비교하세요.',0),('두 메뉴를 자주 함께 만든다면 두 서랍을 검토하세요.',1),('가장 큰 제품보다, 내가 실제로 쓸 기능에 돈을 쓰는 것이 스마트초이스의 판단입니다.',2),('여러분은 다섯 번 중 몇 번이었나요? 댓글로 알려주세요. 다음 구매재판도 보고 싶다면 구독해 주세요.',-1)])

def font(n):return ImageFont.truetype(FONT,n)
def draw(si,ci,path):
 s=S[si];cue=s['cues'][ci];im=Image.new('RGB',(1920,1080),'#f5f3ee');d=ImageDraw.Draw(im);navy='#13243a';gold='#d9a84e'
 def txt(t,x,y,n=46,c=navy):d.text((x,y),t,font=font(n),fill=c)
 def wrap(t,x,y,n,width,c=navy,maxlines=3):
  lines=[];line=''
  for word in t.split():
   candidate=(line+' '+word).strip()
   if line and d.textlength(candidate,font=font(n))>width:lines.append(line);line=word
   else:line=candidate
  if line:lines.append(line)
  assert len(lines)<=maxlines,(t,lines)
  for j,l in enumerate(lines):txt(l,x,y+j*(n+12),n,c)
 def focus(box,k):
  if cue['target']==k:d.rounded_rectangle(box,18,outline=gold,width=7)
 d.rectangle((0,0,1920,92),fill=navy);txt('SMART CHOICE 365',64,17,40,'white');txt('구매재판 EP.01',1510,23,32,'#ead1a0')
 if s['kind']=='intro':
  logo=Image.open(ROOT.parent/'assets/smartchoice365-brand-logo-v1.png').convert('RGBA');logo.thumbnail((1540,470));im.paste(logo,((1920-logo.width)//2,130),logo)
  txt('에어프라이어, 두 서랍 필요할까?',330,585,72);txt('오늘의 증거: 우리 집 저녁 메뉴',550,690,56);txt('smartchoice365-web.pages.dev',600,783,38)
 elif s['kind']=='quality':
  txt(s['title'],85,150,72)
  for j,label in enumerate(s['rows']):
   x=85+j*620;box=(x,330,x+510,690);d.rounded_rectangle(box,25,fill=navy if j==2 else 'white');focus(box,j)
   
   if j==0:
    cx=x+230;cy=440
    for a in range(8):
     v=a*math.pi/4;d.line((cx+40*math.cos(v),cy+40*math.sin(v),cx+65*math.cos(v),cy+65*math.sin(v)),fill=navy,width=18)
    d.ellipse((cx-47,cy-47,cx+47,cy+47),fill=navy);d.ellipse((cx-20,cy-20,cx+20,cy+20),fill='white')
   else:txt(['','HD','1080p'][j],x+100,380,80,gold)
   txt(label,x+50,555,52,'white' if j==2 else navy)
   if j<2:txt('→',x+530,460,68,gold)
  txt('기기에 따라 메뉴가 다를 수 있습니다 · 설정 방법을 설명한 그림',85,760,34)
 else:
  wrap(s['title'],65,120,62,1790,maxlines=2)
  if s['kind']=='photo':
   p=Image.open(ROOT/'assets'/f'{s["photo"]}.png').convert('RGB');p=ImageOps.contain(p,(1060,540),Image.Resampling.LANCZOS);im.paste(p,(55+(1060-p.width)//2,235+(540-p.height)//2))
   txt('이해를 돕기 위한 연출 이미지',70,797,26,'#58677b')
   for j,row in enumerate(s['rows']):
    y=285+j*155;focus((1160,y-15,1860,y+122),j);txt(f'0{j+1}',1190,y,33,'#8b6426');wrap(row,1190,y+45,41,620,maxlines=2)
  elif s['kind']=='test':
   txt('최근 다섯 번의 저녁을 떠올려 보세요',90,235,49)
   for j in range(5):
    x=95+j*350;d.rounded_rectangle((x,325,x+300,425),20,fill=navy);txt(f'저녁 {j+1}',x+55,343,49,'white')
   for j,row in enumerate(s['rows']):
    y=480+j*100;d.rounded_rectangle((80,y,1840,y+88),18,fill='#e2e7ec');txt(row,120,y+10,47);focus((80,y,1840,y+88),j)
  elif s['kind']=='cost':
   for j,(p,n,amt) in enumerate([(200000,100,2000),(400000,20,20000)]):
    x=70+j*915;d.rounded_rectangle((x,290,x+870,690),24,fill=navy if j==0 else '#e2e7ec');col='white' if j==0 else navy
    txt(f'{p:,}원 ÷ {n}회',x+35,335,56,col);txt(f'1회당 {amt:,}원',x+35,470,68,gold if j==0 else navy);txt('실제 판매가가 아닌 가상 예시',x+35,610,33,col);focus((x,290,x+870,690),j)
   txt('구입비 ÷ 입는 횟수 · 관리비 제외',80,745,42);focus((65,730,1850,810),2)
  else:
   for j,row in enumerate(s['rows']):
    y=270+j*150;d.rounded_rectangle((80,y,1840,y+125),20,fill='#e2e7ec');txt(f'0{j+1}',120,y+25,52,'#8b6426');txt(row,270,y+25,52);focus((80,y,1840,y+125),j)
  
  if s['kind']=='verdict':
   logo=Image.open(ROOT.parent/'assets/smartchoice365-brand-logo-v1.png').convert('RGBA');logo.thumbnail((550,90));im.paste(logo,(1240,735),logo)
  txt(s['note'],70,832,26,'#58677b')
 d.rectangle((0,875,1920,1080),fill=navy);wrap(cue['text'],70,889,46,1780,'white',3)
 d.rectangle((0,1071,int(1920*(si+1)/len(S)),1079),fill=gold);im.save(path)

def main():
 os.environ['SC365_FONT']=FONT
 # Narration is generated and audited before any video assembly.
 engine=TTS(model='supertonic-3',model_dir=str(ROOT.parent/'.models/supertonic-3'),auto_download=False,intra_op_num_threads=2,inter_op_num_threads=1);style=engine.get_voice_style(voice_name='F1');rate=engine.sample_rate
 audio=[];timings=[];frame=0
 for si,s in enumerate(S):
  for ci,c in enumerate(s['cues']):
   wav=ROOT/f'audio_{si}_{ci}.wav'
   if wav.exists():raw,sr=sf.read(wav,dtype='float32');assert sr==rate
   else:
    raw,_=engine.synthesize(c['text'],voice_style=style,total_steps=8,speed=1.1,lang='ko');raw=np.asarray(raw).reshape(-1);sf.write(wav,raw,rate)
   rms=float(np.sqrt(np.mean(raw**2)));assert rms>.008 and np.isfinite(raw).all(),(si,ci,rms)
   frames=math.ceil((len(raw)/rate+.12)*FPS);samples=round(frames/FPS*rate);audio.append(np.pad(raw,(0,samples-len(raw))));timings.append(dict(scene=si,cue=ci,start=frame/FPS,end=(frame+frames)/FPS,frames=frames,text=c['text'],target=c['target'],rms=rms));frame+=frames
   print('VOICE',si,ci,round(len(raw)/rate,2),flush=True)
 combined=np.concatenate(audio)
 # Original quiet gavel cue on the verdict transition; no stock music or extra voice.
 verdict=next(t['start'] for t in timings if t['scene']==11)
 rng=np.random.default_rng(365)
 for delay in [0,.16]:
  start=round((verdict+delay)*rate);length=round(.07*rate);tone=(rng.normal(0,1,length)*np.exp(-np.linspace(0,8,length))*.012).astype(np.float32)
  combined[start:start+length]+=tone[:max(0,min(length,len(combined)-start))]
 sf.write(OUT/'voice.wav',combined,rate);(OUT/'timings.json').write_text(json.dumps(timings,ensure_ascii=False,indent=2));(OUT/'script.json').write_text(json.dumps(S,ensure_ascii=False,indent=2))
 clips=[]
 for n,t in enumerate(timings):
  png=OUT/f'frame_{n:02}.png';draw(t['scene'],t['cue'],png);mp4=OUT/f'clip_{n:02}.mp4'
  if not mp4.exists():subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-loop','1','-framerate',str(FPS),'-i',str(png),'-frames:v',str(t['frames']),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',str(mp4)],check=True)
  clips.append(mp4);print('FRAME',n,flush=True)
 (OUT/'concat.txt').write_text(''.join(f"file '{p}'\n" for p in clips))
 final=OUT/'SmartChoice365_BuyingTrial_AirFryer_Korean_v1.mp4';subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-f','concat','-safe','0','-i',str(OUT/'concat.txt'),'-i',str(OUT/'voice.wav'),'-c:v','copy','-c:a','aac','-b:a','128k','-movflags','+faststart',str(final)],check=True)
 def ts(t):return f'{int(t//3600):02}:{int(t//60)%60:02}:{int(t)%60:02},{round(t%1*1000):03}'
 (OUT/'captions.srt').write_text('\n\n'.join(f'{n+1}\n{ts(t["start"])} --> {ts(t["end"])}\n{t["text"]}' for n,t in enumerate(timings)))
 m=dict(title='에어프라이어 서랍 2개, 결국 하나만 쓰게 될까? | 스마트초이스 구매재판',duration=frame/FPS,voice='Sarah F1',speed=1.1,steps=8,status='awaiting_approval',published=False,sha256=hashlib.sha256(final.read_bytes()).hexdigest(),sources=['https://sharkninja.com.au/products/ninja-foodi-max-xxxl-dual-zone-air-fryer-af400'],disclosure='가상의 구매 토론과 생활 사례. 모든 인물·제품 장면은 연출 이미지이며 특정 모델의 공식 사진이나 실물 시험이 아닙니다. 최근 다섯 번의 저녁 분류는 편집용 자가 점검이며 과학적 성능 점수가 아닙니다.')
 (OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));print(json.dumps(m,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
