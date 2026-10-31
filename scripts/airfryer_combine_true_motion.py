#!/usr/bin/env python3
"""Merge verified real Hugging Face character animation over 6-scene Kokoro narration video.
Source audio is copied unmodified from the approved narration master; never synthesize fallback TTS.
"""
import json, subprocess, pathlib, sys
master=pathlib.Path("input/kokoro/SmartChoice365_AirFryer_Kokoro_English.mp4")
motion=pathlib.Path("input/motion/airfryer_true_motion.mp4")
out=pathlib.Path("out/SmartChoice365_AirFryer_Full_Animated_Kokoro.mp4")
if not master.is_file() or not motion.is_file():raise SystemExit("Missing real source media; not substituting mock animations or voice")
out.parent.mkdir(parents=True,exist_ok=True)
def probe(p):
 r=subprocess.run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(p)],capture_output=True,text=True,check=True)
 return json.loads(r.stdout)
m=probe(master);v=probe(motion)
assert any(x["codec_type"]=="audio" for x in m["streams"]),"Kokoro master has no audio"
assert any(x["codec_type"]=="video" for x in v["streams"]),"HF motion MP4 has no video"
# Picture-in-picture moving mascot across the full narration. Master images remain legible.
cmd=["ffmpeg","-hide_banner","-y","-loglevel","warning","-i",str(master),
     "-stream_loop","-1","-i",str(motion),
     "-filter_complex",
     "[1:v]fps=24,scale=560:560:force_original_aspect_ratio=decrease,pad=560:560:(ow-iw)/2:(oh-ih)/2:color=0x101820,setsar=1[moving];"
     "[0:v][moving]overlay=x=W-w-30:y=34:shortest=1:format=auto,format=yuv420p[v]",
     "-map","[v]","-map","0:a:0","-c:v","libx264","-preset","veryfast","-crf","22",
     "-c:a","copy","-movflags","+faststart","-shortest",str(out)]
subprocess.run(cmd,check=True)
res=probe(out)
assert int(next(s for s in res["streams"] if s["codec_type"]=="video")["width"])==1920
assert any(s["codec_type"]=="audio" for s in res["streams"])
assert out.stat().st_size>50000
print("FULL_VIDEO_READY",out,"bytes",out.stat().st_size)
