"""Website comment and thumbnail for the explicitly approved English Buying Court upload."""
import json, os, urllib.parse
from pathlib import Path
from publish_youtube_generic import api, receipt_read, receipt_write, CHANNEL
from check_youtube import request_json

request=json.loads(Path(os.environ['PUBLICATION_REQUEST']).read_text())
assert request['id']=='robot-buying-court-en-v1' and request['approval']=='publish'
path='publications/receipts/robot-buying-court-en-v1-youtube.json'
receipt,_=receipt_read(path)
assert receipt['status']=='published_verified' and receipt['sha256']==request['sha256']
payload={key:os.environ['YOUTUBE_'+key.upper()].strip() for key in ['client_id','client_secret','refresh_token']}
payload['grant_type']='refresh_token'
token=request_json('https://oauth2.googleapis.com/token',data=urllib.parse.urlencode(payload).encode())['access_token']
print('::add-mask::'+token,flush=True)
video_id=receipt['video_id']; base='https://www.googleapis.com/youtube/v3/'
video=request_json(base+'videos?part=snippet,status&id='+video_id,token=token)['items'][0]
assert video['snippet']['channelId']==CHANNEL and video['status']['privacyStatus']=='public'
if not receipt.get('thumbnail_set'):
    try:
        result,_=api('https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId='+video_id+'&uploadType=media','POST',Path('approved-artifact/thumbnail.jpg').read_bytes(),token,{'Content-Type':'image/jpeg'})
        assert result.get('items')
        receipt['thumbnail_set']=True
    except (RuntimeError,AssertionError):
        receipt['thumbnail_status']='not_verified'
    receipt_write(path,receipt)
text=request['comment_text'];comment_id=receipt.get('comment_id')
if not comment_id:
    existing=request_json(base+'commentThreads?part=snippet&videoId='+video_id+'&maxResults=100&textFormat=plainText',token=token).get('items',[])
    for item in existing:
        top=item['snippet']['topLevelComment'];s=top['snippet']
        if s.get('authorChannelId',{}).get('value')==CHANNEL and s.get('textOriginal')==text:
            comment_id=top['id'];break
    if not comment_id:
        if receipt.get('comment_status')=='insert_initiated':
            raise RuntimeError('Earlier comment insertion uncertain; duplicate blocked.')
        receipt['comment_status']='insert_initiated';receipt_write(path,receipt)
        body={'snippet':{'videoId':video_id,'topLevelComment':{'snippet':{'textOriginal':text}}}}
        result,_=api(base+'commentThreads?part=snippet','POST',json.dumps(body,ensure_ascii=False).encode(),token,{'Content-Type':'application/json; charset=UTF-8'})
        comment_id=result['snippet']['topLevelComment']['id']
        receipt['comment_id']=comment_id;receipt_write(path,receipt)
saved=request_json(base+'comments?part=snippet&id='+urllib.parse.quote(comment_id),token=token)['items'][0]
assert saved['snippet']['textOriginal']==text
receipt.update(comment_id=comment_id,comment_status='published_verified',comment_text_verified=True,comment_pinned=False,pin_status='YouTube Data API has no supported pin operation; browser not signed in')
receipt_write(path,receipt)
print(json.dumps({'url':receipt['url'],'comment_id':comment_id,'comment_verified':True,'thumbnail_set':receipt.get('thumbnail_set',False),'pinned':False},ensure_ascii=False))
