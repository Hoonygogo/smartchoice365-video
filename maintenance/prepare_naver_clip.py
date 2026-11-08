#!/usr/bin/env python3
"""Prepare a Clip browser handoff from existing publication requests. Never posts."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def prepare(req, root=ROOT):
    cfg = req.get('naver_clip')
    if not cfg or not cfg.get('enabled'):
        return None
    if cfg.get('mode', 'draft') != 'draft':
        raise ValueError('Only draft preparation is enabled; public posting requires separate owner approval')
    ident = req['id']
    if not re.fullmatch(r'[a-z0-9-]+', ident):
        raise ValueError('Invalid publication id')
    sha = req['sha256']
    if not re.fullmatch(r'[a-f0-9]{64}', sha):
        raise ValueError('Exact media sha256 required')
    # Never queue previously handled media, including drafts with uncertain outcomes.
    for directory in ('publications/naver-clip-receipts', 'publications/naver-clip-queue'):
        for p in (root / directory).glob('*.json'):
            old = json.loads(p.read_text())
            if old.get('id') == ident or old.get('sha256') == sha:
                return None
    blog = cfg['blog_url']
    if not re.fullmatch(r'https://(?:m\.)?blog\.naver\.com/smartchoice365/\d+', blog):
        raise ValueError('Exact published owner blog URL required')
    if type(cfg.get('ai_used')) is not bool or type(cfg.get('advertising')) is not bool:
        raise ValueError('Explicit Clip-specific AI and advertising decisions required')
    title, body = cfg['title'].strip(), cfg['description'].strip()
    description = f'{title}\n\n{body}\n\n관련 블로그: {blog}'
    if len(description) > 3000 or not title or not body:
        raise ValueError('Description must fit the observed 3000-character field')
    if cfg['advertising'] and not cfg.get('disclosure', '').strip():
        raise ValueError('Advertising disclosure required')
    if cfg['advertising']:
        description += '\n\n' + cfg['disclosure'].strip()
    if len(description) > 3000:
        raise ValueError('Disclosure exceeds description limit')
    for key in ('category_primary', 'category_secondary', 'blog_title'):
        if not cfg.get(key):
            raise ValueError(f'{key} must be verified in the live UI')
    return dict(id=ident, sha256=sha, media_path=req.get('media_path'),
                mode='draft', privacy='private', public_publish_enabled=False,
                status='awaiting_local_browser_file_selection',
                title=title, description=description, blog_url=blog,
                blog_title=cfg['blog_title'], category_primary=cfg['category_primary'],
                category_secondary=cfg['category_secondary'], ai_used=cfg['ai_used'],
                advertising=cfg['advertising'],
                limitation='GitHub runner cannot access the signed-in local Chrome. File transfer remains manual; no Naver password/cookies exported.')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--request', required=True)
    ap.add_argument('--output', default='naver-clip-handoff')
    args = ap.parse_args()
    src = Path(args.request)
    if src.is_absolute() or '..' in src.parts or src.parts[:2] not in (
        ('publications', 'meta-requests'), ('publications', 'requests')):
        raise SystemExit('Use existing publication request directories')
    job = prepare(json.loads((ROOT / src).read_text()))
    if job:
        dest = Path(args.output)
        dest.mkdir(parents=True, exist_ok=True)
        (dest / f"{job['id']}.json").write_text(json.dumps(job, ensure_ascii=False, indent=2)+'\n')
        print('Prepared draft-only browser handoff. Nothing uploaded or published.')
    else:
        print('Not enabled or already handled; no duplicate job created.')

def enqueue_from_publication(req):
    """Optional hook shared by existing YouTube/Meta publishers; never posts Clip."""
    if not req.get('naver_clip', {}).get('enabled'):
        return
    # Uses existing GitHub receipt transport, never a Naver session or secret.
    from publish_youtube_generic import receipt_read, receipt_write
    path = f"publications/naver-clip-queue/{req['id']}.json"
    old, _ = receipt_read(path)
    if old:
        return
    job = prepare(req)
    if job:
        receipt_write(path, job)

if __name__ == '__main__':
    main()
