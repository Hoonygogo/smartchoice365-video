#!/usr/bin/env python3
"""Store generated scene images atomically in GitHub before video production.

Requires GITHUB_TOKEN with Contents: write. Example:
  python scripts/store_generated_scenes.py --topic breville-english --input /mnt/data/breville_assets_ready
This command fails closed. It does not pretend that ChatGPT image output automatically
crosses into a GitHub Actions runner: call this from an authenticated runner/runtime.
"""
import argparse,base64,hashlib,json,os,re,sys,time,urllib.error,urllib.request
from io import BytesIO
from pathlib import Path
from PIL import Image,ImageOps

REPO='Hoonygogo/smartchoice365-video'
PREFIX='videos'
def api(method,path,token,payload=None):
    req=urllib.request.Request('https://api.github.com'+path,
      data=json.dumps(payload).encode() if payload is not None else None,
      headers={'Accept':'application/vnd.github+json','Authorization':'Bearer '+token,
               'X-GitHub-Api-Version':'2022-11-28','User-Agent':'smartchoice365-scene-ingestor'},
      method=method)
    try:
      with urllib.request.urlopen(req,timeout=40) as r:return json.loads(r.read())
    except urllib.error.HTTPError as e:
      raise RuntimeError(f'GitHub API {method} {path}: HTTP {e.code}: {e.read(350).decode()}')
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--topic',required=True)
    p.add_argument('--input',required=True,type=Path)
    p.add_argument('--repo',default=REPO)
    p.add_argument('--branch',default='main')
    p.add_argument('--approved',action='store_true',help='Images were individually visually reviewed by creator.')
    args=p.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{2,60}',args.topic):p.error('invalid topic slug')
    if not re.fullmatch(r'[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+',args.repo):p.error('invalid repo')
    if not args.approved:p.error('Requires explicit --approved after reviewing EVERY scene (not a blanket auto-approval)')
    token=os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
    if not token:p.error('GITHUB_TOKEN with contents:write required')
    scenes=sorted(args.input.glob('scene_*.png'))+sorted(args.input.glob('scene_*.jpg'))
    # Sort numerically; either scene_00..11 or scene_01..12
    scenes=sorted(scenes,key=lambda p:int(p.stem.split('_')[-1]))
    if len(scenes)!=12 or [int(s.stem.split('_')[-1]) for s in scenes] not in [list(range(12)),list(range(1,13))]:
        p.error('12 uniquely ordered scenes required (scene_00..11 or scene_01..12)')
    entries=[];blobs=[]
    for idx,src in enumerate(scenes):
        raw=src.read_bytes()
        with Image.open(BytesIO(raw)) as im:
            im.verify()
        with Image.open(BytesIO(raw)) as im:
            w,h=im.size
            if w<1280 or h<720:p.error(f'Low res: {src}: {w}x{h}')
        digest=hashlib.sha256(raw).hexdigest()
        filename=f'scene_{idx:02d}{src.suffix.lower()}'
        # Require scene provenance metadata to avoid mislabeling collages as independent.
        # Metadata can be authored beside images during generation.
        info=src.with_suffix('.json')
        if not info.exists():p.error(f'Missing scene provenance metadata: {info}')
        data=json.loads(info.read_text())
        if not all(data.get(k) is True for k in ['visual_review_passed','usage_approved']):
            p.error(f'Incomplete scene approval: {src}')
        if any(data.get(k) for k in ['contact_sheet','contains_crop_loss','baked_in_storyboard_labels']):
            p.error(f'Forbidden collage/crop/labels: {src}')
        kind=data.get('source_kind')
        gen=data.get('generation_method')
        if kind not in ['single_full_frame_photo','editorial_chart'] or gen not in ['individual_ai_generated','programmatic_comparison']:
            p.error(f'Invalid provenance: {src}')
        entries.append({**data,'file':filename,'sha256':digest,'width':w,'height':h})
        blobs.append((filename,raw))
    if sum(e['source_kind']=='single_full_frame_photo' and e['generation_method']=='individual_ai_generated' for e in entries)<8:
        p.error('At least 8 independently AI-generated photo scenes needed')
    ref=api('GET',f'/repos/{args.repo}/git/ref/heads/{args.branch}',token)
    head=ref['object']['sha']
    commit=api('GET',f'/repos/{args.repo}/git/commits/{head}',token)
    oldtree=commit['tree']['sha']
    base=f'{PREFIX}/{args.topic}'
    tree=[]
    for name,raw in blobs:
        blob=api('POST',f'/repos/{args.repo}/git/blobs',token,
          {'content':base64.b64encode(raw).decode(),'encoding':'base64'})
        tree.append({'path':f'{base}/images/{name}','mode':'100644','type':'blob','sha':blob['sha']})
        print('Stored verified binary blob:',name,flush=True)
    manifest=json.dumps({'schema':1,'topic':args.topic,'assets':entries,
          'approved_by':'creator-provided scene metadata','photo_count':sum(x['source_kind']=='single_full_frame_photo' for x in entries)},
          ensure_ascii=False,indent=2).encode()
    blob=api('POST',f'/repos/{args.repo}/git/blobs',token,{'content':manifest.decode(),'encoding':'utf-8'})
    tree.append({'path':f'{base}/approved_visual_manifest.json','mode':'100644','type':'blob','sha':blob['sha']})
    newtree=api('POST',f'/repos/{args.repo}/git/trees',token,
                {'base_tree':oldtree,'tree':tree})
    newcommit=api('POST',f'/repos/{args.repo}/git/commits',token,
                  {'message':f'Archive verified AI scenes for {args.topic} before video assembly',
                   'tree':newtree['sha'],'parents':[head]})
    api('PATCH',f'/repos/{args.repo}/git/refs/heads/{args.branch}',token,
        {'sha':newcommit['sha'],'force':False})
    # Read-back verifies files are committed, not merely staged as blobs.
    verified=api('GET',f'/repos/{args.repo}/contents/{base}/approved_visual_manifest.json?ref={args.branch}',token)
    if verified['sha']!=blob['sha']:raise RuntimeError('Post-commit verification failed')
    print(json.dumps({'status':'VERIFIED_GITHUB_SAVED','sha':newcommit['sha'],
                       'images':len(blobs),'manifest':f'{base}/approved_visual_manifest.json'}))
if __name__=='__main__':main()
