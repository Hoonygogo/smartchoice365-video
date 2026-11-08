# Naver Clip: tested draft bridge (2026-11-08)

Observed on Smart Choice365's signed-in Chrome. Test draft https://clipcreators.naver.com/web/draft/1639413 was saved and reopened: description/title first line, category 테크 / 인터넷, AI, AI switch on, attached real Roborock blog, public switch off. Existing public RUA unchanged. A second unnamed test draft was also visible; no deletion performed.

## What is and is not automatic
- Manual local file selection succeeded. Automatic setFiles from the remote workspace failed twice with Naver's upload error; no root cause proved. Do not advertise unattended uploading.
- After local file selection, Browser can fill metadata, attach a verified owner blog and save a draft. This UI has one 설명 field (3000 chars), no separate title field. AI policy is Clip-specific: do not copy YouTube's cartoon exemption. Review actual material.
- GitHub Actions cannot control the owner's logged-in Chrome. No Naver credentials/cookies/session are exported. No undocumented Naver endpoints, remote debugging, paid tools or background browser login.

## Existing publisher integration
Existing maintenance/publish_youtube_generic.py and maintenance/publish_meta_reels.py call enqueue_from_publication only when a request explicitly has naver_clip.enabled=true. prepare_naver_clip.py creates a hash-bound draft-only queue file via existing GitHub receipt transport. Existing requests without this field behave as before. It does not alter YT/Meta approval or republish old media. Failure is explicit; inspect receipts before retries.

Add to a NEW intended vertical product request (not historical RUA requests):

    "naver_clip": {
      "enabled": true,
      "mode": "draft",
      "title": "Verified Korean title",
      "description": "Useful caption and real related links",
      "category_primary": "테크",
      "category_secondary": "인터넷, AI",
      "ai_used": true,
      "advertising": true,
      "disclosure": "이 포스팅은 네이버 쇼핑 커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다.",
      "blog_url": "https://blog.naver.com/smartchoice365/224469034521",
      "blog_title": "로보락 로봇청소기 추천｜Qrevo L Pro, 50만원대면 충분할까?"
    }

Use the genuinely matching live blog for each video; the Roborock URL above is not a universal default. Advertising clips need the UI advertising switch plus appropriate programme disclosure and issued links. Shopping Connect product-tag UI has not been tested here.

Manual workflow naver-clip-handoff.yml can prepare the same metadata as an Actions artifact without publishing anything. Default disabled; never auto-enable old requests. Full horizontal videos are not automatically resized here; use approved vertical delivery assets only and check their actual hash/format before attaching.

## Browser execution
1. Read connected-browser documentation; inspect signed-in account and existing Clip rows. Check all local/remote queue and Clip receipts for matching id/hash. If an ambiguous draft already exists, inspect/resume it rather than upload again.
2. Select exact new media on the user's machine, checking expected hash by available authorized file methods. Current file transfer is manual. Do not use old RUA for a test.
3. Adapt maintenance/naver_clip_browser_draft.mjs through the supported Browser tool with fresh DOM snapshots; it is an adapter, not a standalone headless publisher. Fill metadata and keep public switch off. For the blog picker inspect title and URL, scope the correct row, choose it; never blindly first().
4. Select a cover, verify all fields, then saveDraft. Require saved confirmation AND reopen the draft row to verify persistence/category/AI/blog/private. Capture screenshot. Write publications/naver-clip-receipts/<id>.json with exact hash, stage draft_saved_verified and draft URL. Do not mark uploaded/public merely from a click.
5. PUBLIC POSTING IS NOT IMPLEMENTED/ENABLED. Owner must approve the concrete final media and metadata before any future public operation. No registration button is clicked by this bridge.

Tests: python -m unittest discover -s tests -p 'test_naver_clip_handoff.py' -v. Tested public-mode rejection, duplicate media prevention, explicit AI/limits and private-only output. Real local-file upload remains a limitation.
