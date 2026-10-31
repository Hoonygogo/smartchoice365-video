"""Shared native-HD visual layout engine for Korean and Australian-English videos.
Source of truth for full-subject contain, native captions and target-specific focus.
Do not use a contact sheet or typography slide as photo input.
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps

W,H=1920,1080

def place_full(canvas, source, rect):
    """Place the entire image, retaining original aspect and all edges."""
    x0,y0,x1,y1=map(int,rect)
    if x0<0 or y0<0 or x1>canvas.width or y1>canvas.height or x0>=x1 or y0>=y1:
        raise ValueError('visual out of bounds')
    if isinstance(source,str):source=Image.open(source)
    source=ImageOps.exif_transpose(source).convert('RGBA')
    image=ImageOps.contain(source,(x1-x0,y1-y0),Image.Resampling.LANCZOS)
    x=x0+(x1-x0-image.width)//2;y=y0+(y1-y0-image.height)//2
    canvas.paste(image,(x,y),image)
    return x,y,x+image.width,y+image.height

def focus_on_regions(canvas,regions,targets,colour='#d9a84e'):
    """Focus exact narration cue targets; coordinates are image content bounds."""
    d=ImageDraw.Draw(canvas)
    for target in targets:
        if target not in regions:raise ValueError('Unmapped spoken target '+str(target))
        x0,y0,x1,y1=regions[target]
        if not(0<=x0<x1<=canvas.width and 0<=y0<y1<=canvas.height):
            raise ValueError('Invalid visual focus bounds')
        pad=10
        d.rounded_rectangle((max(0,x0-pad),max(0,y0-pad),min(canvas.width-1,x1+pad),min(canvas.height-1,y1+pad)),radius=18,outline=colour,width=7)

def validate_original_scene(asset):
    """Fail closed instead of recycling collage or invented approval flags."""
    if asset.get('source_kind') not in ('single_full_frame_photo','single_full_frame_illustration','original_native_graph'):
        raise ValueError('Image-first gate: not a standalone full scene')
    if asset.get('contact_sheet') or asset.get('baked_in_storyboard_labels'):
        raise ValueError('Storyboard/contact sheet or labels forbidden')
    if not asset.get('visual_review_passed'):
        raise ValueError('Needs actual visual review, not only an existence/format check')
    if not asset.get('usage_approved'):
        raise ValueError('Missing image usage approval')
    return True
