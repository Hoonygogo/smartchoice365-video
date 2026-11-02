# Smart Choice 365 — Social Video Referral Rules (2026-11-02)

This is a mandatory pre-publication gate for **Facebook Reels, Instagram Reels, Instagram Stories, and YouTube Shorts**. Every published clip must help viewers discover the related long-form review and the Smart Choice 365 website. Do not invent a related video or product-specific article.

## Facebook Reels
- Put the relevant long-form YouTube video **in the first two nonblank lines**, with the real https://www.youtube.com/watch?v=… URL.
- Put the exact verified related homepage article link next, or https://smartchoice365-web.pages.dev/ when no related article exists.
- Include the direct official channel URL https://www.youtube.com/channel/UC4DzAW-Hbd45bIECwGV7-uA and a compelling, concise hook.
- Verify the **actual published description** using the Facebook video API where accessible; a successful publish status is not sufficient proof of correct caption.
- Consider a comment with links only if platform permission and explicit approval allow it. Never claim pinning unless verified.
- Don't delete or repost an already published Reel merely to fix its caption.

## Instagram Reels
- Top caption: useful hook + clear “Full review and buying guides → link in bio” instruction, even if URLs in captions are unclickable.
- Include direct YouTube long-video URL, website URL and direct YouTube channel URL in the full caption for reference; place the website and long-form link near the top.
- Verify media caption against the approved request through Graph API after publishing. Do not claim bio/profile URLs are set without checking.
- Add the actual site and YouTube destinations to Instagram profile links separately when the profile interface and permissions support it.

## Instagram Stories
- Do not assume Story media supports descriptions or Graph API link stickers. A bare video copied from a Reel has **no built-in referral overlay**.
- Prepare an *approved* Story-specific video with safe-area on-screen CTA: “Full review on YouTube • Buying guides: link in bio”. Use real website or channel handle only if legible and not misleading.
- Never change approved media without a new owner-approved export and hash; don't automatically overlay new text onto previously approved footage.
- Add native link stickers in the Instagram app only if available; Graph API publishing alone does not create clickable link stickers.
- For a Story that is already live without CTA, don't duplicate post or delete it without explicit instruction.

## YouTube Shorts
- Put related long-video link at top of description and website article link below; the Shorts player does not guarantee those URLs are clickable.
- Set YouTube Shorts **Related video** using supported Studio functionality when accessible, and verify the association. Do not represent a plain description URL as an enabled Related video.
- Include direct channel URL and avoid invented long-video/article references.

## Shared validation
1. Determine the real related long-video ID and article URL (or explicit no-related-video fallback).
2. Verify top lines / CTA presence; fail publication when mandatory metadata is missing.
3. Publish only exact SHA256-approved media to approved accounts; keep receipts and prevent duplicates.
4. Post-publish verify platform video ID/status **and actual rendered metadata** if API supports reading it.
5. Record limitations separately: Facebook video description verified/unverified, Instagram Reel caption verified/unverified, Instagram Story CTA visually verified/unverified, YouTube Related video verified/unverified.
6. Preserve A$0 tool priority; no paid subscriptions or APIs without explicit approval.

## RUA EP01 V2 audit
2026-11-02 20-second RUA robot vacuum clip was published to YouTube Shorts, Instagram Reel, Facebook Reel and Instagram Story with success receipts. Existing Reel requests contain the long-video, site and channel URLs, but they were placed after a prose hook. Facebook public rendered description was not independently retrievable in this audit; do not claim absent/present without verification. Instagram Reel publisher verifies caption equality with the request; current request lacked “link in bio”. Story media was the same approved 20-second clip with no separately authored overlay, so no Story-specific link CTA was added. Do NOT repost or delete these four published items without explicit instruction.
