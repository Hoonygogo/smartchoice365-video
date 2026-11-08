# Ready: RUA Qrevo L Pro — Sarah/F1 full video (manual YouTube release)

**State: prepared, NOT YET PUBLIC.** The owner reviewed and approved this exact long-form Sarah/F1 narrated 16:9 version as the default style. No existing Shorts, Reels or Naver Clip are to be re-uploaded.

## Single-click YouTube publication
- **No video re-upload to GitHub is needed.** The approved binary is already in the repository:
  [GitHub stored MP4](https://github.com/Hoonygogo/smartchoice365-video/blob/main/renders/rua-qrevo-sarah-20261108/RUA_Qrevo_L_Pro_Full_Sarah_Focus_1080p.mp4).
- Open the [Sarah full-video manual workflow](https://github.com/Hoonygogo/smartchoice365-video/actions/workflows/rua-qrevo-sarah-full-20261108-youtube.yml) on the `main` branch.
- Click **Run workflow** then the green **Run workflow** confirmation. **This action is the publication trigger.** Do not manually re-upload the prior unvoiced MP4.
- The workflow runs strict SHA, size, duration, sound, voice timing, focus-target mapping, affiliate-link, Korean-language and disclosure preflight. It publishes **only** to the known YouTube channel and saves one `published_verified` receipt.
- Publication receipt: `publications/receipts/rua-qrevo-l-pro-sarah-full-20261108-youtube.json`. Do not claim successful publication until this receipt says `published_verified`; on an uncertain result, inspect rather than blindly retry.

## Approved rendered asset
- Path: `renders/rua-qrevo-sarah-20261108/RUA_Qrevo_L_Pro_Full_Sarah_Focus_1080p.mp4`
- SHA-256: `f1c0b63848a87cce8753e1d916b1358b0474e4ee10f4ac90c31fe3ce3008d844`
- 18,893,102 bytes, 4m48.304s, 1920x1080 landscape, 24 fps H.264 / AAC
- Supertonic 3 Sarah/F1 original locked voice (`ko`, speed 1.1, 8 steps); 27 individually timed Korean voice/caption/focus highlights; existing RUA cartoon start and official RUA ending
- Cue timing evidence: `renders/rua-qrevo-sarah-20261108/Sarah_Focus_Timings.json`
- Korean subtitles: `renders/rua-qrevo-sarah-20261108/Sarah_Focus_Captions.srt`
- Publisher: `maintenance/publish_rua_qrevo_sarah_full_20261108.py`
- Full curated YouTube description: `publications/requests/rua-qrevo-l-pro-sarah-full-20261108.json`

## Customer value + affiliate transparency
The YouTube description first links to:
https://smartchoice365-web.pages.dev/guides/2026-roborock-qrevo-l-pro-buying-value.html#selection-reasons

Short purchase-copy:
**고객을 위해 검토하고 엄선한 구매 링크입니다.**
- **네이버 · 엄선 구매처**: https://naver.me/F05el04Z
- **G마켓 · 카드 할인 조건부**: https://bestmore.net/click.php?m=gmarket&a=A100708938&l=9999&l_cd1=3&l_cd2=0&tu=https%3A%2F%2Fitem.gmarket.co.kr%2FItem%3FgoodsCode%3D4822243340

Include conspicuous **광고·제휴 안내** with the correct programmes and **no extra affiliate fee for the buyer**; price, shipping, eligibility and returns can change. The amounts mentioned are **2026-11-08 observations**, not guaranteed current prices or nationwide best deals. The RUA cartoon is illustrative, not a hands-on test or exact real product footage.

## After published_verified (manual Studio finishing)
1. In **YouTube Studio**, apply the already-created `RUA_Qrevo_L_Pro_Full_Thumbnail_1280x720.jpg` thumbnail, if it still matches the chosen title/video. This GitHub workflow does not set a custom image.
2. Edit the existing `https://www.youtube.com/shorts/KwhM7d6u2RA` and set **Related video** to the newly published full video. A Related video card is a way to take Shorts viewers to the clickable full-video description. This action is not performed by the GitHub workflow.
3. On the full video, check that Advanced Features for clickable external links are enabled, and ensure descriptions actually show the matching seller URLs and current conditions.
4. Check the full-video embed and links on [curated buying recommendation](https://smartchoice365-web.pages.dev/guides/2026-roborock-qrevo-l-pro-buying-value.html) and [pros/cons guide](https://smartchoice365-web.pages.dev/guides/2026-roborock-robot-vacuum-l-pro-pros-cons.html). Both now read the specific Sarah exact-public receipt and show it only after verification.
5. The homepage Korean **Full video** shelf also reads the exact Sarah release receipt for discovery.

**Deprecated:** the old 2m27s voiceless video uploader is intentionally disabled to prevent accidental wrong-version publication. No existing YouTube, Facebook, Instagram or Naver Clip post was changed, overwritten, deleted or re-published by the preparation work.
