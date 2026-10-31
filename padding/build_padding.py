import sys,os,json,math,hashlib,subprocess,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw,ImageFont,ImageOps
from supertonic import TTS
ROOT=Path(__file__).resolve().parent; OUT=ROOT/'output';OUT.mkdir(exist_ok=True)
FONT=str(ROOT/'NotoSansCJK-Regular.ttc'); FPS=24
S=[]
def scene(title,kind,photo,rows,cues,note='공식 자료 기반 편집 판단 · 직접 착용시험 아님'):
 S.append(dict(title=title,kind=kind,photo=photo,rows=rows,cues=[dict(text=t,target=k) for t,k in cues],note=note))
scene('패딩, 비싸면 더 따뜻할까요?','intro',None,[],[('안녕하세요, 스마트 초이스 삼육오입니다.',-1),('오늘은 패딩을 사기 전에 확인할 다섯 가지를 살펴보겠습니다.',-1),('도움 되는 구매 비교를 계속 보시려면 구독도 부탁드립니다.',-1)])
scene('화면이 흐리게 보이나요?','quality',None,['설정','화질 · 고급','1080p'],[('화면이 흐리게 보이면 설정에서 화질을 높여 주세요.',0),('휴대폰에서는 화질, 고급에서 천팔십 피를 선택할 수 있습니다. 기기에 따라 메뉴는 다를 수 있습니다.',2)])
scene('가격표보다, 입는 환경부터','photo',1,['실내 이동이 많은가요?','밖에서 오래 기다리나요?','매일 입을 옷인가요?'],[('결론부터 말씀드리면, 비싼 패딩이 내 생활에도 가장 좋은 패딩인 것은 아닙니다.',-1),('실내 이동이 많은지, 밖에서 오래 기다리는지부터 나누세요.',0),('스마트 초이스는 브랜드보다 실제로 입는 환경을 먼저 보겠습니다.',-1)])
scene('① 필파워는 보온 점수가 아닙니다','photo',2,['필파워 = 다운의 부풀음','높을수록 무게 대비 효율','옷 전체의 따뜻함과 구분'],[('첫째는 필파워입니다. 다운이 얼마나 잘 부풀어 오르는지를 나타내는 지표입니다.',0),('높은 필파워는 가벼운 무게로 공기를 가두는 데 유리할 수 있습니다.',1),('하지만 숫자가 높다고 옷 전체가 무조건 더 따뜻한 것은 아닙니다.',2)],'Patagonia · Norrøna 설명 참고 | 이미지 속 다운은 성능시험 아님')
scene('② 충전량과 혼용률은 다른 정보','photo',3,['충전량: 들어간 다운의 무게','혼용률: 솜털·깃털의 비율','같은 사이즈 기준으로 확인'],[('둘째는 충전량입니다. 다운이 실제로 얼마나 들어 있는지도 함께 확인하세요.',0),('솜털과 깃털의 비율은 충전량과 다른 정보입니다. 비율만 보고 다운의 양을 알 수는 없습니다.',1),('충전량이 공개돼 있다면 같은 사이즈 기준인지 확인하고, 없으면 판매처에 물어보세요.',2)])
scene('③ 숏패딩과 롱패딩, 길이의 선택','photo',4,['짧은 길이: 이동 편의 확인','긴 길이: 하체를 덮는 범위','앉기 · 계단 · 지퍼 직접 확인'],[('셋째는 길이와 움직임입니다. 짧은 패딩은 앉거나 이동할 때 편한지 보세요.',0),('롱패딩은 하체를 덮는 범위가 넓지만, 길이만으로 전체 보온 성능을 단정할 수는 없습니다.',1),('가능하면 앉아 보고 계단을 오르는 동작도 해보세요. 이중 지퍼가 필요한지도 확인하세요.',2)])
scene('④ 바람과 물, 겉감도 확인하세요','photo',5,['목 · 소매 · 밑단의 여밈','발수와 방수는 같은 말 아님','비가 잦다면 합성 충전재도 비교'],[('넷째는 겉감과 여밈입니다. 목과 소매, 밑단이 어떻게 닫히는지 확인하세요.',0),('발수라는 말만 보고 비를 계속 막아 주는 방수 옷이라고 생각하지 마세요.',1),('다운은 젖으면 보온력이 떨어질 수 있습니다. 비가 잦은 환경이라면 합성 충전재도 비교할 만합니다.',2)],'Patagonia 다운·합성 충전재 설명 참고 · 모델별 방수 사양 확인')
scene('⑤ 출퇴근용은, 하루 전체로 판단','photo',6,['가상 예시: 짧은 통근','난방 실내에 오래 머무름','무게 · 벗어서 들기 · 부피'],[('다섯째는 하루의 생활 패턴입니다. 예를 들어 짧게 통근하고 난방된 실내에 오래 머문다면,',0),('최대한 두꺼운 옷보다 입고 벗기 편한 조합을 우선 비교하겠습니다.',1),('이것은 우리의 편집 판단입니다. 무게와 벗어서 들고 다닐 때의 부피까지 생각해 보세요.',2)],'Smart Choice 365 편집 판단 · 가상의 생활패턴 예시')
scene('야외에 오래 있다면, 확인 순서도 달라집니다','photo',7,['야외 대기 시간부터 확인','충전량 · 길이 · 여밈 함께','안에 입을 옷까지 여유 있게'],[('반대로 야외에서 오래 기다리는 분은, 가벼움 하나보다 보온 구성 전체를 먼저 보겠습니다.',0),('충전량과 길이, 목과 소매의 여밈을 함께 확인하세요.',1),('안에 입을 옷을 고려해 입어 보고, 움직일 때 불편하지 않은지도 살펴보세요.',2)],'Smart Choice 365 편집 판단 · 특정 최저기온 보장 아님')
scene('세탁표와 관리비까지 보세요','photo',8,['모델별 세탁표 우선','건조기 가능 여부 따로 확인','보관 · 건조에 드는 수고도 비용'],[('마지막으로 세탁표를 확인하세요. 모든 패딩을 같은 방법으로 세탁하고 말릴 수 있는 것은 아닙니다.',0),('건조기 사용 가능 여부는 해당 제품의 표시를 따르세요.',1),('구입 가격뿐 아니라, 관리와 보관에 드는 수고까지 감당할 수 있는 옷을 고르는 것이 좋겠습니다.',2)])
scene('비싼 옷보다, 자주 입는 옷의 가치','cost',None,['20만원 ÷ 100회 = 2,000원','40만원 ÷ 20회 = 20,000원','가상 가격 · 1회당 구입비'],[('가격은 입는 횟수로도 생각해 볼 수 있습니다. 지금부터는 실제 판매가가 아닌 가상 예시입니다.',-1),('이십만 원짜리를 백 번 입으면, 한 번당 구입비는 이천 원입니다.',0),('사십만 원짜리를 스무 번 입으면, 한 번당 이만 원입니다.',1),('물론 관리비는 제외한 계산입니다. 저렴하다는 이유보다 자주 입을 수 있는지를 보세요.',2)],'설명용 가상 계산 · 실제 판매가격 아님 · 관리비 제외')
scene('스마트초이스의 선택 기준','verdict',None,['필파워 + 충전량 함께 보기','길이 + 겉감 + 생활패턴','세탁표와 착용감 확인 후 결정'],[('정리하겠습니다. 필파워와 충전량을 함께 보고,',0),('길이와 겉감은 내 생활 패턴에 맞추세요.',1),('마지막으로 세탁표와 실제 착용감을 확인하세요. 가격표보다 내가 잘 입을 옷인지가 먼저입니다.',2),('도움이 되셨다면 구독해 주세요. 다음 구매 비교도 스마트 초이스 삼육오와 함께하세요.',-1)])

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
 d.rectangle((0,0,1920,92),fill=navy);txt('SMART CHOICE 365',64,17,40,'white');txt('패딩 구매가이드',1510,23,32,'#ead1a0')
 if s['kind']=='intro':
  logo=Image.open(ROOT.parent/'assets/smartchoice365-brand-logo-v1.png').convert('RGBA');logo.thumbnail((1540,470));im.paste(logo,((1920-logo.width)//2,130),logo)
  txt('패딩, 비싸면 더 따뜻할까요?',330,585,72);txt('사기 전에 확인할 5가지',550,690,56);txt('smartchoice365-web.pages.dev',600,783,38)
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
 sf.write(OUT/'voice.wav',np.concatenate(audio),rate);(OUT/'timings.json').write_text(json.dumps(timings,ensure_ascii=False,indent=2));(OUT/'script.json').write_text(json.dumps(S,ensure_ascii=False,indent=2))
 clips=[]
 for n,t in enumerate(timings):
  png=OUT/f'frame_{n:02}.png';draw(t['scene'],t['cue'],png);mp4=OUT/f'clip_{n:02}.mp4'
  if not mp4.exists():subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-loop','1','-framerate',str(FPS),'-i',str(png),'-frames:v',str(t['frames']),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',str(mp4)],check=True)
  clips.append(mp4);print('FRAME',n,flush=True)
 (OUT/'concat.txt').write_text(''.join(f"file '{p}'\n" for p in clips))
 final=OUT/'SmartChoice365_Padding_Korean_v1.mp4';subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-f','concat','-safe','0','-i',str(OUT/'concat.txt'),'-i',str(OUT/'voice.wav'),'-c:v','copy','-c:a','aac','-b:a','128k','-movflags','+faststart',str(final)],check=True)
 def ts(t):return f'{int(t//3600):02}:{int(t//60)%60:02}:{int(t)%60:02},{round(t%1*1000):03}'
 (OUT/'captions.srt').write_text('\n\n'.join(f'{n+1}\n{ts(t["start"])} --> {ts(t["end"])}\n{t["text"]}' for n,t in enumerate(timings)))
 m=dict(title='패딩, 비싸면 더 따뜻할까? 사기 전에 확인할 5가지',duration=frame/FPS,voice='Sarah F1',speed=1.1,steps=8,status='awaiting_approval',published=False,sha256=hashlib.sha256(final.read_bytes()).hexdigest(),sources=['https://www.patagonia.com/stories/guides/product/down-fill-power-explained/story-166881.html','https://www.norrona.com/gb/en/knowledge/why-down','https://www.patagonia.com/stories/guides/product/natural-down-vs-synthetic-down-insulation-warmth-comes-standard/story-175856.html'],disclosure='독립적으로 생성한 연출 이미지와 공식 자료를 바탕으로 한 구매가이드. 직접 착용시험이나 특정 브랜드의 공식 제품 사진이 아닙니다. 가상 가격 계산은 실제 판매가격이 아닙니다.')
 (OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));print(json.dumps(m,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
