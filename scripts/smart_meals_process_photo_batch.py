#!/usr/bin/env python3
"""Free-only exact recipe photography candidates. Do not publish without photo QA."""
import os,re,json,io,base64,hashlib,pathlib,urllib.request,urllib.error,sys
from html.parser import HTMLParser
from PIL import Image
MODEL="@cf/black-forest-labs/flux-2-klein-4b"
class ScriptParser(HTMLParser):
 def __init__(self): super().__init__();self.active=False;self.data=[]
 def handle_starttag(self,t,attrs):
  if t=="script" and dict(attrs).get("type")=="application/ld+json": self.active=True
 def handle_data(self,t):
  if self.active:
   try:self.data.append(json.loads(t))
   except ValueError:pass
 def handle_endtag(self,t):
  if t=="script":self.active=False
def source(slug,lang):
 url="https://smartc365.com/guides/smart-dinner-"+slug+"-"+lang
 req=urllib.request.Request(url,headers={"User-Agent":"SC365-process-photo-candidate-generator/1.0"})
 with urllib.request.urlopen(req,timeout=25) as r:html=r.read(500000).decode()
 p=ScriptParser();p.feed(html)
 for x in p.data:
  for item in (x if isinstance(x,list) else [x]):
   if item.get("@type")=="Recipe":return item
 raise ValueError("Missing published Recipe JSON-LD: "+url)
def api(prompt,width,height):
 token=os.environ["CLOUDFLARE_AI_TOKEN"];account=os.environ["CLOUDFLARE_ACCOUNT_ID"]
 boundary="----SC365Recipe"+hashlib.sha256(os.urandom(12)).hexdigest()[:16]
 body=b""
 for k,v in {"prompt":prompt,"width":width,"height":height}.items():
  body+=(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode()
 body+=(f"--{boundary}--\r\n").encode()
 req=urllib.request.Request("https://api.cloudflare.com/client/v4/accounts/"+account+"/ai/run/"+MODEL,data=body,method="POST",headers={"Authorization":"Bearer "+token,"Content-Type":"multipart/form-data; boundary="+boundary})
 try:
  with urllib.request.urlopen(req,timeout=125) as r:data=json.load(r)
 except urllib.error.HTTPError as e:raise RuntimeError("AI HTTP "+str(e.code)+", no retry, no paid fallback") from None
 b64=(data.get("result") or {}).get("image")
 if data.get("success") is not True or not isinstance(b64,str):raise RuntimeError("Missing generated image")
 raw=base64.b64decode(b64,validate=True)
 with Image.open(io.BytesIO(raw)) as img:dimensions=img.size;fmt=img.format
 if dimensions[0]<width or dimensions[1]<height:raise RuntimeError("Image below required resolution: "+str(dimensions))
 if fmt not in ("JPEG","PNG","WEBP"):raise RuntimeError("Unexpected format")
 return raw,("jpg" if fmt=="JPEG" else fmt.lower()),dimensions
def main():
 if os.environ.get("CLOUDFLARE_WORKERS_FREE_CONFIRMED")!="true":raise RuntimeError("Stop: Free AI status not confirmed")
 if not os.environ.get("CLOUDFLARE_ACCOUNT_ID") or not os.environ.get("CLOUDFLARE_AI_TOKEN"):raise RuntimeError("Stop: AI credentials unavailable")
 slug=os.getenv("RECIPE_SLUG","three-bean-lemon-parsley-salad")
 if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",slug):raise RuntimeError("Invalid selected recipe slug")
 ko=source(slug,"ko");en=source(slug,"en")
 ks,steps=ko["recipeInstructions"],en["recipeInstructions"]
 assert 3<=len(steps)<=8 and len(ks)==len(steps)
 selected_text=os.getenv("PHOTO_STEPS",", ".join(str(n) for n in range(1,len(steps)+1)))
 selected=[int(x.strip()) for x in selected_text.split(",") if x.strip()]
 if len(selected)<2 or len(selected)>7 or len(set(selected))!=len(selected) or any(x<1 or x>len(steps) for x in selected) or len(steps) not in selected:raise RuntimeError("Invalid photo stages; final stage mandatory")
 ingredients="; ".join(en["recipeIngredient"])
 method=" ".join(str(i+1)+": "+str(x["text"]) for i,x in enumerate(steps))
 if len(method)>2400:raise RuntimeError("Full method unexpectedly long")
 target=pathlib.Path("artifacts/smart-meals-process-photos")/slug;target.mkdir(parents=True,exist_ok=True)
 manifest={"dish":slug,"model":MODEL,"koTitle":ko["name"],"enTitle":en["name"],"ingredients":en["recipeIngredient"],"method":steps,"reviewed":False,"sitePublished":False,"generated":[]}
 for i,step in enumerate(steps):
  if i+1 not in selected:continue
  last=i==len(steps)-1
  prompt=("Photorealistic authentic original recipe cooking-process food photograph. "+en["name"]+". "+
   "ONLY THESE INGREDIENTS: "+ingredients+". COMPLETE METHOD CONTEXT: "+method+". "+
   "DEPICT EXACTLY STAGE "+str(i+1)+" ONLY: "+step["name"]+": "+step["text"]+". "+
   "Match the precise recipe at this stage, cut size, equipment, raw/cooked state, no unlisted extra food or garnish. "+
   ("Fully finished dish, separate editorial composition from hero, 3:2 landscape." if last else "Show the physical preparation action as close-up, square crop.")+
   " No labels, text, typography, logos, collage, fictitious tools or unrelated dishes.")
  width,height=(1536,1024) if last else (1024,1024)
  raw,fmt,sz=api(prompt,width,height)
  filename=f"step-{i+1:02d}.{fmt}"
  if (target/filename).exists():raise RuntimeError("Refuse to overwrite prior candidate")
  (target/filename).write_bytes(raw)
  manifest["generated"].append({"file":filename,"step":i+1,"size":sz,"sha256":hashlib.sha256(raw).hexdigest(),"prompt":prompt,"reviewed":False})
  (target/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
  print("IMAGE_CANDIDATE",filename,sz,flush=True)
 hero=("Photorealistic premium food-magazine HERO image, high-resolution. Finished "+
  en["name"]+". Ingredients only: "+ingredients+". Exactly plated at conclusion of: "+steps[-1]["text"]+
  ". Large appealing three-quarter 3:2 landscape composition, unlike step-final arrangement, genuine edible textures, soft daylight. "+
  "No extra garnishes, no unknown ingredients, no captions, no typography, no logo.")
 raw,fmt,sz=api(hero,1536,1024);filename="hero."+fmt
 if (target/filename).exists():raise RuntimeError("Refuse to overwrite prior hero")
 (target/filename).write_bytes(raw)
 manifest["generated"].append({"file":filename,"step":0,"role":"hero","size":sz,"sha256":hashlib.sha256(raw).hexdigest(),"prompt":hero,"reviewed":False})
 (target/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
 print("CANDIDATES_COMPLETE",len(manifest["generated"]),"AWAIT_IMAGE_QA",flush=True)
if __name__=="__main__":
 try:main()
 except Exception as e:
  print("NO_PAID_FALLBACK",type(e).__name__,str(e)[:250],file=sys.stderr);sys.exit(1)
