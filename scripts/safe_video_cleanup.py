#!/usr/bin/env python3
"""Safe cleanup for Smart Choice 365 videos.

Default is dry-run. --apply removes expendable intermediates AND unshared
AI-generated scene originals listed in cleanup_approval.json, but ONLY after
user approval and verification of a retained final MP4 SHA256.
Never removes brand marks, protected voice samples, or unlisted source images.
"""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROTECTED=('assets/','voices/reference/','config/','videos/','requests/','editorial/')
ALLOWED_DIRS=('tmp','temp','cache','intermediate','frames','renders','working')
IMAGE_SUFFIXES={'.png','.jpg','.jpeg','.webp'}
ALLOWED_SUFFIXES={'.png','.jpg','.jpeg','.webp','.wav','.pcm','.tmp','.part'}
def cleanup(workspace,apply=False):
    ws=workspace.resolve()
    if not ws.is_relative_to(ROOT.resolve()):raise ValueError('Workspace must be inside repository')
    rel=ws.relative_to(ROOT.resolve()).as_posix()
    if not rel.startswith('output/') and not rel.startswith('workspaces/'):
        raise ValueError('Only output/ or workspaces/ folders may be cleaned')
    receipt=ws/'cleanup_approval.json'
    if not receipt.exists():raise ValueError('Missing cleanup_approval.json; no cleanup')
    data=json.loads(receipt.read_text())
    if data.get('approved_for_cleanup') is not True or data.get('user_approved_final') is not True:
        raise ValueError('Final video not explicitly approved: no cleanup')
    video=ws/data.get('final_video','')
    if not video.resolve().is_relative_to(ws) or video.suffix.lower()!='.mp4' or not video.is_file():
        raise ValueError('Verified final MP4 missing')
    sha=hashlib.sha256(video.read_bytes()).hexdigest()
    if sha!=data.get('final_video_sha256'):raise ValueError('Final MP4 checksum mismatch')
    candidates=[]
    for d in ALLOWED_DIRS:
        folder=ws/d
        if not folder.is_dir():continue
        for item in folder.rglob('*'):
            if item.is_symlink():raise ValueError('Symlink in cleanup folder; refusing cleanup')
            if item.is_file() and item.suffix.lower() in ALLOWED_SUFFIXES:
                candidates.append(item)
    # Raw AI originals are opt-in per file and must be inside THIS approved workspace.\n    # Do not infer that every image in the global GitHub archive is disposable.\n    for name in data.get('disposable_ai_originals',[]):\n        item=(ws/name).resolve()\n        if not item.is_relative_to(ws) or item.suffix.lower() not in IMAGE_SUFFIXES:\n            raise ValueError('Unsafe AI original path: '+str(name))\n        if item.is_symlink():raise ValueError('Symlink AI image: refusing cleanup')\n        if item.is_file():\n            expected=data.get('disposable_image_sha256',{}).get(name)\n            if not expected or hashlib.sha256(item.read_bytes()).hexdigest()!=expected:\n                raise ValueError('Missing or incorrect original-image SHA: '+name)\n            if item not in candidates:candidates.append(item)\n    bytes_total=sum(p.stat().st_size for p in candidates)
    print(json.dumps({'mode':'DELETE' if apply else 'PREVIEW_ONLY','files':len(candidates),
                      'bytes':bytes_total,'workspace':rel,
                      'examples':[str(p.relative_to(ROOT)) for p in candidates[:25]]},ensure_ascii=False))
    if apply:
        for item in candidates:item.unlink()
        print('Deleted only eligible intermediary files. Only explicitly listed AI originals deleted; logo and voice references protected.')
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('workspace',type=Path,help='output/<video> or workspaces/<video>')
    p.add_argument('--apply',action='store_true',help='Actually delete eligible intermediates')
    a=p.parse_args();cleanup(a.workspace,a.apply)
