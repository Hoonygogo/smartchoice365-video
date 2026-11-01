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
