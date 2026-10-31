#!/usr/bin/env python3
"""Generate 8 standalone AI lifestyle-photo candidate scenes via an explicit HF inference token.
Fail closed on missing credentials or exhausted free credits. Never assert visual approval.
"""
import os, json, hashlib, random, time, sys
from pathlib import Path
from PIL import Image, ImageOps
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'ninja-english'/'ai-candidates'
OUT.mkdir(parents=True,exist_ok=True)
PROMPTS=[
 ("welcome","Wide single coherent photographic shot of a warm modern Australian kitchen island with two different size black countertop air fryers, delicious roast foods, a friendly lifestyle editorial look. Entire appliances visible."),
 ("choice","Wide single scene in an Australian family kitchen, one person thoughtfully comparing a compact black countertop air fryer with a larger two drawer air fryer. Both devices fully visible."),
 ("cooking","Single naturally lit culinary kitchen scene, crisp golden air fried potatoes on a platter near an air fryer, fresh herbs, realistic food texture."),
 ("capacity","Single coherent wide kitchen product still life featuring compact and large black air fryers displayed beside their separate food serving bowls, appliances entirely visible."),
 ("dual","Photographic kitchen editorial shot of roast chicken and colourful vegetables in separate serving dishes beside a dual drawer black air fryer, full frame."),
 ("small","Single everyday small apartment kitchen scene with one plated small serving of home cooked chips and vegetables, compact air fryer on bench."),
 ("family","Australian family dinner setting with several plated home cooked dishes and two drawer air fryer safely positioned on adjacent countertop, warm natural evening light."),
 ("verdict","Premium editorial kitchen still life with two different size air fryers and abundant appetising plated food, warm lighting, both appliances entirely visible.")
]
SUFFIX=("Generate ONE original standalone photorealistic 16:9 scene. A single coherent shot, not panels, collage, storyboard or grid. "
        "No written words, numbers, logos, timecodes, diagrams, frame borders or labels. "
        "Keep all people, appliances and essential food completely inside generous safe margins. "
        "This is an illustrative concept image, not verified manufacturer photography or a hands-on test.")
def main():
    if os.getenv('ALLOW_PAID_IMAGE_API') not in (None,'','false','0'):
        raise RuntimeError('Paid API mode is forbidden in this A$0 workflow')
    token=os.getenv('HF_TOKEN','').strip()
    if not token:
        raise RuntimeError('AI_GENERATION_NOT_CONNECTED: Configure HF_TOKEN with a fine-grained Inference Providers token; no charges are initiated.')
    from huggingface_hub import InferenceClient
    client=InferenceClient(api_key=token)
    model=os.getenv('HF_IMAGE_MODEL','black-forest-labs/FLUX.1-dev')
    result=[]
    for i,(key,prompt) in enumerate(PROMPTS,1):
        file=OUT/f'ai_{i:02}.png'
        if not file.exists():
            try:
                generated=client.text_to_image(prompt+' '+SUFFIX,model=model)
            except Exception as exc:
                # Never retry an unknown or paid inference result automatically
                raise RuntimeError('AI generation failed / free credits unavailable; stop instead of accepting a paid fallback: '+type(exc).__name__) from None
            im=ImageOps.exif_transpose(generated).convert('RGB')
            # Non-cropping letterbox into final native render frame.
            canvas=Image.new('RGB',(1920,1080),'#14283b')
            fit=ImageOps.contain(im,(1920,1080),Image.Resampling.LANCZOS)
            canvas.paste(fit,((1920-fit.width)//2,(1080-fit.height)//2))
            canvas.save(file,optimize=True)
        with Image.open(file) as pic:assert pic.size==(1920,1080)
        result.append({'scene_id':key,'file':file.name,'generation_method':'individual_ai_generated',
                       'source_kind':'single_full_frame_photo','is_photo_led':True,
                       'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
                       'provenance':'AI original via Hugging Face inference providers ('+model+')',
                       'contact_sheet':False,'baked_in_storyboard_labels':False,'contains_crop_loss':False,
                       'visual_review_passed':False,'usage_approved':False})
        print('Image candidate',i,'of',len(PROMPTS),'complete',flush=True)
    (OUT/'ai_candidates.json').write_text(json.dumps({'photos':result,'publish_ready':False,'visual_review_required':True},indent=2)+'\n')
if __name__=='__main__':main()
