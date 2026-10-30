"""Place the approved guide CTA first, preserving other writable snippet metadata."""
import json
import os
from pathlib import Path
import sys
import urllib.parse
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_youtube import request_json
from publish_youtube import api,receipt_write,CHANNEL

VIDEO='FMdhtInQdPE'

def main():
    approved=json.loads(Path('publications/requests/heattech-graph-sync-ko-v5.json').read_text())
    request_metadata=approved['metadata']['snippet']
    urls=[line.split(': ',1)[-1] for line in request_metadata['description'].splitlines() if line.startswith('자세한 비교표와 구매가이드: ')]
    if len(urls)!=1:raise RuntimeError('Expected one verified guide URL')
    guide=urls[0]
    if urllib.parse.urlparse(guide).hostname!='smartchoice365-web.pages.dev':raise RuntimeError('Unexpected guide domain')
    top='👉 자세한 비교표·선택 가이드: '+guide
    payload={k:os.environ['YOUTUBE_'+k.upper()].strip() for k in ('client_id','client_secret','refresh_token')};payload['grant_type']='refresh_token'
    auth=request_json('https://oauth2.googleapis.com/token',data=urllib.parse.urlencode(payload).encode());token=auth['access_token'];print('::add-mask::'+token,flush=True)
    current=request_json('https://www.googleapis.com/youtube/v3/videos?part=snippet,status&id='+VIDEO,token=token)['items'][0]
    if current['snippet']['channelId']!=CHANNEL:raise RuntimeError('Wrong target channel')
    old=current['snippet'];description=old.get('description','')
    if description.splitlines()[0]!=top:
        body='\n'.join(line for line in description.splitlines() if guide not in line).strip()
        updated=top+'\n일반·엑스트라웜·울트라웜, 내 생활에 맞는 선택을 확인하세요.\n\n'+body
        if len(updated)>5000:raise RuntimeError('Description exceeds limit')
        snippet={k:old[k] for k in ('title','categoryId','tags','defaultLanguage','defaultAudioLanguage') if k in old}
        snippet['description']=updated
        api('https://www.googleapis.com/youtube/v3/videos?part=snippet','PUT',json.dumps({'id':VIDEO,'snippet':snippet},ensure_ascii=False).encode(),token,{'Content-Type':'application/json; charset=UTF-8'})
    verified=request_json('https://www.googleapis.com/youtube/v3/videos?part=snippet,status&id='+VIDEO,token=token)['items'][0]
    if verified['snippet']['description'].splitlines()[0]!=top:raise RuntimeError('Top guide link was not saved')
    if verified['snippet']['title']!=old['title'] or verified['status']!=current['status']:raise RuntimeError('Unexpected title or status change')
    receipt={'status':'description_updated_verified','video_id':VIDEO,'url':'https://www.youtube.com/watch?v='+VIDEO,'first_line':top,'guide_url':guide,'run_id':os.environ.get('GITHUB_RUN_ID')}
    receipt_write('publications/receipts/heattech-graph-sync-ko-v5-description.json',receipt)
    print(json.dumps(receipt,ensure_ascii=False),flush=True)
if __name__=='__main__':
    try:main()
    except (RuntimeError,KeyError,IndexError):
        print('Description update failed; inspect permissions and target metadata.',file=sys.stderr);sys.exit(1)
