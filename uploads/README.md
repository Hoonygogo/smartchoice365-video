# RUA EP.00 — One-file automatic publication (owner-approved 2026-11-02)

Upload **exactly one unchanged file** through the GitHub web upload screen into the `uploads/` folder on `main`:

`SmartChoice365_RUA_EP00_20261102.mp4`

- Source: approved `main(2).mp4` 10-second original with full original audio and its existing ending. Do not attach a second outro.
- File size: **4,331,981 bytes**.
- SHA-256: `5f7f4cd01c23c2bf9f7869ac4a6850e1825e7e515e80994b975bf2689c223dcf`.
- On upload, `.github/workflows/rua-ep00-one-file-autopublish.yml` is triggered automatically, first verifying original hash and audio, then publishing YouTube Short -> Instagram Reel + Facebook Reel -> Instagram Story.
- GitHub Actions uses existing channel/Page credentials and free official APIs; success is **not** assured until API receipts confirm each destination.
- Check GitHub Actions run and `publications/receipts/` + `publications/meta-receipts/`. Receipts prevent blind duplicate uploads.
- The exact-file trigger is **only for RUA EP.00**; future shorts require their own approved metadata/hash and publishing trigger. Do not assume that arbitrary uploads auto-publish.
- There is no need to configure new YouTube/Meta credentials if the existing publishing secrets still work. Do not commit tokens.

---

# Owner-approved Ninja V4 video upload

This folder contains media pending upload to the Smart Choice 365 YouTube channel.

## Current replacement task

Upload **only the exact approved video** with this filename:

`SmartChoice365_Ninja_English_V4_Precise_StableFocus.mp4`

Verified size: 5,507,006 bytes.

Verified SHA-256:
`b0d49b9b59c7cfded99259501fbc744e85c83de319d21fa213dba0e81e4c4e51`

The workflow `.github/workflows/ninja-v4-approved-replace.yml` starts automatically on a direct `main` branch upload matching this path. It will reject any other video, confirm YouTube public processing and metadata, then delete only previous Ninja video `UJ-azoT4vso`. The old video remains untouched on any error before verification.

Do not rename or re-encode the approved MP4. Never upload drafts or transfer text chunks in its place.
