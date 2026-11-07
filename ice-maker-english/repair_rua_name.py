#!/usr/bin/env python3
"""Regenerate only the two verified RUA-name scenes using genuine Kokoro.
The visible/closed-caption brand spelling stays RUA. The synthesized spoken text
says 'Roo-ah' to prevent the model from spelling the acronym R-U-A.
"""
import hashlib, json, re
from pathlib import Path
import numpy as np, soundfile as sf
from kokoro import KPipeline

ROOT=Path(__file__).resolve().parent
cfg=json.loads((ROOT/"kokoro_storyboard.json").read_text())
assert len(cfg["scenes"])==15
assert (cfg["voice"],cfg["speed"],cfg["sample_rate"])==("af_heart",0.96,24000)
out=ROOT/"name-repair-audio"
out.mkdir(exist_ok=True)
pipe=KPipeline(lang_code="a")
receipt={"source":"15-scene production audit","scenes_changed":[0,14],"voice":"af_heart","speed":0.96,"sample_rate":24000,"replacements":[]}
for index in (0,14):
    original=cfg["scenes"][index]["voice"]
    assert len(re.findall(r"\bRUA\b",original))==1, (index,original)
    spoken=re.sub(r"\bRUA\b", "Roo-ah", original)
    assert not re.search(r"\bRUA\b",spoken)
    chunks=[]
    for p in pipe(spoken,voice="af_heart",speed=0.96):
        a=p.audio
        if hasattr(a,"detach"):a=a.detach().cpu().numpy()
        a=np.asarray(a,dtype=np.float32).reshape(-1)
        if a.size:chunks.append(a)
    if not chunks:raise RuntimeError(f"Empty Kokoro speech for scene {index}")
    sound=np.concatenate(chunks)
    if not np.isfinite(sound).all() or np.sqrt(np.mean(sound**2))<0.002:
        raise RuntimeError("Invalid or silent audio")
    target=out/f"scene_{index:02d}_Roo-ah.wav"
    sf.write(target,sound,24000,subtype="PCM_16")
    item={"scene":index,"original_script":original,"spoken_kokoro_text":spoken,"speech_seconds":round(len(sound)/24000,4),"wav_sha256":hashlib.sha256(target.read_bytes()).hexdigest()}
    receipt["replacements"].append(item)
    print(f"KOKORO_RUA_NAME_REPAIRED: scene={index},seconds={item['speech_seconds']}",flush=True)
(out/"rua_name_audit.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
print("RUA_NAME_TWO_SCENE_SYNTHESIS_DONE",flush=True)
