"""Branded editorial layouts; lifestyle image is explicitly illustrative."""
from pathlib import Path
from photo_layout import place_full_photo
from PIL import Image, ImageDraw, ImageFont, ImageOps


def draw_editorial(scene, index, total, path, font):
    im=Image.new('RGB',(720,1280),'#f5f3ee'); d=ImageDraw.Draw(im)
    navy='#12243b'; gold='#e9bd65'
    def put(text,xy,size=30,color=navy):
        d.text(xy,text,font=ImageFont.truetype(font,size),fill=color)
    def block(text,y,size=38,width=600,color=navy,gap=12):
        f=ImageFont.truetype(font,size)
        for para in text.split('\n'):
            line=''
            for c in para:
                if line and d.textlength(line+c,font=f)>width:
                    put(line,(60,y),size,color); y+=size+gap; line=c
                else: line+=c
            put(line,(60,y),size,color); y+=size+gap
        return y
    d.rectangle((0,0,720,125),fill=navy)
    put('SMART CHOICE 365',(48,43),26,'#ffffff')
    put(f'{index:02} / {total:02}',(574,48),20,gold)
    put(scene['eyebrow'],(60,161),21,'#7a5a24')
    block(scene['heading'],215,49,gap=12)
    mode=scene.get('visual','all')
    image=Image.open(Path(__file__).resolve().parents[1]/'assets/heattech-lifestyle.jpg')
    if mode=='table':
        rows=[('일반','실내 · 가벼운 겹쳐 입기'),('코튼 엑스트라웜','쌀쌀한 실내외 이동'),('울트라웜','추운 야외에 오래 있을 때')]
        for j,(name,desc) in enumerate(rows):
            y=420+j*144
            d.rounded_rectangle((48,y,672,y+126),18,fill=navy if j==1 else '#e3e7eb')
            put(name,(70,y+20),30,gold if j==1 else navy)
            put(desc,(70,y+70),25,'white' if j==1 else '#40516a')
    else:
        if mode in ('office','commute','cold'):
            j=('office','commute','cold').index(mode)
            w=image.width//3; image=image.crop((j*w,0,(j+1)*w,image.height))
        place_full_photo(im,image,(48,385,624,445),font,label_size=17,label_height=32)
    block(scene['body'],861,28,gap=10)
    d.rounded_rectangle((42,1005,678,1196),20,fill=navy)
    end=block(scene['narration'],1030,25,width=600,color='white',gap=10)
    if end>1192: raise ValueError(f'Caption overflow in scene {index}')
    put('공식 자료 기반 비교 · 직접 착용 시험 아님',(50,1222),17,'#526074')
    im.save(path)
