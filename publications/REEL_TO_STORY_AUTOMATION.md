# Smart Choice 365 — Instagram Reel + Story automatic cross-posting

Configured: 2026-11-01 (Australia/Brisbane).

## Core behavior

For every **new approved Instagram Reel successfully published by** `.github/workflows/meta-reels-publish.yml`:

1. The existing Reels publisher validates the approved MP4, verifies Instagram's published Reel, and records `publications/meta-receipts/<request-id>-instagram.json` as `published_verified`.
2. In the **same GitHub Actions job**, `maintenance/publish_meta_story_from_reel.py` checks that verified Reel receipt, matching SHA-256, authorized channel, and the original Reel's publishing gate.
3. It passes **the same approved video** to `maintenance/publish_meta_stories.py`, publishing a **separate native Instagram Story** using Meta's official free Graph API.
4. Its unique deterministic publication receipt `publications/meta-receipts/<request-id>-instagram-story.json` prevents a repeat when GitHub jobs are rerun.
5. It never adds link stickers (Meta's Story publishing API doesn't offer them), so CTA URLs need to be in the Instagram profile or posted via the Instagram app's manual Link sticker.

The Instagram Story expires after about 24 hours (unless the account owner adds it to a Highlight). The automatically shared Story is **a copy of the same approved MP4**, not Instagram's UI-style "share Reel into Story" object. It does not natively display a clickable Reel sticker or clickable YouTube/guide URL.

## Scope, defaults and limitations

- This auto-share happens **only** after the authorized GitHub **Instagram Reel publishing workflow** successfully verifies the post. It does **not** detect Reels posted manually in Instagram or automatically detect YouTube uploads.
- The existing `META_PUBLISH_ENABLED` and request-level approval requirements are unchanged. This feature **does not enable or broaden** unrelated auto-posting.
- Instagram must be explicitly requested in `platforms` and publishing must be enabled for that request.
- Default when the approved Reel is eligible: **auto-share as Story ON**. To opt out for a specific Reel, add `"share_to_instagram_story": false` to its `publications/meta-requests/<id>.json`. An unset flag means true.
- A Story must use the same verified H.264/AAC 9:16 MP4, and its video must fit the Instagram Story upload duration limit (3–60 seconds as currently validated).
- Use the saved `META_SYSTEM_USER_ACCESS_TOKEN` GitHub Actions secret. No tokens are committed, printed or manually requested.
- If Instagram Reel publishing is not verified, or Story publishing is uncertain, stop safely. Never blindly retry an uncertain publish call.
- The older standalone `meta-stories-publish.yml` remains available for deliberately approved Stories not linked to a Reel.
- Previously published Ninja Reel/Story on 2026-11-01 was reconciled into the auto-share receipt, **without reposting**.

## Verified

- Published Story 2026-11-01: `https://www.instagram.com/stories/smartchoice365official/18018751613745234/`
- Related verified Instagram Reel: `https://www.instagram.com/reel/DfMavk6FX72/`
- CI: `.github/workflows/meta-reel-story-ci.yml` checks code compilation and eight offline safety cases (no token and no network access).
- Do not claim that future live auto-share has posted until the next real Reel-to-Story publication is verified.

## Routine for future new Reels

1. Prepare approved MP4 and an approved `publications/meta-requests/<id>.json` with `platforms` including `instagram`.
2. Run existing Reels publishing workflow (its existing activation gate is unchanged).
3. Confirm both Instagram receipts reach `published_verified`; if Story fails, inspect the receipt and GitHub Actions log without blindly reposting.
4. Do not separately create a `publications/story-requests/` request for the same video; the Reel workflow will already upload its Story.
