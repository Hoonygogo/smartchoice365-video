#!/usr/bin/env python3
"""Six independently generated comical true-motion HF scenes, synced to approved Kokoro.
Fails closed: no still substitutes, fake movement or synthetic voice fallbacks.
"""
import base64,json,os,pathlib,subprocess,sys,urllib.request,urllib.error
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from scripts.approved_voice import kokoro_english_pipeline,render_english_clause
import soundfile as sf
ROOT=pathlib.Path("out/airfryer-six-animated");ROOT.mkdir(parents=True,exist_ok=True)
STYLE=("A single movie-quality stylized 3D animated film frame of THE SAME friendly cream-colored rounded air fryer "
"mascot, big expressive warm brown eyes, pink cheeks, little smile, precisely two short arms and two short legs, "
"warm bright modern kitchen, framed wide with entire character and key objects visible, no words, no logo, no collage. ")
SCENES=[
("Welcome to Smart Choice 365! Today our little chef is choosing an air fryer. Let's see what really matters.",
"Our little chef bursts into the kitchen, proudly takes a playful bow, then waves at the audience.",
"mascot standing center stage next to a friendly countertop air fryer, welcoming excitedly",
"The mascot blinks, performs one playful bow and waves both original arms, then smiles at camera."),
("Everyone loves crispy chips. But don't let golden potatoes distract you from the things that matter!",
"Our chef gets a little too excited about delicious chips, then catches itself before dropping any.",
"mascot presenting a bowl of crispy golden fries on counter, eager delighted expression",
"The mascot points at the golden chips, a few chips bounce playfully, and it catches one in surprise. Keep chip movement believable."),
("Cooking for one, or feeding a family? Basket capacity makes a huge difference.",
"Our chef shows a tiny basket and a big basket, pretending the tiny one could fit a feast.",
"mascot standing between two different-size empty air fryer baskets on counter, cute amused expression",
"The mascot gestures toward the tiny basket, shakes head playfully, then spreads its arms to present the bigger basket."),
("Easy cleaning is a feature worth celebrating. Check the removable basket and follow the instructions.",
"Our chef happily wipes a basket clean, then celebrates with a little dance.",
"mascot next to clean removable air fryer basket and soft cloth, bright kitchen",
"The mascot carefully wipes the removable empty basket with a cloth, then does a tiny joyful dance with both arms."),
("The most expensive model isn't always the best. Choose what fits your kitchen and cooking habits.",
"Our chef weighs two options, makes a funny thinking face and confidently chooses practicality.",
"mascot comparing a small and large unbranded air fryer, playful thoughtful expression",
"The mascot looks left and right at both models, scratches its cheek thoughtfully, then nods approvingly."),
("Find the full comparison on Smart Choice 365, and subscribe for more smart buying guides!",
"Our cheerful chef waves goodbye while the camera stays steady, with a friendly energetic finale.",
"mascot waving goodbye at counter, background bright sunny kitchen, happy expression",
"The mascot gives a big double-arm wave, happily blinks once and gently bounces in place.")
]
def run(args):subprocess.run(args,check=True)
def ffprobe_duration(p):
 x=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(p)],text=True)
 return float(x)
def main():
 if os.environ.get("CLOUDFLARE_WORKERS_FREE_CONFIRMED")!="true":raise SystemExit("No free-plan confirmation")
 token=os.environ["CLOUDFLARE_AI_TOKEN"];account=os.environ["CLOUDFLARE_ACCOUNT_ID"]
 url=f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/black-forest-labs/flux-1-schnell"
 pipeline=kokoro_english_pipeline()
 ready=[]
 for i,(narration,comic,visual,motion) in enumerate(SCENES,1):
  stem=f"scene_{i:02}"
  image=ROOT/f"{stem}.jpg";clip=ROOT/f"{stem}_motion.mp4";wav=ROOT/f"{stem}_voice.wav"
  if not (image.exists() and image.stat().st_size>10000):
   request=urllib.request.Request(url,data=json.dumps({"prompt":STYLE+visual,"steps":4}).encode(),method="POST",headers={"Authorization":"Bearer "+token,"Content-Type":"application/json","User-Agent":"SmartChoice365-Video/1.0"})
   try:
    with urllib.request.urlopen(request,timeout=90) as response:result=json.load(response)
   except urllib.error.HTTPError as e:raise SystemExit(f"AI picture scene {i}: HTTP {e.code} (no paid retry)")
   raw=base64.b64decode((result.get("result") or {}).get("image",""),validate=True)
   if not result.get("success") or not raw.startswith(bytes.fromhex("ffd8ff")):raise SystemExit(f"Bad scene {i} image")
   image.write_bytes(raw)
  if not clip.exists():
   prompt=("Animate the exact supplied first frame. Preserve the same 3D mascot identity, facial features, limbs, "
           "appliance shape and background. "+motion+" Natural funny timing and expressive motion, camera locked, "
           "NO zooms, NO scene changes, NO extra limbs, NO melting or morphing, NO overlays or text.")
   run(["python","experiments/wan22_image_to_video.py","--image",str(image),"--prompt",prompt,"--out",str(clip)])
  render_english_clause(pipeline,narration,wav)
  if ffprobe_duration(clip)<1:raise SystemExit("Empty HF true animation in "+stem)
  voicedur=ffprobe_duration(wav)
  # Repeat true animation clip as needed to fill narration; never replace with camera zoom or still.
  out=ROOT/f"{stem}_with_voice.mp4"
  run(["ffmpeg","-y","-loglevel","error","-stream_loop","-1","-i",str(clip),"-i",str(wav),
       "-filter_complex","[0:v]fps=24,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x101820,format=yuv420p[v]",
       "-map","[v]","-map","1:a:0","-t",str(voicedur+0.25),"-c:v","libx264","-preset","veryfast","-crf","24",
       "-c:a","aac","-b:a","160k",str(out)])
  ready.append(out)
  print(f"SCENE {i}/6 REAL MOTION OK + Kokoro OK",flush=True)
 paths=ROOT/"concat.txt";paths.write_text("".join("file '"+str(p.resolve())+"'\n" for p in ready))
 dest=ROOT/"SmartChoice365_Six_Comic_Animated_Kokoro.mp4"
 run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(paths),"-c","copy","-movflags","+faststart",str(dest)])
 assert dest.stat().st_size>100000
 print("FULL_6_SCENE_REAL_ANIMATION",dest,flush=True)
if __name__=="__main__":main()
