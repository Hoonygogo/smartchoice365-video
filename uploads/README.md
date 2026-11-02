# RUA English Introduction — approved 10-second release (2026-11-02)

The user-approved original from this conversation is ready for the **existing free GitHub Actions -> YouTube + Meta publishing system**. The binary MP4 has not yet been transferred into this GitHub repository.

**Direct browser upload UI:** https://github.com/Hoonygogo/smartchoice365-video/upload/main/uploads

Upload exactly this unmodified MP4 to the `uploads/` directory on the `main` branch:

`SmartChoice365_RUA_English_Intro_20261102.mp4`

- Bytes: **3,337,041**
- SHA-256: `4ae6b12be58f717d00115d3312768efe5202a69fb100f627a734a5184aab4c6a`
- Duration: 10.026667 seconds, 720×1280 portrait, H.264 video with original AAC audio
- Official RUA wardrobe, voice, ending and soundtrack must not be changed in this publishing step
- **Automatic trigger:** `.github/workflows/rua-english-intro-one-file-autopublish.yml` on matching file push
- Planned destinations: Smart Choice 365 YouTube Shorts, Instagram Reel, Facebook Reel, then Instagram Story
- Planned captions: English, linking Smart Choice 365 home and official YouTube channel, with original outro already in the MP4; never append a second outro
- All four publish statuses must be verified from receipts; an Actions run starting is **not** proof of publication
- Keep earlier Korean RUA EP00 publication unchanged. No deletions and no blind duplicate uploads.

---

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
