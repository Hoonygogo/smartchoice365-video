#!/usr/bin/env python3
"""Render every approved ice-maker guide sentence with actual Kokoro af_heart, never eSpeak."""
import hashlib
import json
import re
from pathlib import Path
import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = Path(__file__).resolve().parent
config = json.loads((ROOT / "kokoro_storyboard.json").read_text(encoding="utf-8"))
assert (config["lang_code"], config["voice"], config["speed"], config["sample_rate"]) == ("a","af_heart",0.96,24000)
assert len(config["scenes"]) == 15
output = ROOT / "output"
segments = output / "audio"
segments.mkdir(parents=True,exist_ok=True)
pipeline = KPipeline(lang_code="a")
parts = []
durations = []
receipts = []
sr = 24000
for i, scene in enumerate(config["scenes"]):
    chunks = []
    # RUA is the written character/brand; voice must say Roo-ah, never R-U-A.
    display_text = scene["voice"]
    spoken_text = re.sub(r"\\bRUA\\b", "Roo-ah", display_text)
    if re.search(r"\\bRUA\\b", spoken_text):
        raise RuntimeError("Unnormalized spoken RUA would be spelled letter by letter")
    for result in pipeline(spoken_text,voice="af_heart",speed=0.96):
        a = result.audio
        if a is None:
            raise RuntimeError(f"Kokoro generated no audio in scene {i}")
        if hasattr(a, "detach"):
            a = a.detach().cpu().numpy()
        a = np.asarray(a,dtype=np.float32).reshape(-1)
        if a.size: chunks.append(a)
    if not chunks: raise RuntimeError(f"No speech in scene {i}")
    speech = np.concatenate(chunks)
    if not np.isfinite(speech).all(): raise RuntimeError("Invalid Kokoro samples")
    if float(np.sqrt(np.mean(speech ** 2))) < 0.002: raise RuntimeError("Silent voice generated")
    segpath = segments / f"{i:02d}.wav"
    sf.write(segpath,speech,sr,subtype="PCM_16")
    pad = np.zeros(round(sr*float(config["pad_seconds"])),dtype=np.float32)
    parts.append(np.concatenate([speech,pad]))
    duration = (speech.size+pad.size)/sr
    durations.append(duration)
    receipts.append({
        "scene_index":i,"voice":"af_heart","speed":0.96,"sample_rate":sr,
        "speech_seconds":round(speech.size/sr,4),"scene_seconds":round(duration,4),
        "wav_sha256":hashlib.sha256(segpath.read_bytes()).hexdigest(),
        "rms":round(float(np.sqrt(np.mean(speech**2))),6),
        "text":scene["voice"], "spoken_text":spoken_text
    })
    print(f"KOKORO_AUDIO_SCENE_{i:02d} speech={speech.size/sr:.2f}s scene={duration:.2f}s rms={receipts[-1]['rms']}",flush=True)

full = np.concatenate(parts)
sf.write(output/"narration.wav",full,sr,subtype="PCM_16")
manifest = {
    "id":config["id"],"engine":"Kokoro KPipeline (not eSpeak)",
    "voice":"af_heart","lang_code":"a","speed":0.96,
    "sample_rate":sr,"scene_count":15,
    "scene_durations":durations,"total_seconds":full.size/sr,
    "sha256":hashlib.sha256((output/"narration.wav").read_bytes()).hexdigest(),
    "receipts":receipts
}
(output/"kokoro_voice_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert float(np.sqrt(np.mean(full**2))) > 0.002
print("KOKORO_VOICE_RENDER_SUCCESS",round(full.size/sr,3),manifest["sha256"],flush=True)
