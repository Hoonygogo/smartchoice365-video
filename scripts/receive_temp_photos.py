#!/usr/bin/env python3
"""Download six independently approved photos from Cloudflare KV into runner temp.
Never stores images in Git history. Verify hashes before use. Fails closed.
Input manifest schema: {"photos":[{"scene":1,"id":"...","sha256":"...","file":"images/scene_01.png","independent_generation":true,"single_scene":true,"visually_checked":true,"storyboard_collage":false,"focus_regions":{"machine":[0.1,0.1,0.9,0.9]}} ...]}.
"""
import argparse,hashlib,json,os,pathlib,re,urllib.request
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--manifest",required=True)
    a.add_argument("--out",required=True)
    z=a.parse_args()
    token=os.environ.get("IMAGE_HANDOFF_TOKEN","")
    base=os.environ.get("IMAGE_HANDOFF_BASE_URL","").rstrip("/")
    if len(token)<16 or not base.startswith("https://"):raise SystemExit("Missing secure handoff settings")
    data=json.loads(pathlib.Path(z.manifest).read_text())
    photos=data.get("photos",[])
    if len(photos)!=6 or sorted(p.get("scene") for p in photos)!=[1,2,3,5,8,9]:
        raise SystemExit("Expected six independent photos for scenes 2,3,4,6,9,10 (zero-indexed)")
    root=pathlib.Path(z.out).resolve()
    root.mkdir(parents=True,exist_ok=True)
    seen=set()
    for p in photos:
        if not (p.get("independent_generation") is True and p.get("single_scene") is True and p.get("visually_checked") is True and p.get("storyboard_collage") is False):raise SystemExit("Missing genuine individual image approval")
        key=p.get("id","")
        if not re.fullmatch(r"[A-Za-z0-9_-]{8,80}",key):raise SystemExit("Invalid temporary asset id")
        digest=p.get("sha256","").lower()
        if not re.fullmatch(r"[a-f0-9]{64}",digest) or digest in seen:raise SystemExit("Duplicate or invalid SHA256")
        seen.add(digest)
        name=p.get("file","")
        dest=(root/name).resolve()
        if not dest.is_relative_to(root) or dest.suffix.lower() not in (".png",".jpg",".jpeg",".webp"):raise SystemExit("Unsafe photo path")
        req=urllib.request.Request(base+"/assets/"+key,headers={"Authorization":"Bearer "+token,"User-Agent":"SmartChoice365-Video-Handoff/1.0 (+GitHub-Actions)"})
        with urllib.request.urlopen(req,timeout=40) as response:
            if response.status!=200:raise SystemExit("Photo download failed")
            image=response.read(8*1024*1024+1)
        if len(image)>8*1024*1024 or hashlib.sha256(image).hexdigest()!=digest:raise SystemExit("Image exceeds limit or SHA256 mismatch")
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(image)
    # Renderer consumes the same manifest, stripped of temporary IDs.
    for p in photos:p.pop("id",None)
    (root/"approved_visual_manifest.json").write_text(json.dumps(data,indent=2))
    print("Received six SHA-verified temporary photos into Actions workspace")
if __name__=="__main__":main()
