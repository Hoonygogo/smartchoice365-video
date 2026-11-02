# RUA EP.01 — 14.55s owner-approved upload and automatic publication

Status: **EXACT FINAL MP4 NOT YET TRANSFERRED TO GITHUB**. The user approved publishing this EP.01 video across four platforms on November 2, 2026. Do not claim public publication until receipts confirm it.

## Required original final asset
- Local / ChatGPT Library filename: `RUA_EP01_FINAL_14s.mp4`
- Library backup: `/SmartChoice365/FinalShorts/RUA_EP01_FINAL_14s.mp4` (uploaded and verified)
- Exact GitHub destination path: `uploads/RUA_EP01_FINAL_14s.mp4`
- Byte length: `3724808`
- SHA256: `672e91ea81e47226d89a8c0cff54707ced43301448308b3ac3314e976587ab3f`
- H.264 video, 720x1280, AAC audio, exact duration 14.549 seconds
- Full 10-second cartoon and official outro are **already joined**. Never append a second ending.
- Exact file decoded fully without errors in the ChatGPT environment on November 2, 2026.

## Browser upload
Direct upload UI: https://github.com/Hoonygogo/smartchoice365-video/upload/main/uploads

A single commit adding the above exact file to `main` triggers `.github/workflows/rua-ep01-robot-sock-trial-one-file-autopublish.yml`.

## Destinations and discovery
- YouTube Shorts (English): owner-approved title `My Robot Vacuum STOLE My Sock! 😂🤖 | RUA #Shorts`
- Instagram Reel and Facebook Reel, plus Instagram Story
- Related long-form YouTube video: https://www.youtube.com/watch?v=FC4FvuBPS8w
- Homepage: https://smartchoice365-web.pages.dev/
- Don't assert that the YouTube Shorts Studio "Related video" field is configured, since the official YouTube API doesn't expose this edit to our publisher.
- Publishing receipts: `publications/receipts/rua-ep01-robot-sock-trial-20261102-youtube.json` and `publications/meta-receipts/rua-ep01-robot-sock-trial-20261102-{instagram,facebook,instagram-story}.json`
- GitHub Actions published status and the actual public media URL must be verified for every channel; never invent URLs or blind-retry.

## Transfer status and limitations
The connected GitHub interface can manipulate existing Git blobs and create UTF-8 files, but cannot directly read binary bytes from a ChatGPT conversation attachment. Therefore, creating and committing the publisher workflow is not proof that the MP4 was transferred, and user action may be needed to select the original file on GitHub's upload UI. Avoid incorrectly claiming the file is already uploaded/published.
