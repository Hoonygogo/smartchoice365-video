"""Guard against the observed regression: portrait models cropped by wide boxes."""
from pathlib import Path
from PIL import Image, ImageDraw
from photo_layout import place_full_photo
from render_readability import font_path

for size in [(512,1024),(1536,1024),(1024,256)]:
    source=Image.new('RGB',size,'white');d=ImageDraw.Draw(source)
    colors=['red','green','blue','yellow'];sw,sh=size
    corners=[(0,0,sw//5,sh//5),(4*sw//5,0,sw-1,sh//5),
             (0,4*sh//5,sw//5,sh-1),(4*sw//5,4*sh//5,sw-1,sh-1)]
    for color,box in zip(colors,corners):d.rectangle(box,fill=color)
    canvas=Image.new('RGB',(900,600),'black')
    x0,y0,x1,y1=place_full_photo(canvas,source,(60,70,720,430),font_path())
    # Every source corner must survive, including bottom corners above the label.
    points=[(x0+2,y0+2),(x1-3,y0+2),(x0+2,y1-3),(x1-3,y1-3)]
    from PIL import ImageColor
    assert [canvas.getpixel(p) for p in points]==[ImageColor.getrgb(c) for c in colors]
    assert y1<=70+430-54
for name in ['draw_graph_hd.py','draw_analysis.py','draw_editorial.py']:
    assert 'ImageOps.fit(' not in Path(__file__).with_name(name).read_text()
print('Full source corners preserved for portrait, group and panorama; labels separated')
