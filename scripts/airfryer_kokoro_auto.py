#!/usr/bin/env python3
"""Six-scene animated-style review: Cloudflare FLUX images + approved Kokoro af_heart audio.
One inference per scene; no paid fallback; a failed voice fails the entire build.
"""
import base64,hashlib,json,os,pathlib,subprocess,sys,urllib.request,urllib.error
from PIL import Image,ImageOps
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from scripts.approved_voice import kokoro_english_pipeline,render_english_clause
R=pathlib.Path("out/airfryer-kokoro")
R.mkdir(parents=True,exist_ok=True)
S=[
("WELCOME TO SMART CHOICE 365","Hello, and welcome to Smart Choice 365. Today, we are exploring how to choose an air fryer for your kitchen.","Friendly cream-coloured rounded air fryer mascot waving both arms happily in a modern warm sunny Australian kitchen, centered, full body visible."),
("CRISPY RESULTS","A great air fryer can make crispy chips with less added oil. But the right model depends on your portions, budget, and available bench space.","Same friendly cream rounded air fryer mascot with red brown eyes pink cheeks, presenting a generous bowl of golden crispy potato chips on kitchen bench."),
("CAPACITY MATTERS","Start with capacity. A small basket suits one or two people. For larger families, compare how much food you can actually cook in one batch.","Same friendly cream rounded air fryer mascot pointing to two differently sized simple unbranded air fryer baskets side by side on a warm kitchen counter."),
("CLEANING AND CONTROLS","Look for simple controls, a basket that is easy to clean, and enough room around the appliance for safe airflow.","Same friendly cream rounded air fryer mascot next to a removable clean air fryer basket, cheerful kitchen demonstration, no labels."),
("SMART VALUE","Our pick is not automatically the biggest or most expensive option. The best value is the model you will use often and can clean easily.","Same friendly cream rounded air fryer mascot thoughtfully comparing a small and large unbranded air fryer on counter, balanced composition."),
("THANKS FOR WATCHING","For a detailed buying guide, visit Smart Choice 365. Subscribe for more practical comparisons, and make your next purchase a smarter choice.","Same friendly cream rounded air fryer mascot smiling and waving goodbye in a lovely sunlit modern kitchen, visually inviting outro."),
]
def run(cmd):
 subprocess.run(cmd,check=True)
def main():
 if os.environ.get("CLOUDFLARE_WORKERS_FREE_CONFIRMED")!="true":raise SystemExit("Free plan guard not confirmed")
 account=os.environ["CLOUDFLARE_ACCOUNT_ID"]; token=os.environ["CLOUDFLARE_AI_TOKEN"]
 url=f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/black-forest-labs/flux-1-schnell"
 pipe=kokoro_english_pipeline()
 clips=[]; receipts=[]
 for i,(title,voice,prompt) in enumerate(S,1):
  request=urllib.request.Request(url,data=json.dumps({"prompt":"ONE original premium 3D animated film still. Wide 16:9 composition, keep entire subject inside frame. "+prompt+" Soft cinematic lighting, single scene, no text, no logos, no collage.","steps":4}).encode(),method="POST",headers={"Authorization":"Bearer "+token,"Content-Type":"application/json","User-Agent":"SmartChoice365-Video/1.0"})
  try:
   with urllib.request.urlopen(request,timeout=80) as response: data=json.load(response)
  except urllib.error.HTTPError as e:raise SystemExit(f"Cloudflare image generation failed on scene {i}: HTTP {e.code}; no retry, no paid fallback")
  encoded=(data.get("result") or {}).get("image")
  if not data.get("success") or not encoded:raise SystemExit("Cloudflare returned no image on scene "+str(i))
  b=base64.b64decode(encoded,validate=True)
  if not (b.startswith(bytes.fromhex("ffd8ff")) or b.startswith(bytes.fromhex("89504e470d0a1a0a"))):raise SystemExit("Invalid image signature")
  raw=R/f"scene_{i:02}.jpg";raw.write_bytes(b)
  im=Image.open(raw).convert("RGB")
  base=Image.new("RGB",(1920,1080),(22,27,31)); im=ImageOps.contain(im,(1920,1080),Image.Resampling.LANCZOS)
  base.paste(im,((1920-im.width)//2,(1080-im.height)//2))
  # Reserve a bottom text banner and render title without hiding the mascot face.
  from PIL import ImageDraw,ImageFont
  d=ImageDraw.Draw(base,"RGBA");d.rectangle((0,930,1920,1080),fill=(5,14,21,215))
  font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",45)
  d.text((80,979),title,font=font,fill=(255,255,255,255))
  art=R/f"frame_{i:02}.jpg";base.save(art,quality=91)
  wav=R/f"voice_{i:02}.wav";rec=render_english_clause(pipe,voice,wav);receipts.append(rec)
  import soundfile as sf
  f,sr=sf.read(wav);dur=len(f)/sr+0.35
  clip=R/f"clip_{i:02}.mp4"
  run(["ffmpeg","-y","-loglevel","error","-loop","1","-framerate","24","-i",str(art),"-i",str(wav),"-filter_complex",f"[0:v]scale=2000:1125,crop=1920:1080:x='40+40*sin(t/6)':y=22,format=yuv420p[v]","-map","[v]","-map","1:a","-t",str(dur),"-c:v","libx264","-preset","veryfast","-crf","23","-r","24","-c:a","aac","-b:a","160k","-movflags","+faststart",str(clip)])
  clips.append(clip)
  print("Scene",i,"Kokoro audio and image rendered",flush=True)
 concat=R/"concat.txt";concat.write_text("".join("file '"+str(p.resolve())+"'\n" for p in clips))
 final=R/"SmartChoice365_AirFryer_Kokoro_English.mp4"
 run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-c","copy","-movflags","+faststart",str(final)])
 run(["ffprobe","-v","error","-select_streams","a:0","-show_entries","stream=codec_name","-of","default=noprint_wrappers=1",str(final)])
 (R/"receipts.json").write_text(json.dumps({"approved_voice":"af_heart","speed":0.96,"clips":receipts,"final_sha256":hashlib.sha256(final.read_bytes()).hexdigest()},indent=2))
 print("FINAL_KOKORO_VIDEO",final,flush=True)
if __name__=="__main__":main()
