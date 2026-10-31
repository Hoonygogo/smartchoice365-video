"""Single source of truth for production TTS. Fails closed, never changes voice."""
import json,hashlib
from pathlib import Path
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config'/'approved_voices.json'
def approved_voice(language):
    cfg=json.loads(CONFIG.read_text())
    voice=cfg[language]
    assert cfg['rules']['fallback_voice_allowed'] is False
    return voice
def kokoro_english_pipeline():
    cfg=approved_voice('english')
    if (cfg['engine'],cfg['voice'],cfg['lang_code'],cfg['speed'])!=('kokoro','af_heart','a',0.96):
        raise RuntimeError('Unexpected English TTS configuration: forbidden voice substitution')
    from kokoro import KPipeline
    return KPipeline(lang_code=cfg['lang_code'])
def render_english_clause(pipeline,txt,out):
    cfg=approved_voice('english')
    parts=[np.asarray(audio,dtype=np.float32) for _,_,audio in pipeline(txt,voice=cfg['voice'],speed=cfg['speed'])]
    if not parts:raise RuntimeError('Selected Kokoro voice failed: no fallback allowed')
    audio=np.concatenate(parts)
    rms=float(np.sqrt(np.mean(audio*audio)))
    peak=float(np.max(np.abs(audio)))
    if len(audio)<cfg['sample_rate'] or rms<0.008 or peak<0.03:
        raise RuntimeError(f'Kokoro output invalid: samples={len(audio)} rms={rms:.4f} peak={peak:.4f}')
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    sf.write(out,audio,cfg['sample_rate'])
    reread,sr=sf.read(out,dtype='float32')
    if sr!=cfg['sample_rate'] or np.sqrt(np.mean(reread*reread))<0.008:
        raise RuntimeError('Voice file failed decoded playback amplitude verification')
    return {'engine':cfg['engine'],'voice':cfg['voice'],'speed':cfg['speed'],
            'sample_rate':sr,'samples':len(reread),'rms':rms,'peak':peak,
            'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
            'file':str(out)}
