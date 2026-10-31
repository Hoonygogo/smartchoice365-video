#!/usr/bin/env python3
"""Experimental Wan 2.2 image-to-video via PUBLIC Hugging Face ZeroGPU Space.
No paid fallback. This is an optional, manually triggered test, not guaranteed availability.
Endpoint shape checked against IgorCSIS/nifty-vid/worker/src/index.ts (2026-10-31).
"""
import argparse
import json
import os
from pathlib import Path
import sys
import requests

SPACE = "https://cbensimon-wan2-2-fp8da-aoti-preview2.hf.space"
NEGATIVE = ("色调艳丽, 过曝, 静态, 细节模糊不清, 字幕, 风格, 作品, 画作, 画面, 静止, 整体发灰, "
            "最差质量, 低质量, JPEG压缩残留, 丑陋的, 残缺的, 多余的手指, 畸形的, 三条腿")
PROMPT = (
    "Use the supplied reference image as the exact first frame. "
    "A single adorable anthropomorphic black Ninja air fryer celebrates in the same "
    "warm sunlit kitchen. Preserve its identical rounded black appliance silhouette, "
    "front basket, metallic handle, white Ninja logo, two white-gloved hands, "
    "large warm brown eyes, smiling mouth and original proportions throughout. "
    "First the character gives one clear natural blink, then gently and playfully "
    "waves BOTH original arms without adding or changing any limbs. "
    "Three or four crispy golden fries pop upward from the open basket, "
    "rotate slightly while airborne and fall back toward the basket with plausible gravity. "
    "Keep the appliance body almost stationary and the camera locked off. "
    "Smooth consistent cinematic 3D animation, same lighting and background, "
    "subtle expressive facial motion. No melting, stretching, morphing, object duplication, "
    "extra fingers, new characters, logo changes, subtitle overlays or scene cuts."
)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--image", default="assets/ninja_original.png")
    p.add_argument("--image-url", default="")
    p.add_argument("--out", default="out/wan22/ninja_generated.mp4")
    p.add_argument("--prompt", default=PROMPT)
    args=p.parse_args()
    sess=requests.Session()
    token=os.environ.get("HF_TOKEN","").strip()
    if token:
        sess.headers["Authorization"]=f"Bearer {token}"
    if args.image_url:
        if not args.image_url.startswith("https://"):
            sys.exit("Image URL must use HTTPS")
        r=sess.get(args.image_url,timeout=30)
        r.raise_for_status()
        blob=r.content
        filename="ninja_original.png"
    else:
        file=Path(args.image)
        if not file.is_file():
            sys.exit(f"Missing original photo: {file}. Upload exact Ninja image or pass --image-url.")
        blob=file.read_bytes()
        filename=file.name
    if len(blob)>8*1024*1024 or len(blob)<100:
        sys.exit("Source image must be 100 bytes–8MB")
    if blob[:8] != b"\x89PNG\r\n\x1a\n" and not blob.startswith(b"\xff\xd8\xff") and blob[:4]!=b"RIFF":
        sys.exit("Source must be PNG/JPEG/WEBP (not ZIP)")
    up=sess.post(SPACE+"/gradio_api/upload",files={"files":(filename,blob,"image/png")},timeout=120)
    up.raise_for_status()
    file_path=up.json()[0]
    source={"path":file_path,"url":SPACE+"/gradio_api/file="+file_path,
            "orig_name":filename,"size":None,"mime_type":None,
            "meta":{"_type":"gradio.FileData"}}
    data=[source,None,args.prompt,6,NEGATIVE,3.5,1,1,42,True,6,
          "UniPCMultistep",3.0,16,False,True]
    r=sess.post(SPACE+"/gradio_api/call/generate_video",json={"data":data},timeout=120)
    r.raise_for_status()
    event_id=r.json()["event_id"]
    print("Generation queued; shared free quota may fail or time out.",flush=True)
    with sess.get(SPACE+"/gradio_api/call/generate_video/"+event_id,
                  headers={"Accept":"text/event-stream"},stream=True,timeout=(30,900)) as resp:
        resp.raise_for_status()
        event=""
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            if line.startswith("event: "):
                event=line[7:].strip()
            elif line.startswith("data: "):
                payload=line[6:]
                if event=="error":
                    sys.exit("Space reported an error: "+payload[:500])
                if event!="complete":
                    continue
                result=json.loads(payload)
                # Gradio output is an array; video may be dict {'video': {'url':...}}.
                def find_video(v):
                    if isinstance(v,dict):
                        if isinstance(v.get("url"),str) and (".mp4" in v["url"] or "/gradio_api/file=" in v["url"]):
                            return v["url"]
                        for vv in v.values():
                            got=find_video(vv)
                            if got:return got
                    if isinstance(v,list):
                        for vv in v:
                            got=find_video(vv)
                            if got:return got
                    if isinstance(v,str) and v.startswith("http") and ".mp4" in v:
                        return v
                    return None
                url=find_video(result)
                if not url:
                    sys.exit("Completed but no video URL in output; API result shape may have changed")
                if url.startswith("/"):
                    url=SPACE+url
                if not url.startswith("https://") or not ("hf.space" in url.split("/")[2]):
                    sys.exit("Refusing video URL outside Hugging Face Space")
                dst=Path(args.out);dst.parent.mkdir(parents=True,exist_ok=True)
                v=sess.get(url,timeout=120);v.raise_for_status();dst.write_bytes(v.content)
                if dst.stat().st_size<1000:
                    sys.exit("Video download suspiciously small")
                print("Generated:",dst)
                return
    sys.exit("Stream ended without a complete event")

if __name__=="__main__":
    main()
