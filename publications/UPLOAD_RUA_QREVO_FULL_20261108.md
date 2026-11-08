# RUA Qrevo L Pro — 16:9 YouTube full buying guide, one-file upload

**PREPARED, NOT PUBLISHED.** The owner must review the full `MP4` and explicitly upload it to the repository to authorize new long-form publishing. The earlier 37.86-second Shorts, Instagram Reels, Facebook Reels, Instagram Story and owner-published Naver Clip remain unchanged and must NOT be duplicated.

## Exact upload

1. Download the ChatGPT deliverable named `RUA_Qrevo_L_Pro_Full_Buying_Guide_1080p.mp4` (do not rename).
2. Go to https://github.com/Hoonygogo/smartchoice365-video/upload/main/uploads
3. Upload ONLY the full MP4 to `uploads/` on the `main` branch and commit.

File expected size: **14,587,506 bytes**

SHA-256: `2fc8b5ce5d9294b4746437973e5732eec0ef8985e0ed81a1edc232ac8731b3dc`

Duration **146.743 sec (2m26.7s)**, landscape **1920×1080, 24 FPS, H264 video + AAC stereo**.

Triggered GitHub Actions workflow:

https://github.com/Hoonygogo/smartchoice365-video/actions/workflows/rua-qrevo-l-pro-full-20261108-youtube.yml

Only if exact file validation passes, the workflow publishes on the authorized **YouTube channel** and writes one-time `published_verified` receipt: `publications/receipts/rua-qrevo-l-pro-full-20261108-youtube.json`.

YouTube metadata includes **both exact-product officially issued affiliate links** and program disclosure above the video chapters:

- Curated seller research: https://smartchoice365-web.pages.dev/guides/2026-roborock-qrevo-l-pro-buying-value.html#selection-reasons
- Naver Shopping Connect: https://naver.me/F05el04Z
- LinkPrice Gmarket (card-conditioned alternative): https://bestmore.net/click.php?m=gmarket&a=A100708938&l=9999&l_cd1=3&l_cd2=0&tu=https%3A%2F%2Fitem.gmarket.co.kr%2FItem%3FgoodsCode%3D4822243340

All price, reward, warranty, source and model information is **dated 2026-11-08**, may change at checkout, and is not a nationwide lowest-price guarantee. The animated robot is not actual product testing, and the schematic graphic is not an official product photograph. Video is text-led Korean editorial; it does not have new narrated Korean voiceover. The original RUA story and official V2 outro retain their source audio.

## After YouTube verifies publication

1. The Roborock curated-buying and pros-and-cons website guides have been configured to prioritize the **new 16:9 full video embed** when its exact approved YouTube receipt is publicly available, while preserving Shorts and other links.
2. The existing homepage video gallery reads verified public video index/YouTube feed and should classify this as **Korean / Full video** once the index has refreshed; check public UI.
3. Upload the provided `RUA_Qrevo_L_Pro_Full_Thumbnail_1280x720.jpg` as a **custom thumbnail** through YouTube Studio (the one-file GitHub workflow does not upload the thumbnail).
4. Edit the existing Short `https://www.youtube.com/shorts/KwhM7d6u2RA` in **YouTube Studio** to attach its new **Related video** (the full watch URL). This is a clickable Short-to-long transition. YouTube Shorts description URLs are not clickable.
5. Long-form descriptions have clickable external links only if the channel has **Advanced Features** enabled in YouTube Studio > Settings > Channel > Feature eligibility. The workflow cannot independently assert the account eligibility.
6. No Instagram/Facebook/Naver main-video upload is attempted: 16:9 video would not follow their established portrait/Reel workflow.

## Duplicate safety

The workflow is triggered solely by `uploads/RUA_Qrevo_L_Pro_Full_Buying_Guide_1080p.mp4` pushed to `main`. It checks byte size, SHA-256, 16:9, 24 FPS, duration, decoder output, both issuer links and conspicuous disclosure. On an ambiguous YouTube outcome, the receipt blocks blind duplicate insertion.
