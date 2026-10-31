#!/usr/bin/env python3
"""Prepare eight independently sourced free-license photo candidates BEFORE video rendering.

Public Wikimedia Commons MediaWiki API, no API fee or credential. Never interpret
search results as proof of product identity or independent visual approval.
"""
import hashlib,html,json,re,time,urllib.parse,urllib.request
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'ninja-english'/'photo-candidates';OUT.mkdir(parents=True,exist_ok=True)
QUERIES=[
 ('01_kitchen','modern kitchen interior photograph'),
 ('02_cooking','home cooking ingredients kitchen photograph'),
 ('03_fries','french fries bowl photograph'),
 ('04_chicken','roasted chicken vegetables food photograph'),
 ('05_vegetables','roasted vegetables food photograph'),
 ('06_family','family meal dinner table photograph'),
 ('07_salmon','salmon food dinner plate photograph'),
 ('08_small_meal','small meal potatoes vegetables food photograph')]
UA='SmartChoice365Video/1.0 (editorial free-license photo candidate verification)'
API='https://commons.wikimedia.org/w/api.php'
def get_json(params):
    qs=urllib.parse.urlencode(params)
    req=urllib.request.Request(API+'?'+qs,headers={'User-Agent':UA})
    with urllib.request.urlopen(req,timeout=35) as res:return json.load(res)
def clean(v):return re.sub('<[^>]+>','',html.unescape(v or '')).strip()
def choose(query,used):
    data=get_json({'action':'query','generator':'search','gsrsearch':query+' filetype:bitmap','gsrnamespace':6,'gsrlimit':24,'prop':'imageinfo','iiprop':'url|size|extmetadata','iiurlwidth':2200,'format':'json'})
    candidates=[]
    for item in data.get('query',{}).get('pages',{}).values():
        inf=(item.get('imageinfo') or [None])[0]
        if not inf:continue
        url=inf.get('thumburl') or inf.get('url','')
        ext=inf.get('extmetadata') or {}
        label=clean(ext.get('LicenseShortName',{}).get('value','')).lower()
        allowed=(label in ('cc0','public domain','cc by 4.0','cc by-sa 4.0','cc by 3.0','cc by-sa 3.0','cc by 2.0','cc by-sa 2.0'))
        if not allowed or not url.lower().split('?')[0].endswith(('.jpg','.jpeg','.png','.webp')):continue
        if inf.get('width',0)<1920 or inf.get('height',0)<1050:continue
        if item['title'] in used:continue
        candidates.append((item,inf,ext,label,url))
    return sorted(candidates,key=lambda e:e[1]['width']*e[1]['height'],reverse=True)
def main():
    results=[];used=set()
    for number,(key,query) in enumerate(QUERIES):
        error=''
        try:
            candidates=choose(query,used)
            for item,inf,ext,label,url in candidates[:7]:
                try:
                    req=urllib.request.Request(url,headers={'User-Agent':UA})
                    with urllib.request.urlopen(req,timeout=45) as response:content=response.read(20_000_000)
                    from io import BytesIO
                    src=ImageOps.exif_transpose(Image.open(BytesIO(content))).convert('RGB')
                    if min(src.size)<900:continue
                    # Preserve entire photo; letterboxing prevents any crop loss.
                    base=Image.new('RGB',(1920,1080),'#172b40')
                    fit=ImageOps.contain(src,(1920,1080),Image.Resampling.LANCZOS)
                    base.paste(fit,((1920-fit.width)//2,(1080-fit.height)//2))
                    name=f'photo_{number+1:02}.jpg';file=OUT/name;base.save(file,quality=91,optimize=True)
                    used.add(item['title'])
                    result={'scene_id':key,'file':name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
                            'source_kind':'single_full_frame_photo','is_photo_led':True,
                            'width':1920,'height':1080,'provenance':inf.get('descriptionurl',''),
                            'source_title':item['title'],'license':label,
                            'attribution':clean(ext.get('Artist',{}).get('value','')),
                            'license_url':clean(ext.get('LicenseUrl',{}).get('value','')),
                            'usage_approved':False,'visual_review_passed':False,
                            'contact_sheet':False,'baked_in_storyboard_labels':False,
                            'contains_crop_loss':False}
                    results.append(result);break
                except Exception as e:error=type(e).__name__
            else:error=error or 'No freely licensed source photo usable'
        except Exception as e:error=type(e).__name__
        if not any(x['scene_id']==key for x in results):
            results.append({'scene_id':key,'error':error,'query':query,'usage_approved':False,'visual_review_passed':False})
    (OUT/'candidates.json').write_text(json.dumps({'purpose':'review_only_not_product_testing','photos':results},indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'image_candidates':sum('file'in x for x in results),'total_slots':8,'all_approved':False},indent=2))
    # Do not fail: retain partial results as downloadable artifact for inspection.
if __name__=='__main__':main()
