#!/usr/bin/env python3
"""Fail-closed AI photo gate: six distinct full-frame originals; no storyboard collages."""
from pathlib import Path
from PIL import Image
import argparse,hashlib,json,sys
def main():
    p=argparse.ArgumentParser()
    p.add_argument("directory",type=Path)
    p.add_argument("--manifest",type=Path)
    a=p.parse_args()
    photos=sorted(x for x in a.directory.iterdir() if x.is_file() and x.suffix.lower() in ('.png','.jpg','.jpeg','.webp'))
    if len(photos)!=6:sys.exit(f"FAILED: expected six independently produced full-frame photos, found {len(photos)}")
    hashes=[]
    for photo in photos:
        with Image.open(photo) as im:
            w,h=im.size
            if w<1280 or h<720:sys.exit(f"FAILED: {photo.name} only {w}x{h}")
            rgb=im.convert('RGB')
            hashes.append(hashlib.sha256(rgb.tobytes()).hexdigest())
    if len(set(hashes))!=6:sys.exit("FAILED: duplicate photo originals")
    if not a.manifest or not a.manifest.is_file():sys.exit("FAILED: individual generation/visual verification manifest missing")
    data=json.loads(a.manifest.read_text())
    if len(data.get('photos',[]))!=6:sys.exit("FAILED: 6 photo entries required")
    for i,entry in enumerate(data['photos']):
        if entry.get('filename')!=photos[i].name or entry.get('independent_generation') is not True or entry.get('single_scene') is not True or entry.get('visually_checked') is not True or entry.get('storyboard_collage') is not False:
            sys.exit(f"FAILED: {photos[i].name} needs individually reviewed single-photo proof")
    print("PASS: Six distinct, individually verified full-frame photos")
if __name__=="__main__":main()
