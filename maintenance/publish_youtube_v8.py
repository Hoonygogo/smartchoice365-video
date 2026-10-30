"""Publish an explicitly approved, hash-bound artifact. Never retry an uncertain insert."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_youtube import request_json

REPO = 'Hoonygogo/smartchoice365-video'
CHANNEL = 'UC4DzAW-Hbd45bIECwGV7-uA'


def api(url, method='GET', body=None, token=None, headers=None):
    h = {'Accept': 'application/json'}
    if token:
        h['Authorization'] = 'Bearer ' + token
    h.update(headers or {})
    req = urllib.request.Request(url, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            raw = response.read()
            return (json.loads(raw) if raw else {}), response.headers
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f'API {method} failed: HTTP {exc.code}. No automatic duplicate upload attempted.') from None
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise RuntimeError(f'API {method} response uncertain. Inspect receipt before retrying.') from None


def receipt_read(path):
    url = f'https://api.github.com/repos/{REPO}/contents/{path}'
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            item = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None, None
        raise RuntimeError('Could not inspect publication receipt.') from None
    return json.loads(base64.b64decode(item['content'])), item['sha']


def receipt_write(path, value):
    _, sha = receipt_read(path)
    data = {'message': 'Record YouTube publication: ' + value['status'], 'branch': 'main',
            'content': base64.b64encode((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()).decode()}
    if sha:
        data['sha'] = sha
    api(f'https://api.github.com/repos/{REPO}/contents/{path}', 'PUT', json.dumps(data).encode(), os.environ['GH_TOKEN'], {'Content-Type': 'application/json'})


def main():
    request = json.loads(Path(os.environ['PUBLICATION_REQUEST']).read_text())
    identity = request['id']
    if not re.fullmatch(r'[a-z0-9-]+', identity):
        raise RuntimeError('Invalid publication ID.')
    if request.get('approval') != '좋아 맘에들어 교체해' or identity != 'heattech-full-photo-ko-v8' or request.get('privacy') != 'public':
        raise RuntimeError('Explicit approval and visibility are required.')
    if request['channel_id'] != CHANNEL:
        raise RuntimeError('Publication target mismatch.')
    folder = Path('approved-artifact')
    manifest = json.loads((folder / 'manifest.json').read_text())
    media = folder / 'draft.mp4'
    digest = hashlib.sha256(media.read_bytes()).hexdigest()
    if digest != request['sha256'] or manifest['sha256'] != digest or manifest['id'] != identity:
        raise RuntimeError('Artifact differs from the approved version; upload blocked.')
    if digest != '57bef2c4131e84ff9f40b1275b03f34243af9494d995bedd1cd3d9a52419c437':
        raise RuntimeError('This replacement is approved only for the reviewed v8 media.')
    metadata = request['metadata']
    if metadata['status']['privacyStatus'] != 'public' or metadata['status']['selfDeclaredMadeForKids'] is not False:
        raise RuntimeError('Unexpected publication settings.')
    if len(metadata['snippet']['title']) > 100 or len(metadata['snippet']['description']) > 5000:
        raise RuntimeError('Metadata exceeds YouTube limits.')
    payload = {key: os.environ['YOUTUBE_' + key.upper()].strip() for key in ['client_id', 'client_secret', 'refresh_token']}
    payload['grant_type'] = 'refresh_token'
    auth = request_json('https://oauth2.googleapis.com/token', data=urllib.parse.urlencode(payload).encode())
    token = auth['access_token']
    print('::add-mask::' + token, flush=True)
    channels = request_json('https://www.googleapis.com/youtube/v3/channels?part=id&mine=true', token=token)['items']
    if [item['id'] for item in channels] != [CHANNEL]:
        raise RuntimeError('OAuth channel differs from approved channel; upload blocked.')
    path = f'publications/receipts/{identity}-youtube.json'
    receipt, _ = receipt_read(path)
    if receipt:
        if receipt.get('sha256') != digest:
            raise RuntimeError('Existing receipt has a different video hash.')
        if not receipt.get('video_id'):
            raise RuntimeError('An earlier upload was initiated with an uncertain outcome. Inspect YouTube Studio; duplicate blocked.')
        video_id = receipt['video_id']
        print('Existing video found in receipt; no new upload created.', flush=True)
    else:
        receipt = {'id': identity, 'sha256': digest, 'channel_id': CHANNEL, 'status': 'upload_initiated',
                   'approval': request['approval'], 'run_id': os.environ.get('GITHUB_RUN_ID'), 'platform': 'youtube'}
        # Persist the lock before creating a remote upload; a crash cannot cause a duplicate.
        receipt_write(path, receipt)
        _, headers = api('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status', 'POST',
                         json.dumps(metadata, ensure_ascii=False).encode(), token,
                         {'Content-Type': 'application/json; charset=UTF-8', 'X-Upload-Content-Length': str(media.stat().st_size), 'X-Upload-Content-Type': 'video/mp4'})
        session = headers.get('Location', '')
        parsed = urllib.parse.urlparse(session)
        if parsed.scheme != 'https' or parsed.hostname != 'www.googleapis.com' or not parsed.path.startswith('/upload/youtube/'):
            raise RuntimeError('Unexpected resumable upload endpoint; upload blocked.')
        result, _ = api(session, 'PUT', media.read_bytes(), token, {'Content-Type': 'video/mp4'})
        video_id = result.get('id')
        if not video_id or not re.fullmatch(r'[A-Za-z0-9_-]{11}', video_id):
            raise RuntimeError('Upload returned no valid video ID. Inspect Studio before retrying.')
        receipt.update(video_id=video_id, url='https://www.youtube.com/watch?v=' + video_id, status='uploaded_processing')
        print(json.dumps({'uploaded_video_id': video_id, 'url': receipt['url']}), flush=True)
        receipt_write(path, receipt)
    # Verify privacy, channel, and processing. A timeout keeps the receipt and media for inspection.
    for attempt in range(24):
        data = request_json('https://www.googleapis.com/youtube/v3/videos?part=status,processingDetails,snippet&id=' + video_id, token=token)
        items = data.get('items', [])
        if items:
            video = items[0]
            status = video['status']
            if video['snippet']['channelId'] != CHANNEL:
                raise RuntimeError('Uploaded video channel mismatch.')
            processing = video.get('processingDetails', {}).get('processingStatus')
            upload_status = status.get('uploadStatus')
            receipt.update(privacy=status.get('privacyStatus'), upload_status=upload_status, processing_status=processing)
            if upload_status in ('failed', 'rejected', 'deleted') or processing in ('failed', 'terminated'):
                receipt['status'] = 'processing_failed'
                receipt_write(path, receipt)
                raise RuntimeError('YouTube processing failed or rejected the upload; media retained.')
            if upload_status == 'processed' and processing == 'succeeded' and status.get('privacyStatus') == 'public':
                saved = video['snippet']
                if saved.get('title') != metadata['snippet']['title'] or saved.get('description') != metadata['snippet']['description']:
                    raise RuntimeError('Saved public metadata differs from the approved description; old video retained.')
                receipt['metadata_verified'] = True
                receipt['description_first_line'] = saved['description'].splitlines()[0]
                receipt['source_run_id'] = request['source_run_id']
                receipt['status'] = 'published_verified'
                receipt_write(path, receipt)
                print(json.dumps(receipt, ensure_ascii=False), flush=True)
                old_id = request.get('delete_old_video_id')
                if old_id:
                    if old_id != 'FMdhtInQdPE' or old_id == video_id:
                        raise RuntimeError('Unexpected old video deletion target.')
                    previous = request_json('https://www.googleapis.com/youtube/v3/videos?part=snippet&id=' + old_id, token=token).get('items', [])
                    if not previous:
                        receipt['old_video_cleanup'] = {'video_id':old_id,'status':'already_absent'}
                    elif previous[0]['snippet']['channelId'] != CHANNEL:
                        raise RuntimeError('Old video channel mismatch; deletion blocked.')
                    else:
                        try:
                            api('https://www.googleapis.com/youtube/v3/videos?id=' + old_id, 'DELETE', token=token)
                            remaining = request_json('https://www.googleapis.com/youtube/v3/videos?part=id&id=' + old_id, token=token).get('items', [])
                            receipt['old_video_cleanup'] = {'video_id':old_id,'status':'deleted_verified' if not remaining else 'deletion_not_verified'}
                        except RuntimeError as exc:
                            receipt['old_video_cleanup'] = {'video_id':old_id,'status':'blocked','reason':str(exc)}
                    receipt_write(path, receipt)
                    print(json.dumps({'old_video_cleanup':receipt['old_video_cleanup']}),flush=True)
                summary = os.environ.get('GITHUB_STEP_SUMMARY')
                if summary:
                    with open(summary, 'a') as out:
                        out.write('Published and verified: ' + receipt['url'] + '\n')
                return
        time.sleep(10)
    receipt['status'] = 'awaiting_processing_verification'
    receipt_write(path, receipt)
    raise RuntimeError('Upload saved, but public processing is not yet verified. Do not upload a duplicate.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, KeyError, OSError) as exc:
        # Fixed diagnostic only: never include raw Google responses or tokens.
        print(str(exc) if isinstance(exc, RuntimeError) else 'Publication configuration or file error.', file=sys.stderr)
        sys.exit(1)
