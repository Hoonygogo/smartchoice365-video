# Cloudflare temporary photo handoff — A$0 pilot

Status: Worker code committed; locally tested; NOT deployed to the user's Cloudflare account yet.

Design: Cloudflare Worker + **Workers KV**, not a Git commit and not R2. Six images (~2 MB each) fit within KV Free (1 GB total, 25 MiB per value at time of writing). TTL=3600 seconds; 8 MiB max per photo. Only PNG/JPEG/WebP accepted. Every request except GET /health requires an Authorization: Bearer secret. This route has no public file listing.

## One-time account configuration (must be performed by authorized Cloudflare account holder)
1. Cloudflare dashboard > Storage & databases > Workers KV > create namespace `smartchoice365-video-temporary`.
2. Workers & Pages > Create Worker named `sc365-video-handoff`, deploy `cloudflare/image-handoff/worker.mjs` (do NOT replace the production Smart Choice 365 Pages website).
3. Worker Settings > Bindings > Workers KV namespace: binding name `ASSETS`, select `smartchoice365-video-temporary`.
4. Worker Settings > Variables and Secrets > add encrypted Secret `HANDOFF_TOKEN` with a long randomly generated value. Never send the value in chat, commit it, or put it in URLs.
5. Save/deploy. Run GET `https://<your-worker>.workers.dev/health`. Expected: `{"ok":true}`.
6. For GitHub Actions downloads, configure repository Actions secrets `IMAGE_HANDOFF_BASE_URL` (Worker HTTPS URL) and `IMAGE_HANDOFF_TOKEN` (same token). Secrets stay separate from code.
7. Uploaders must send binary bytes directly with HTTPS PUT /assets/<unique-random-id>, Authorization Bearer and correct image Content-Type; verify returned SHA256. Download from GitHub runner using GET with token, verify SHA256, then DELETE as soon as no longer needed. Never use public no-auth image URLs.
8. Worker automatically expires keys after 1 hour, but do not rely on expiry alone for prompt cleanup. Cloudflare KV expiration/replication can be eventual.

## Limitations
- ChatGPT image generation does not itself authorize binary upload to arbitrary Cloudflare endpoints. The current chat runtime still needs a separately verified tool/path that can send local photo bytes with the required bearer token.
- The small GitHub PNG commit test was NOT a test of this Cloudflare handoff.
- Worker does not auto-deploy from this file. The one-time Cloudflare dashboard setup is required unless a compatible connected deployment tool becomes available.
- Don't start six full photo generations or claim end-to-end completion before a successful *real* remote upload / download / SHA comparison / delete round-trip.
- If the Worker is not bound and secret is not set, requests fail closed (HTTP 503).
- Pilot only; no user data/public images without consent; do not publish until user approves final MP4.
