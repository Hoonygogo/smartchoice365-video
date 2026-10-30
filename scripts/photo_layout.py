"""Place the complete selected source image; labels never cover the model."""
from PIL import Image, ImageDraw, ImageFont, ImageOps

def place_full_photo(canvas, source, box, font_path, label_size=28, label_height=54):
    x,y,w,h=box
    if w<=0 or h<=label_height:raise ValueError('Photo box too small')
    if x<0 or y<0 or x+w>canvas.width or y+h>canvas.height:
        raise ValueError('Photo outside canvas')
    # Aspect-preserving contain; empty space is intentional. Never cover/fit.
    source=ImageOps.exif_transpose(source).convert('RGB')
    photo=ImageOps.contain(source,(w,h-label_height),Image.Resampling.LANCZOS)
    px=x+(w-photo.width)//2;py=y+(h-label_height-photo.height)//2
    d=ImageDraw.Draw(canvas)
    d.rectangle((x,y,x+w-1,y+h-1),fill='#e5e9ed')
    canvas.paste(photo,(px,py))
    label_top=y+h-label_height
    assert py+photo.height<=label_top
    d.rectangle((x,label_top,x+w-1,y+h-1),fill='#13243a')
    font=ImageFont.truetype(font_path,label_size)
    label='이해를 돕기 위한 연출 이미지'
    if d.textlength(label,font=font)>w-20:raise ValueError('Photo disclosure too wide')
    d.text((x+10,label_top+(label_height-label_size)//2-3),label,font=font,fill='white')
    return (px,py,px+photo.width,py+photo.height)
