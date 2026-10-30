"""Create an approval-only, mobile-compatible Korean Sarah draft."""
import argparse
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
from datetime import datetime, timezone

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import soundfile as sf

MODEL_REVISION = "3cadd1ee6394adea1bd021217a0e650ede09a323"
WIDTH, HEIGHT = 720, 1280


def validate_request(data):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,60}", data.get("id", "")):
        raise ValueError("Invalid draft id")
    scenes = data.get("scenes", [])
    if not 1 <= len(scenes) <= 20:
        raise ValueError("Use 1–20 scenes")
    if not isinstance(data.get("title"), str) or not data["title"].strip():
        raise ValueError("A title is required")
    from urllib.parse import urlparse
    url = urlparse(data.get("guide_url", ""))
    if url.scheme != "https" or url.hostname != "smartchoice365-web.pages.dev":
        raise ValueError("Guide URL must use the official HTTPS site")
    for scene in scenes:
        for key in ("eyebrow", "heading", "body", "narration"):
            if not isinstance(scene.get(key), str) or not scene[key].strip():
                raise ValueError(f"Missing scene field: {key}")
        if len(scene["narration"]) > 500:
            raise ValueError("Split narrations longer than 500 characters")
    if sum(len(s["narration"]) for s in scenes) > 4000:
        raise ValueError("Draft narration exceeds initial size budget")
    return data


def font_path():
    configured = os.getenv("SC365_FONT")
    if configured and Path(configured).is_file():
        return configured
    for path in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                 "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"]:
        if Path(path).is_file():
            return path
    raise RuntimeError("Install fonts-noto-cjk or set SC365_FONT to a Korean font")


def wrap(draw, text, font, max_width):
    lines = []
    for paragraph in text.split("\n"):
        line = ""
        for ch in paragraph:
            if line and draw.textlength(line + ch, font=font) > max_width:
                lines.append(line.strip())
                line = ch
            else:
                line += ch
        lines.append(line.strip())
    return lines


def text_block(draw, text, y, size, color, *, width=600, gap=14, max_y=1200):
    font = ImageFont.truetype(font_path(), size)
    lines = wrap(draw, text, font, width)
    bottom = y + len(lines) * (size + gap)
    if bottom > max_y:
        raise ValueError("Text would overflow the scene; shorten the copy")
    for line in lines:
        draw.text((60, y), line, font=font, fill=color)
        y += size + gap
    return y


def draw_scene(scene, index, total, path):
    im = Image.new("RGB", (WIDTH, HEIGHT), "#f5f3ec")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((48, 58, 672, 112), radius=27, fill="#143f3a")
    d.text((73, 72), "SMART CHOICE 365", font=ImageFont.truetype(font_path(), 20), fill="white")
    d.text((574, 73), f"{index:02}/{total:02}", font=ImageFont.truetype(font_path(), 18), fill="#cce9d1")
    d.ellipse((475, 160, 760, 445), fill="#dee9db")
    d.ellipse((555, 240, 665, 350), fill="#c5d6bc")
    text_block(d, scene["eyebrow"], 210, 19, "#4b6a5b", max_y=300)
    text_block(d, scene["heading"], 330, 59, "#143f3a", gap=18, max_y=610)
    d.rectangle((60, 640, 142, 647), fill="#e8a540")
    text_block(d, scene["body"], 704, 28, "#40504a", gap=16, max_y=920)
    d.rounded_rectangle((40, 970, 680, 1177), radius=24, fill="#143f3a")
    text_block(d, scene["narration"], 1000, 23, "#ffffff", width=600, gap=12, max_y=1165)
    d.text((60, 1212), "DRAFT / 확인용 초안 · SNS 미발행", font=ImageFont.truetype(font_path(), 18), fill="#647268")
    im.save(path)


def timestamp(seconds):
    millis = round(seconds * 1000)
    h, rem = divmod(millis, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def write_preview(out, data, manifest):
    title = html.escape(data["title"])
    guide = html.escape(data["guide_url"], quote=True)
    script = "".join(f"<p>{html.escape(s['narration'])}</p>" for s in data["scenes"])
    content = f'''<!doctype html><html lang="ko"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>
<style>body{{margin:0;background:#f5f3ec;color:#143f3a;font:16px/1.65 system-ui,sans-serif}}main{{max-width:700px;margin:32px auto;padding:20px}}video{{display:block;width:100%;max-height:75vh;background:#111;border-radius:18px}}a{{color:#143f3a}}.pill{{display:inline-block;padding:5px 12px;border-radius:24px;background:#dce9da}}.links{{display:flex;gap:20px;flex-wrap:wrap}}small{{overflow-wrap:anywhere}}</style>
<main><span class="pill">컨펌 대기 · SNS 미발행</span><h1>{title}</h1>
<p>목소리: Sarah · 한국어 · 먼저 재생해서 음성과 자막을 확인해 주세요.</p>
<video controls playsinline preload="metadata" poster="poster.jpg"><source src="draft.mp4" type="video/mp4"></video>
<p class="links"><a href="draft.mp4" download>MP4 다운로드</a><a href="voice.wav" download>음성만 듣기</a><a href="{guide}" target="_blank" rel="noopener">구매가이드 열기</a></p>
<p>발행하려면 이 버전을 확인한 뒤 대화에서 <strong>“{html.escape(data['id'])} 버전 {manifest['sha256'][:12]} 발행해”</strong>라고 알려주세요. 이 페이지에는 자동 발행 버튼이 없습니다.</p>
<small>버전: {manifest['sha256'][:12]} · 생성: {manifest['created_at']} · 초안은 공개 링크로 접근할 수 있습니다.</small>
<details><summary>내레이션 대본</summary>{script}</details></main></html>'''
    (out / "index.html").write_text(content, encoding="utf-8")


def render(request, output, model_dir, smoke=False):
    data = validate_request(json.loads(Path(request).read_text(encoding="utf-8")))
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    engine = None
    if not smoke:
        from supertonic import TTS
        engine = TTS(model="supertonic-3", model_dir=model_dir, auto_download=False,
                     intra_op_num_threads=2, inter_op_num_threads=1)
        style = engine.get_voice_style(voice_name="F1")  # Sarah, verified in official demo script.js
    elapsed, audio_parts, srt = 0.0, [], []
    rate = engine.sample_rate if engine else 44100
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        clips = []
        for i, scene in enumerate(data["scenes"], 1):
            image, wav, clip = tmp / f"{i}.png", tmp / f"{i}.wav", tmp / f"{i}.mp4"
            draw_scene(scene, i, len(data["scenes"]), image)
            if i == 1:
                Image.open(image).save(out / "poster.jpg", quality=90)
            if engine:
                audio, _ = engine.synthesize(scene["narration"], voice_style=style,
                                             total_steps=8, speed=1.0, lang="ko")
                audio = np.asarray(audio).reshape(-1)
            else:
                audio = np.zeros(rate, dtype=np.float32)
            if len(audio) == 0 or not np.isfinite(audio).all():
                raise ValueError("Invalid synthesized audio")
            # Keep the whole delivered voice waveform and align cards to real audio lengths.
            padded = np.concatenate([audio, np.zeros(round(rate * .4), dtype=audio.dtype)])
            sf.write(wav, padded, rate)
            duration = len(padded) / rate
            audio_parts.append(padded)
            srt.append(f"{i}\n{timestamp(elapsed)} --> {timestamp(elapsed + duration)}\n{scene['narration']}\n")
            elapsed += duration
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(image),
                            "-i", str(wav), "-t", str(duration), "-r", "24", "-c:v", "libx264",
                            "-preset", "veryfast", "-crf", "23", "-profile:v", "baseline", "-level", "4.0",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                            "-movflags", "+faststart", str(clip)], check=True)
            clips.append(clip)
        playlist = tmp / "concat.txt"
        playlist.write_text("".join(f"file '{c.as_posix()}'\n" for c in clips))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i",
                        str(playlist), "-c", "copy", "-movflags", "+faststart", str(out / "draft.mp4")], check=True)
    sf.write(out / "voice.wav", np.concatenate(audio_parts), rate)
    (out / "captions.srt").write_text("\n".join(srt), encoding="utf-8")
    video = out / "draft.mp4"
    if video.stat().st_size > 90 * 1024 * 1024:
        raise RuntimeError("Draft exceeds 90 MiB preview budget")
    manifest = {"id": data["id"], "status": "awaiting_approval", "published": False,
                "title": data["title"], "guide_url": data["guide_url"], "voice": "Sarah", "voice_style": "F1",
                "model_revision": MODEL_REVISION, "created_at": datetime.now(timezone.utc).isoformat(),
                "sha256": hashlib.sha256(video.read_bytes()).hexdigest(), "duration_seconds": elapsed,
                "smoke_test_only": smoke, "platform_posts": {}}
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "script.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_preview(out, data, manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--request", default="requests/sarah-test.json")
    p.add_argument("--output", default="output")
    p.add_argument("--model-dir", default=".models/supertonic-3")
    p.add_argument("--smoke-test", action="store_true", help="Silent local renderer test; never used by publishing workflows")
    args = p.parse_args()
    render(args.request, args.output, args.model_dir, args.smoke_test)

