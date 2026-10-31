# Korean/English YouTube publish pipeline — persistent operating rule

## Reuse the proven Korean architecture
1. Build a complete 1920×1080 H.264/AAC MP4 INSIDE a GitHub Actions workflow or upload the exact user-approved MP4 into an Actions artifact. Never confuse a ChatGPT sandbox file with a GitHub artifact.
2. Save draft.mp4 and manifest.json in the same named GitHub Actions artifact using actions/upload-artifact@v4. Manifest must contain real SHA256, source_run_id and truthful QA flags.
3. Generate an English publication request in publications/requests with the exact video SHA256, artifact source run, approved metadata, Smart Choice 365 channel UC4DzAW-Hbd45bIECwGV7-uA, and related guide URL as the first description line.
4. Use .github/workflows/youtube-publish-generic.yml and maintenance/publish_youtube_generic.py to download that exact artifact, validate ownership, and upload using existing repository YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN secrets. Do NOT reconnect OAuth merely because a second language is being published.
5. Store and check the YouTube receipt (video ID and processing status) before asserting successful publication. Never retry when an earlier upload outcome is uncertain.

## Explicit existing-video approval and artifact caveat
On 2026-10-31, the owner explicitly instructed publication of the existing English Ninja AF141 vs AF400 2m13s draft, despite its acknowledged visual imperfections. Do not silently substitute a different generated render, claim that artifact is missing when it only exists in the ChatGPT sandbox, or fake quality_verified=true. The exact file in chat was Ninja_AF141_AF400_English_New_NativeScenes.mp4. This sandbox file is NOT automatically a GitHub Actions artifact, and the GitHub connector currently does not provide a binary-artifact upload action.

## Subsequent videos
Continue to apply VIDEO_EDITORIAL_POLICY.md: 12 scene-specific 1920×1080 compositions, ≥8 picture-led scenes, no collages or cropped contact sheets, spoken-target focus, and unobtrusive 'Illustrative image for reference' caption. For an older explicitly accepted draft, track the quality exception accurately rather than pretending to meet the stricter newer standard.
