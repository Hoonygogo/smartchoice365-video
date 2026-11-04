#!/usr/bin/env python3
import json,math,hashlib
from pathlib import Path
import numpy as np
import soundfile as sf
from supertonic import TTS

ROOT=Path("mats")
data=json.loads((ROOT/"request.json").read_text(encoding="utf-8"))
out=ROOT/"output";out.mkdir(parents=True,exist_ok=True)
engine=TTS(model="supertonic-3",model_dir=".models/supertonic-3",auto_download=False,intra_op_num_threads=2,inter_op_num_threads=1)
style=engine.get_voice_style(voice_name="F1")
rate=engine.sample_rate
parts=[];timing=[];elapsed=0
for cue in data["cues"]:
    audio,_=engine.synthesize(cue["text"],voice_style=style,total_steps=8,speed=1.1,lang="ko")
    audio=np.asarray(audio,dtype=np.float32).reshape(-1)
    if len(audio)==0 or not np.isfinite(audio).all() or np.sqrt(np.mean(audio**2))<0.001:raise RuntimeError("invalid audio "+str(cue["i"]))
    gap=int(rate*(.18 if cue["i"]==len(data["cues"]) else .10))
    part=np.concatenate([audio,np.zeros(gap,dtype=np.float32)])
    start=elapsed;elapsed+=len(part)/rate
    timing.append({**cue,"start":round(start,3),"end":round(elapsed,3),"audio_seconds":round(len(audio)/rate,3)})
    parts.append(part)
    print(f'{cue["i"]:02d} {cue["scene"]}: {elapsed:.1f}s',flush=True)
voice=np.concatenate(parts)
sf.write(out/"voice.wav",voice,rate)
(out/"timings.json").write_text(json.dumps({"id":data["id"],"voice":"Sarah F1","sample_rate":rate,"total_seconds":round(elapsed,3),"cues":timing},ensure_ascii=False,indent=2),encoding="utf-8")
def ts(t):
    h=int(t//3600);m=int(t%3600//60);s=int(t%60);ms=int(round((t%1)*1000))
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
(out/"captions.srt").write_text("\n\n".join(f'{i+1}\n{ts(c["start"])} --> {ts(c["end"])}\n{c["caption"]}' for i,c in enumerate(timing)),encoding="utf-8")
(out/"request.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
assert 85<=elapsed<=230,("duration outside expected 2-3 minute range",elapsed)
print("SUCCESS",elapsed,"s Sarah Korean narration")
