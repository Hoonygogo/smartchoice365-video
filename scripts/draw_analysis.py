"""Evidence-led landscape editorial frames. Numerical graphics are deterministic."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

W,H=1280,720
NAVY='#13243a'; GOLD='#d9a84e'; INK='#1e314a'; MUTED='#58677b'; BG='#f5f3ee'


def draw_analysis(scene,index,total,caption,path,font,active=None):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    def f(size): return ImageFont.truetype(font,size)
    def text(s,x,y,size=26,color=INK): d.text((x,y),s,font=f(size),fill=color)
    def block(s,x,y,size=28,width=1140,color=INK,gap=10,limit=598):
        for para in s.split('\n'):
            line=''
            for c in para:
                if line and d.textlength(line+c,font=f(size))>width:
                    text(line,x,y,size,color); y+=size+gap;line=c
                else: line+=c
            text(line,x,y,size,color);y+=size+gap
        if y>limit: raise ValueError(f'Text overflow in scene {index}: {s}')
        return y
    def card(x,y,w,h,fill='#e5e9ed'):
        d.rounded_rectangle((x,y,x+w,y+h),18,fill=fill)
    def photo(mode,x=850,y=260,w=366,h=295):
        p=Image.open(Path(__file__).resolve().parents[1]/'assets/heattech-lifestyle.jpg')
        if mode in ('office','outside'):
            j=0 if mode=='office' else 2
            p=p.crop((j*p.width//3,0,(j+1)*p.width//3,p.height))
        p=ImageOps.fit(p,(w,h),method=Image.Resampling.LANCZOS,centering=(.5,.4))
        im.paste(p,(x,y))
        d.rectangle((x,y+h-30,x+w,y+h),fill=NAVY)
        text('이해를 돕기 위한 연출 이미지',x+12,y+h-27,15,'white')
    d.rectangle((0,0,W,65),fill=NAVY)
    text('SMART CHOICE 365',42,18,24,'white')
    text(f'BUYING GUIDE   {index:02}/{total:02}',966,20,19,'#ead1a0')
    text(scene['eyebrow'],48,88,21,'#8b6426')
    block(scene['heading'],48,130,43,width=1180,gap=9,limit=248)
    mode=scene['visual']
    if mode in ('hero','closing'):
        photo('all',750,275,480,275)
        block('생활환경\n소재와 관리\n입는 횟수',55,294,34,width=620,gap=19)
        block(scene['body'],55,513,23,width=650)
    elif mode=='temperature':
        left,right=375,1160
        for val in (-20,-10,0,10,20):
            x=left+(val+20)/40*(right-left)
            d.line((x,268,x,501),fill='#cbd1d8',width=1)
            text(f'{val}°C',x-18,508,19,MUTED)
        for j,(name,lo,hi,col) in enumerate([('일반',5,20,'#8b9eb3'),('코튼 엑스트라웜',-5,15,'#bc9851'),('울트라웜',-20,10,'#294764')]):
            y=285+j*74;text(name,54,y,26)
            a=left+(lo+20)/40*(right-left);b=left+(hi+20)/40*(right-left)
            d.rounded_rectangle((a,y+5,b,y+45),10,fill=col)
            text(f'{lo} ~ {hi}°C',a+12,y+9,22,'white')
        text('브랜드의 참고 구간입니다. 최저 안전기온이나 개인 체감 보장값이 아닙니다.',54,551,22,MUTED)
    elif mode=='warmth':
        for j,(name,v) in enumerate([('일반 소재',1),('코튼 엑스트라웜',1.5),('울트라웜',2.25)]):
            y=277+j*85;text(name,55,y+6,26)
            d.rounded_rectangle((325,y,325+v*280,y+50),10,fill=NAVY if j!=1 else '#92712e')
            text(f'{v:g}×',345+v*280,y+6,29)
        text('CLO 비교 · 기본 소재 = 1 / 제조사 시험 안내이며 자체 실측 아님',55,548,23,MUTED)
    elif mode=='cotton':
        card(48,276,560,260);card(632,276,600,260,NAVY)
        text('라인업 안내',75,300,22,MUTED);block('피부에 닿는 면\n100% 코튼',75,351,38,width=500)
        text('확인한 타이즈 BLACK 몸판 예시',660,300,22,'#e7d4aa')
        text('면 64%',660,351,45,'white')
        text('아크릴 28% + 폴리우레탄 8%',660,422,24,'white')
        text('전체 소재와 접촉면 설명은 서로 다른 정보',660,476,21,'#c8d4e3')
        text('색상·모델별 소재표 확인 / 모든 코튼 엑스트라웜에 같은 혼용률을 적용하지 않음',55,550,21,MUTED)
    elif mode=='laundry':
        for j,name in enumerate(('코튼 엑스트라웜 타이즈','울트라웜 타이즈')):
            x=48+j*600;card(x,285,572,226)
            text(name,x+24,308,28);text('세탁기  가능',x+24,366,33)
            text('건조기  사용 불가',x+24,425,33,'#8c472c')
        text('구매할 상품의 세탁표가 우선입니다. 다른 모델까지 같은 조건이라고 가정하지 마세요.',55,552,21,MUTED)
    elif mode=='office':
        photo('office')
        text('가상 하루 패턴',55,280,23,MUTED)
        d.rounded_rectangle((55,333,112,390),9,fill=GOLD)
        d.rounded_rectangle((112,333,798,390),9,fill=NAVY)
        text('통근 40분',55,411,27);text('난방 실내 8시간',400,411,29)
        text('우리의 출발점: 일반부터 비교',55,496,32)
        text('비율 막대는 위 예시의 시간 비율',55,550,20,MUTED)
    elif mode=='outside':
        photo('outside')
        for j,s in enumerate(('야외 체류가 긴가?','외투가 바람을 막아 주는가?','실내 이동은 얼마나 잦은가?')):
            text(f'{j+1:02}',55,285+j*73,31,'#9c732d');text(s,124,285+j*73,30)
        text('우리의 출발점: 울트라웜 검토 + 전체 옷 조합 확인',55,540,24)
    elif mode=='activity':
        for j,(a,b) in enumerate([('보온력','춥게 머무는 시간'),('활동량','움직임과 땀'),('환경 변화','실내로 들어간 뒤')]):
            x=48+j*400;card(x,286,376,220,NAVY if j==1 else '#e3e8ed')
            text(a,x+24,314,32,'white' if j==1 else INK)
            text(b,x+24,389,25,'white' if j==1 else INK)
        text('땀 배출 성능의 제품별 우열은 이번 비교에서 시험하지 않았습니다.',55,551,23,MUTED)
    elif mode=='cost':
        for j,(price,n,cost) in enumerate([('20,000원','40회','500원'),('30,000원','5회','6,000원')]):
            x=48+j*600;card(x,285,572,245,NAVY if j==0 else '#e3e8ed')
            color='white' if j==0 else INK
            text(f'{price} ÷ {n}',x+28,316,34,color)
            text(f'1회당 {cost}',x+28,393,43,'#e8c783' if j==0 else INK)
            text('설명용 가상 가격',x+28,475,20,color)
        block(scene['body'],55,551,21,width=1170)
    elif mode=='decision':
        for j,(name,env) in enumerate([('일반','난방 실내 중심 · 가볍게 겹쳐 입기'),('코튼 엑스트라웜','쌀쌀한 실내외 이동'),('울트라웜','추운 야외 체류가 긴 날')]):
            y=275+j*90;card(48,y,1184,77,NAVY if j==1 else '#e3e8ed')
            text(name,75,y+18,29,'#e7c986' if j==1 else INK)
            text(env,465,y+20,27,'white' if j==1 else INK)
        text('개인의 추위 민감도·활동량·외투에 따라 조정하세요.',55,556,22,MUTED)
    elif mode=='checklist':
        for j,(a,b) in enumerate([('제품명','코튼 / 캐시미어 블렌드'),('소재표','상의 / 타이즈 · 색상별'),('세탁표','건조기 사용 여부'),('입을 날','가장 오래 머무는 환경')]):
            x=48+(j%2)*602;y=275+(j//2)*137;card(x,y,580,118)
            text(a,x+23,y+15,30);text(b,x+23,y+64,25,MUTED)
    else: raise ValueError(f'Unknown scene layout {mode}')
    # Editorial focus follows a short visual beat, while chart geometry and captions stay fixed.
    if active is not None:
        boxes={
            'hero':[(44,289+k*53,670,343+k*53) for k in range(3)],
            'temperature':[(44,277+k*74,1235,345+k*74) for k in range(3)],
            'warmth':[(44,268+k*85,1228,335+k*85) for k in range(3)],
            'cotton':[(48,276,608,536),(632,276,1232,536)],
            'laundry':[(48,285,620,511),(648,285,1220,511)],
            'office':[(50,328,117,395),(112,328,803,395)],
            'outside':[(48,275+k*73,815,337+k*73) for k in range(3)],
            'activity':[(48+k*400,286,424+k*400,506) for k in range(3)],
            'cost':[(48,285,620,530),(648,285,1220,530)],
            'decision':[(48,275+k*90,1232,352+k*90) for k in range(3)],
            'checklist':[(48+(k%2)*602,275+(k//2)*137,628+(k%2)*602,393+(k//2)*137) for k in range(4)],
            'closing':[(44,289+k*53,670,343+k*53) for k in range(3)]
        }[mode]
        box=boxes[active%len(boxes)]
        d.rounded_rectangle(box,12,outline=GOLD,width=5)
    # Caption is one synthesized sentence, not a wall of the complete scene narration.
    d.rectangle((0,597,W,H),fill=NAVY)
    block(caption,48,610,25,width=1184,color='white',gap=8,limit=677)
    text(scene['source'],48,686,15,'#c4ceda')
    d.rectangle((0,715,int(W*index/total),719),fill=GOLD)
    im.save(path)
