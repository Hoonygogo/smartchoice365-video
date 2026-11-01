# Smart Choice 365 — Instagram Reels + Facebook Reels automated publishing

## Current status — 2026-11-01

- **Code and workflow prepared. Not yet account-connected; no posts made to Meta.**
- Official Meta API via a **single Facebook Page access token** + Instagram professional account linked to that Page.
- Graph API **v26.0**. No paid APIs, paid AI credits, or paid scheduling subscription.
- YouTube remains unaffected; already published original 12-second Ninja recut:
  https://www.youtube.com/shorts/8OX29Fx2axc
- Matching full comparison:
  https://www.youtube.com/watch?v=2R5Nyt42hRs
- Prepared test request (NOT authorized for publication):
  `publications/meta-requests/ninja-rewind-recut-meta-20261101.json`
- Publisher: `maintenance/publish_meta_reels.py`
- Workflow: `.github/workflows/meta-reels-publish.yml`
- When approved, each platform publishes once and maintains a separate receipt at
  `publications/meta-receipts/<id>-instagram.json` or `<id>-facebook.json`.

### Account owner — one-time connection only

1. Open https://business.facebook.com/ and ensure a real **Smart Choice 365 Facebook Page** exists (not a personal Facebook profile) and you have full Page control/CREATE_CONTENT rights.
2. Convert the Smart Choice 365 Instagram profile to **Professional** (Business or Creator) and link it to that same Facebook Page in Meta Account settings.
3. Open https://developers.facebook.com/apps/ . **Reuse the existing Smart Choice 365 Meta app if available**, adding the correct Instagram Graph API / Facebook Page publishing use case. Site Facebook sign-in email/public_profile permissions alone cannot publish Reels.
4. Request official Facebook Login/Page permissions:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `instagram_basic`
   - `instagram_content_publish`
   Meta may require business verification/App Review/Advanced Access depending on the app configuration and accounts. Own/admin-managed app roles can sometimes be used in development mode; do not assume access until the preflight checks succeed.
5. Use Meta Graph API Explorer https://developers.facebook.com/tools/explorer/ with your app to authorize those permissions and choose the Smart Choice 365 Page. **Obtain a Page access token** (not the user token). Consider renewing/maintaining long-lived access as required by Meta; do not assume all Page tokens are permanent.
6. Find the Page ID and linked Instagram professional ID with Graph API (replace token locally, never in chat/repository):
   `GET /v26.0/me/accounts?fields=name,id,access_token,instagram_business_account`
   or
   `GET /v26.0/{page-id}?fields=name,id,instagram_business_account`
   Verify the selected Page belongs to Smart Choice 365.
7. In private GitHub repository settings https://github.com/Hoonygogo/smartchoice365-video/settings/secrets/actions add an **Actions secret**:
   - `META_PAGE_ACCESS_TOKEN` = Page token only.
   Do **not** paste token values into ChatGPT, a public GitHub issue, a commit, or this README.
8. In https://github.com/Hoonygogo/smartchoice365-video/settings/variables/actions add repository **variables**:
   - `META_FACEBOOK_PAGE_ID` = numeric Facebook Page ID
   - `META_INSTAGRAM_ACCOUNT_ID` = linked numeric Instagram professional ID
   - `META_PUBLISH_ENABLED` = `false` initially
9. With `META_PUBLISH_ENABLED=false`, use Actions → Smart Choice 365 — Instagram and Facebook Reels (free API) → Run workflow and input:
   `publications/meta-requests/ninja-rewind-recut-meta-20261101.json`
   This performs **media and public URL validation without making a Meta post**.
10. After the owner explicitly approves the Ninja cross-post, change its request `approval` from `prepare` to `publish` and change `META_PUBLISH_ENABLED` to `true`. A commit changing the approved request triggers automatic posting to IG and FB.
    - The exact MP4 is served by the public GitHub repository at a commit-pinned HTTPS URL. **No manual MP4 upload required** for a video already present in GitHub.
    - If credentials, professional account connection, video validation, or target account checks fail, no post is attempted.
    - The implementation prevents **blind retries** after uncertain API publish outcomes to avoid duplicates.

### Reels publishing flow

Instagram professional: upload a publicly fetchable 9:16 MP4 with `POST /{ig-id}/media` `media_type=REELS` and `video_url` → poll `status_code=FINISHED` → `POST /{ig-id}/media_publish` → confirm media ID, caption and permalink.

Facebook Page: `POST /{page-id}/video_reels` (`upload_phase=start`) → POST hosted `file_url` to returned `rupload.facebook.com` endpoint → `upload_phase=finish`/`PUBLISHED` → poll video processing status.

### Source & safety

- Reuse only uploaded MP4 with approved SHA-256 and 9:16 H.264/AAC, duration 4–60s in this shared workflow, matching Facebook Page Reels documented requirement.
- Exact user-approved topic and platform-specific captions, no invented product claims or discounts.
- Meta may cache/fetch source URLs asynchronously. Keep them publicly accessible through processing (the public GitHub source remains available).
- Instagram captions generally do **not** offer clickable external URLs, so also place the homepage in the profile bio/website field. Facebook caption can carry a direct article link.
- No automatic paid hosting or unlimited quota claims. GitHub Actions public repository and Meta API have usage/permission limits; stop on error.
- No repeat publishing on uncertainty. Verify per-platform receipts before claiming success.
- When the next video is rendered inside GitHub Actions, call the reusable workflow with an approved request; the MP4 never needs to leave GitHub.
- These scripts do **not** alter YouTube uploads and **do not** post to personal Facebook timelines.

Official resources:
- https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api
- https://www.postman.com/meta/facebook/documentation/r56bjfd/facebook-api
- https://developers.facebook.com/docs/instagram-platform/content-publishing/
- https://developers.facebook.com/docs/graph-api/

