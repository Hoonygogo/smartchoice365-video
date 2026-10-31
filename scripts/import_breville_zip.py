#!/usr/bin/env python3
"""Import approved image pack to the renderer; verify every source SHA256."""
import hashlib,json,sys,zipfile
from pathlib import Path

def main(zip_path,target):
    target=Path(target);target.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        names=set(z.namelist())
        prefix='breville-english/assets/'
        manifest_name=prefix+'approved_visual_manifest.json'
        if manifest_name not in names:raise RuntimeError('Pack missing manifest')
        manifest=json.loads(z.read(manifest_name))
        scenes=manifest.get('assets',[])
        if len(scenes)!=12:raise RuntimeError('Expected 12 scenes')
        numphoto=0
        for item in scenes:
            name=item['file']
            if '/' in name or '\\' in name or not name.startswith('scene_'):raise RuntimeError('Bad scene name')
            raw=z.read(prefix+name)
            if hashlib.sha256(raw).hexdigest()!=item['sha256']:raise RuntimeError('SHA-256 mismatch for '+name)
            if item.get('visual_review_passed') is not True or item.get('usage_approved') is not True:raise RuntimeError('Unapproved scene '+name)
            if any(item.get(k) for k in ('contact_sheet','baked_in_storyboard_labels','contains_crop_loss')):raise RuntimeError('Invalid collage/label/crop in '+name)
            if item.get('source_kind')=='single_full_frame_photo' and item.get('generation_method')=='individual_ai_generated':numphoto+=1
            (target/name).write_bytes(raw)
        if numphoto<8:raise RuntimeError('Missing eight separate AI photo scenes')
        (target/'approved_visual_manifest.json').write_text(json.dumps(manifest,indent=2))
        print(f'VERIFIED: {len(scenes)} images; {numphoto} independent AI photos')
if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('usage: import_breville_zip.py pack.zip target_dir')
    main(sys.argv[1],sys.argv[2])
