"""Native 1080p editorial graphs with larger labels and restrained focus."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from render_readability import font_path

W,H=1920,1080
NAVY='#13243a'; GOLD='#d9a84e'; INK='#1e314a'; MUTED='#58677b'; BG='#f5f3ee'

def draw(scene,index,total,caption,active,path):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    def f(n):return ImageFont.truetype(font_path(),n)
    def text(s,x,y,size=50,color=INK):d.text((x,y),s,font=f(size),fill=color)
    def block(s,x,y,size=50,width=1760,lines=2,color=INK):
        result=[];line=''
        for c in s.replace('\n',' '):
            if line and d.textlength(line+c,font=f(size))>width:result.append(line.strip());line=c
            else:line+=c
        if line:result.append(line.strip())
        if len(result)>lines:raise ValueError('Text overflow: '+s)
        for n,line in enumerate(result):text(line,x,y+n*(size+12),size,color)
    def card(x,y,w,h,fill='#e5e9ed'):d.rounded_rectangle((x,y,x+w,y+h),24,fill=fill)
    targets=([active] if isinstance(active,int) else list(active or []))
    def focus_items(boxes):
        for target in targets:
            if isinstance(active,int):target=target%len(boxes)
            if not 0<=target<len(boxes):raise ValueError('Invalid highlight target')
            d.rounded_rectangle(boxes[target],20,outline=GOLD,width=7)
    def photo(mode,x,y,w,h):
        p=Image.open(Path(__file__).resolve().parents[1]/'assets/heattech-lifestyle.jpg')
        if mode!='all':
            j=0 if mode=='office' else 2;p=p.crop((j*p.width//3,0,(j+1)*p.width//3,p.height))
        p=ImageOps.fit(p,(w,h),method=Image.Resampling.LANCZOS,centering=(.5,.4));im.paste(p,(x,y))
        d.rectangle((x,y+h-54,x+w,y+h),fill=NAVY)
        text('이해를 돕기 위한 연출 이미지',x+12,y+h-48,28,'white')
    d.rectangle((0,0,W,96),fill=NAVY)
    text('SMART CHOICE 365',64,20,42,'white');text(f'BUYING GUIDE  {index:02}/{total:02}',1395,25,32,'#ead1a0')
    text(scene['eyebrow'],72,118,34,'#8b6426')
    block(scene['heading'],72,174,72,lines=2)
    mode=scene['visual'];note=''
    if mode=='hero':
        photo('all',1040,365,800,350)
        for j,s in enumerate(('생활환경','소재와 관리','입는 횟수')):
            text(s,88,365+j*110,66)
        focus_items([(70,355+j*110,975,455+j*110) for j in range(3)])
        note='공식 자료를 바탕으로 한 Smart Choice 365의 구매 판단'
    elif mode=='temperature':
        left,right=650,1770
        for v in (-20,-10,0,10,20):
            x=left+(v+20)/40*(right-left);d.line((x,350,x,700),fill='#cbd1d8',width=2);text(f'{v}°C',x-30,704,36,MUTED)
        rows=[('일반',5,20,'#7d92aa'),('코튼 엑스트라웜',-5,15,'#a58039'),('울트라웜',-20,10,'#294764')]
        for j,(name,lo,hi,color) in enumerate(rows):
            y=350+j*118;text(name,80,y+14,52)
            a=left+(lo+20)/40*(right-left);b=left+(hi+20)/40*(right-left)
            d.rounded_rectangle((a,y+8,b,y+90),16,fill=color)
            text(f'{lo} ~ {hi}°C',a+18,y+16,52,'white')
        focus_items([(66,346+j*118,1854,450+j*118) for j in range(3)])
        note='브랜드 참고 구간 · 개인 체감·최저 안전기온 보장 아님'
    elif mode=='warmth':
        for j,(name,v) in enumerate([('일반 소재',1),('코튼 엑스트라웜',1.5),('울트라웜',2.25)]):
            y=350+j*118;text(name,80,y+12,52)
            d.rounded_rectangle((650,y,650+v*420,y+82),16,fill=NAVY if j!=1 else '#92712e')
            text(f'{v:g}×',675+v*420,y+8,60)
        focus_items([(66,342+j*118,1854,442+j*118) for j in range(3)])
        note='기본 소재 대비 제조사 CLO 시험 · 체감 온도 배수 아님'
    elif mode=='cotton':
        card(72,355,850,348);card(948,355,900,348,NAVY)
        text('피부에 닿는 면',108,390,46,MUTED);text('코튼 100%',108,475,76)
        text('옷 전체 혼용률과 구분',108,605,42)
        text('확인한 BLACK 타이즈 몸판',980,390,40,'#e7d4aa');text('면 64%',980,475,80,'white')
        text('아크릴 28% + 폴리우레탄 8%',980,605,41,'white')
        focus_items([(72,355,922,703),(948,355,1848,703)]);note='모든 모델이 같은 혼용률은 아닙니다. 모델·색상별 확인'
    elif mode=='laundry':
        for j,name in enumerate(('코튼 엑스트라웜 타이즈','울트라웜 타이즈')):
            x=72+j*900;card(x,355,870,348);text(name,x+32,385,45)
            text('세탁기  가능',x+32,480,62);text('건조기  사용 불가',x+32,590,62,'#8c472c')
        focus_items([(72+j*900,355,942+j*900,703) for j in range(2)]);note='확인한 두 타이즈 기준 · 다른 모델은 개별 세탁표 확인'
    elif mode=='office':
        photo('office',1300,355,548,365)
        text('가상 하루 패턴',80,355,42,MUTED)
        d.rounded_rectangle((80,445,160,535),12,fill=GOLD);d.rounded_rectangle((160,445,1220,535),12,fill=NAVY)
        text('통근 40분',80,560,56);text('난방 실내 8시간',650,560,56)
        text('일반부터 비교',80,660,68)
        focus_items([(72,435,625,635),(630,435,1235,635),(72,650,1235,750)]);note='실내 8시간 + 통근 40분의 가상 예시 · 개인 체감 고려'
    elif mode=='outside':
        photo('outside',1300,355,548,365)
        for j,s in enumerate(('야외 체류 시간','방풍 외투','활동량과 땀')):text(f'{j+1:02}  {s}',80,365+j*116,62)
        focus_items([(66,355+j*116,1235,460+j*116) for j in range(3)]);note='울트라웜 검토 + 전체 옷 조합 · 보온·안전 한계 보장 아님'
    elif mode=='cost':
        for j,(price,n,v) in enumerate([('20,000원','40회','500원'),('30,000원','5회','6,000원')]):
            x=72+j*900;color='white' if j==0 else INK;card(x,355,870,350,NAVY if j==0 else '#e3e8ed')
            text(f'{price} ÷ {n}',x+30,390,61,color);text(f'1회당 {v}',x+30,500,76,'#e8c783' if j==0 else INK)
            text('설명용 가상 가격',x+30,625,42,color)
        focus((72+(active%2)*900,355,942+(active%2)*900,705));note='현재 히트텍 판매가격 아님 · 세탁·관리비 제외'
    elif mode=='decision':
        for j,(name,env) in enumerate([('일반','난방 실내 중심'),('코튼 엑스트라웜','쌀쌀한 실내외 이동'),('울트라웜','추운 야외 체류')]):
            y=350+j*122;card(72,y,1776,106,NAVY if j==1 else '#e3e8ed')
            text(name,108,y+18,54,'#e7c986' if j==1 else INK);text(env,850,y+18,54,'white' if j==1 else INK)
        focus_items([(72,350+j*122,1848,456+j*122) for j in range(3)]);note='자료 기반 편집 추천 · 개인 체감·활동량·외투에 따라 조정'
    else:raise ValueError('Unsupported scene '+mode)
    text(note,76,764,38,MUTED)
    d.rectangle((0,830,W,H),fill=NAVY)
    block(caption,72,846,52,lines=3,color='white')
    text('공식 자료 · 상세 출처는 설명란 | 직접 착용시험 아님',72,1030,30,'#c4ceda')
    d.rectangle((0,1072,int(W*index/total),1079),fill=GOLD)
    im.save(path)
