#!/usr/bin/env python3
"""Mandatory 12-scene, 8-photo visual gate; never infer human approval from file existence."""
import json,sys
from pathlib import Path
from PIL import Image

def validate(manifest_path):
    path=Path(manifest_path);doc=json.loads(path.read_text())
    assets=doc.get('assets',doc.get('scenes',[]))
    errors=[];photo_count=0
    if len(assets)!=12:errors.append(f'Expected 12 independent scenes, found {len(assets)}')
    for i,item in enumerate(assets):
        tag=f'scene[{i}]'
        kind=item.get('source_kind')
        photo=kind=='single_full_frame_photo' and item.get('is_photo_led') is True
        if photo:photo_count+=1
        if kind not in ('single_full_frame_photo','single_full_frame_illustration','original_native_graph'):
            errors.append(tag+': invalid source_kind')
        if any(item.get(k) is not False for k in ('contact_sheet','baked_in_storyboard_labels','contains_crop_loss')):
            errors.append(tag+': collage/labels/crop-loss rejection evidence missing or failed')
        for k in ('usage_approved','visual_review_passed'):
            if item.get(k) is not True:errors.append(tag+': '+k+' must be independently verified')
        if not item.get('provenance') or not item.get('sha256'):
            errors.append(tag+': source provenance and hash required')
        filename=item.get('file')
        if not filename:errors.append(tag+': image missing');continue
        file=(path.parent/filename).resolve()
        if not file.is_relative_to(path.parent.resolve()) or not file.is_file():
            errors.append(tag+': invalid/missing image');continue
        try:
            import hashlib
            if hashlib.sha256(file.read_bytes()).hexdigest()!=item.get('sha256'):errors.append(tag+': hash mismatch')
            with Image.open(file) as im:
                if im.size!=(1920,1080):errors.append(tag+': non-native 1920x1080 source')
        except Exception as e:errors.append(tag+': unreadable image '+str(type(e).__name__))
    if photo_count<8:errors.append(f'Only {photo_count}/8 verified photo-led scenes')
    return errors

if __name__=='__main__':
    errors=validate(sys.argv[1])
    print(json.dumps({'passed':not errors,'errors':errors},ensure_ascii=False,indent=2))
    sys.exit(0 if not errors else 2)
