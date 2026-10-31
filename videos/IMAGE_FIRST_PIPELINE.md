# Smart Choice 365 — video scene and storage policy (approved 2026-10-31)

## Default 2–3 minute video: 12 scenes
- **6 independently generated high-quality AI photographs** for product, lifestyle and usage scenarios.
- **6 Python-generated editorial scenes** for brand intro/outro, validated price bar charts, comparison tables, cost calculations and recommendations.
- Counts are a **default, not a hard rule**; optimize per topic, duration and clarity. For 60 seconds use ~3–4 photos; for 4–5 minutes use ~8–10.
- One image can have natural Ken Burns/pan/zoom animation without losing important product details. Sync captions and highlights to narration.
- **Mandatory synchronized focus indicator on both AI photos and Python charts:** draw a clearly visible non-obscuring focus box/outline, callout or soft spotlight around the exact visually grounded feature being narrated. Move it smoothly at the matching spoken word/phrase onset using time-aligned narration cues; hold it for the spoken passage, then transition to the next target. Validate timings against the final synthesized voice audio (not estimated fixed durations). For a photo, annotate only visually identifiable objects; when the specific object cannot be confidently located, use a safe whole-product highlight or no inaccurate box. Keep subjects/text unobstructed and preserve the original photo. Include a timing/visual verification pass before approval.
- Charts must accurately represent verified source values and include appropriate unit/currency/date context. Never pretend AI illustrations are real photos of tested products.
- Preserve original uncropped brand logo, authorized Sarah (KR) and Kokoro af_heart (EN) reference voice files; verify audio, iPhone-playable final MP4, then ask for explicit approval before publication.

## Zero-cost storage rule
- Do **not** Git-commit production AI photos, temporary scene renders, intermediates, or preview video files to main/history merely to move them between stages.
- Use runner temporary workspace for files needed during a job. For cross-job transfer use short-lived Actions artifacts (aim 1–2 days), subject to actual platform limits and working transfer mechanism.
- The exact image handoff from ChatGPT to the runner is **not yet implemented**: do not claim automated image uploading or end-to-end video creation works until verified.
- Once user approves and safely retains the final MP4, cleanup disposables and expired artifacts. Keep code, official logo, production rules, and protected voice references.
- A regular Git deletion does **not** remove old blobs from historical commits or necessarily reclaim repository storage. Do not rewrite Git history without separate explicit authorization and backup.
- The legacy `scripts/store_generated_scenes.py` Git-history uploader is not an approved storage strategy for new production assets.

## Always-on focus tracking (mandatory)
- **Default: use a focus box/outline/spotlight as much as visually meaningful, in BOTH AI-photo and Python-graphic scenes.** Do not limit this feature to the six charts.
- **Voice-following is mandatory, not optional:** focus must track the exact item or concept being spoken at the corresponding actual audio timestamp. Build cues from final synthesized narration and validate with playback; do not use arbitrary equal-duration animation.
- At every narration transition, smoothly move/resize the highlight to the newly discussed object, number, graph bar, comparison item or recommendation. Hold through the spoken clause and transition naturally.
- For whole-scene narration, deliberately use a whole-subject emphasis or a relevant focus region, never an arbitrary/distracting rectangle. If a target cannot be verified in an AI illustration, avoid a misleading precise annotation.
- Ensure the box never hides numbers, subtitles, product details, or branded elements. Use contrast, a clear border and mild glow without clutter.
- The video should fail visual QA if highlights lag narration, jump incorrectly, refer to nonexistent features, or are omitted from scenes where a meaningful target exists.

## Mandatory preflight and generation gate (2026-10-31)
1. **Before generating any photos:** verify the chosen execution environment can actually run Kokoro af_heart 0.96, synthesize a new sentence, inspect a non-silent WAV, run ffmpeg, and transfer photo bytes into the SAME render job **without committing them to Git history**. If the image handoff is unavailable, STOP and report the blocker. Do not generate images hoping to work around it.
2. **Generate EXACTLY one independent photographic scene per image-generation invocation.** Prompts must explicitly request: single full-frame photograph, one camera viewpoint, no storyboard, no split screen, no collage, no comparison panels, no text, no logos, no titles, no captions, no icons, no graphic overlays or YouTube thumbnail. Each of the six images gets its own distinct composition. Never ask image generation for a whole video, scene collection, infographic or storyboard.
3. Visually review each generated result individually before acceptance. The structural validator verifies file count, dimensions, hashes and manifest; **it cannot automatically prove that an image is not a collage or that its product details are correct**. Human/vision review must truthfully set the manifest fields; do not fabricate passes.
4. Reject faulty assets locally; never upload failed images to the repository, artifacts or user's final delivery. No silent crop of a large collage into six alleged originals.
5. Audio-first render: generate the approved voice for the exact production script and verify audio; derive time-coded focus targets from that audio. If exact word-level alignment isn't implemented, report clause-level timing honestly, not as word-level synchronization.
6. Deliver video only after verified photo provenance, sound, focus tracking, 1080p, mobile-compatible encoding and playback. Never substitute a visual-only preview without explicit user request.
7. Do not claim a code commit or GitHub workflow change proves the system successfully rendered. Require a **successful end-to-end run** and a verifiable MP4.
