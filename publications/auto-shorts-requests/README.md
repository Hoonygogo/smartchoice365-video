# Auto-publish Shorts without manually uploading MP4 files

## How this works

The *GitHub Actions runner itself* renders the Short and immediately sends the generated MP4 to YouTube using the channel's existing OAuth secrets. No file needs to be downloaded from ChatGPT or manually uploaded to this repository.

1. Prepare an **approved publication request** JSON file in this directory.
2. Commit it to `main`. The matching production workflow starts automatically.
3. The workflow creates video/audio using its GitHub-hosted free tools, checks 9:16 video, duration, H264/AAC, and publishes to YouTube.
4. It saves a verified receipt at `publications/receipts/<id>-youtube.json` and prevents duplicate reuploads.
5. It reports `related_video_status=STUDIO_MANUAL_ACTION_REQUIRED`. YouTube's API does not expose the clickable Shorts Related video setting.

Never substitute an alternate ChatGPT-rendered MP4 for an approved storyboard without exact-media approval. ChatGPT-local files are not magically available on a GitHub Actions runner.

### Working integration — Ninja Kokoro Shorts

Workflow: `.github/workflows/ninja-shorts-kokoro.yml`

Renderer: `experiments/render_ninja_shorts_kokoro.py`

Publisher: `maintenance/publish_shorts_from_render.py`

Auto-publish request path: `publications/auto-shorts-requests/ninja-shorts-kokoro-v2.json`

Only a request explicitly containing `approval=publish`, `privacy=public`, `visual_review_approved=true`, `render_mode=github_actions_generated`, and the exact Smart Choice 365 YouTube channel ID can publish. An otherwise successful render creates a preview artifact but does not upload to YouTube.

Example JSON template (not automatically activated):

```json
{
  "id": "ninja-shorts-kokoro-v2",
  "approval": "publish",
  "privacy": "public",
  "channel_id": "UC4DzAW-Hbd45bIECwGV7-uA",
  "render_mode": "github_actions_generated",
  "visual_review_approved": true,
  "related_video_id": "2R5Nyt42hRs",
  "language": "en",
  "contains_synthetic_media": true,
  "title": "Ninja AF141 vs AF400: One Drawer or Two? #Shorts",
  "description": "Compare which air fryer suits your kitchen. Full video: https://www.youtube.com/watch?v=2R5Nyt42hRs\n\nRead our buying guide at https://smartchoice365-web.pages.dev/guides/2026-ninja-af141-vs-af400-australia-single-dual-basket.html",
  "tags": ["Ninja AF141", "Ninja AF400", "Smart Choice 365", "Australia"]
}
```

This example must be saved as a request *only after* the actual video content is approved, to avoid publishing a second unreviewed Ninja Short. The previously approved `SmartChoice365_Ninja_Shorts_RelatedVideo_CTA.mp4` is already published separately as https://www.youtube.com/shorts/JgKqCXIvbKI. Do not republish or replace it.

### Clickable related video limitation

A plain video link in a Short's description does **not** create the clickable related-video control. The uploader cannot set it via the official YouTube API. A channel manager needs to visit YouTube Studio → Content → Shorts → [Short] → Related video → select a video from this channel → Save. Never claim this has been completed based only on the upload receipt.

### Cost and safeguards

GitHub Actions may count toward the repository's included free compute quota. Check usage and fail closed rather than enabling paid runners or paid AI APIs. Do not run recurring video production on a fixed schedule unless separately authorized.
