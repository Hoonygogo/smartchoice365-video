# RUA Qrevo L Pro 3-part Shorts — single-file upload release

## Naver Clip owner-confirmed status — 2026-11-08

**Owner confirmed manually published:** RUA Qrevo L Pro 37.86s Clip is already live in Naver Clip Creators and the **native Naver Shopping Connect product tag has been connected manually**. This statement is owner-provided (no official Clip API receipt was independently retrieved). Do **not** propose re-uploading/re-tagging this video or label it merely as an unpublished draft.

For future distinct clips, the GitHub Actions artifact is optional internal handoff only: give the owner a **copy-ready ChatGPT response** with the exact Clip Creators UI fields: description + hashtags, chosen existing-video cover frame, category, Naver Shopping Connect native product tag/manual checks, affiliate disclosure and optional ads/AI selections where supported. The GitHub workflow does not send ChatGPT messages itself. No confirmed automatic Naver Clip publishing API is in use.


**PUBLISHED AND VERIFIED 2026-11-08.** The owner uploaded the approved 37.855-second combined MP4, and GitHub Actions run [42458265296](https://github.com/Hoonygogo/smartchoice365-video/actions/runs/42458265296) completed successfully. All YouTube/Meta published receipts match the approved SHA-256. Naver Clip was separately manually published/tagged per the owner's confirmation; no official Clip API receipt is claimed.

## Confirmed platform destinations
- YouTube Shorts: https://www.youtube.com/shorts/KwhM7d6u2RA — `published_verified`
- Instagram Reels: https://www.instagram.com/reel/DfeNV39j5bQ/ — `published_verified`
- Facebook Reels: https://www.facebook.com/reel/1524406523069407/ — Facebook receipt `published_verified` (stored path: `/reel/1524406523069407/`)
- Instagram Story: https://www.instagram.com/stories/smartchoice365official/18100111607558637/ — `published_verified`; Stories may expire through normal Meta retention
- Naver Clip: owner confirmed manual publication with native Naver Shopping Connect product tag attached, no independent API verification

**Do not re-upload** or create duplicate publications. This workflow is a one-time upload trigger and previous approval records must be preserved.


## Upload destination

https://github.com/Hoonygogo/smartchoice365-video/upload/main/uploads

**Exact filename (do not rename):**
`RUA_Qrevo_L_Pro_3Parts_OfficialOutro_Affiliate_Ready_1080x1920.mp4`

Expected byte length: **16028684**

Expected SHA256: **6e4995d7237f417b0cf835d82236f84decb5dd04471276a36ce26efff176e645**

Full duration: **37.855333 seconds**.

Release workflow:
`.github/workflows/rua-qrevo-l-pro-3part-20261108-auto-publish.yml`

## Expected automatic tasks after owner upload

1. Preflight: validates exact approved SHA256, size, decodability, one H.264 video stream, one AAC audio stream, portrait resolution, duration and both issued affiliate URLs/disclosures in each publication request.
2. Publish **YouTube Shorts** with an approved description containing the buying guide, both issued affiliate URLs, disclosure, no separate referral fee for the buyer, and direct YouTube channel URL. Verify public receipt.
3. Publish **Instagram Reel** and **Facebook Reel** with approved caption, both issued URLs and disclosure, with platform receipts and no blind duplicate retry.
4. Share the verified Instagram Reel as a native **Instagram Story**. The Story CTA is visible inside the video. Instagram API does not insert a clickable story link sticker.
5. Package Naver Clip MP4 and Korean caption/affiliate handoff as a **GitHub Actions artifact**. **Naver Clip still requires signed-in UI upload and native Shopping Connect product tagging**. NEVER claim automatic Naver publication.

Existing earlier 20s RUA release remains separate and unchanged. This file is one-time and hash-pinned, **not** a generalized uploads folder watcher.

## Links & disclosures

- Naver Shopping Connect: https://naver.me/F05el04Z
- LinkPrice Gmarket: https://bestmore.net/click.php?m=gmarket&a=A100708938&l=9999&l_cd1=3&l_cd2=0&tu=https%3A%2F%2Fitem.gmarket.co.kr%2FItem%3FgoodsCode%3D4822243340
- Product price and seller guide: https://smartchoice365-web.pages.dev/guides/2026-roborock-qrevo-l-pro-buying-value.html
- Related Naver blog post: https://blog.naver.com/smartchoice365/224469034521
- YouTube: https://www.youtube.com/channel/UC4DzAW-Hbd45bIECwGV7-uA

Affiliate commission may be received by Smart Choice 365 when a qualifying sale occurs; **no separate affiliate commission is added to the buyer's bill**. Real buyer price is conditional on membership, card, coupon, shipping and timing. Video is a fictional 3D cartoon, not a real product demo; the robot in cartoon does not perfectly match physical Qrevo L Pro. The CTA card directs buyers to the buying guide for actual imagery/specifications.

## Verifying after upload

Open the workflow at:
https://github.com/Hoonygogo/smartchoice365-video/actions/workflows/rua-qrevo-l-pro-3part-20261108-auto-publish.yml

Inspect preflight, YouTube, Meta, Naver Clip handoff jobs separately. Do not claim a successful public post until corresponding platform receipt is `published_verified`; Naver Clip remains `manual_handoff_ready_no_auto_upload`.
