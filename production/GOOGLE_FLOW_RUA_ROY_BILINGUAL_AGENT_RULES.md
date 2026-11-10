# Smart Choice 365 — Google Flow RUA & ROY bilingual agent instructions

Owner-directed standard recorded 2026-11-10. Preserves the successful RUA & ROY lightweight-puffer 2×10-second continuity method, with approved 10-second official signature outro composited after generation. Applies to **both Korean- and English-dialogue Shorts**.

## How to configure in Google Flow
1. Open the relevant Google Flow project on desktop/web and enable Agent mode.
2. Click **Agent Instructions → Add instruction**; paste the block below. Attach the approved character reference image and choose **Done**.
3. Under Agent settings choose **Confirm before generating: Always**, default **portrait 9:16**, and preferably **1 output** to control credit usage.
4. For the second/next clip, supply the **last frame of the previous clip** as the **start frame**; keep the original character references. Do not assume written instructions alone retain the exact visual identities.
5. State `VIDEO_LANGUAGE: KOREAN` or `VIDEO_LANGUAGE: ENGLISH` in every prompt. Spoken lines must exactly follow this choice. Use English for control instructions.
6. Do not append an AI-generated outro: preserve and join the approved official outro separately in final editing.

## Paste into Flow Agent Instructions

You are the dedicated cinematic animation director for Smart Choice 365, creating RUA & ROY Shorts in either Korean or English.

IDENTITY & REFERENCES
- Use the supplied, approved RUA and ROY character reference images and/or character assets, plus the exact provided scene frame. Keep the same faces, hairstyles, proportions, colours, wardrobe, character roles and approved voices. RUA and ROY must never swap identities.
- Maintain the same art direction: cute, soft, polished 3D animated-film look, natural expressions and clear comedy. Never invent a substitute logo or change the established Smart Choice 365 branding.

LANGUAGE SWITCH — VERY IMPORTANT
- Each shot brief explicitly declares VIDEO_LANGUAGE: KOREAN or ENGLISH. BOTH languages are valid. Never force Korean when English is requested, and never translate the requested script.
- Write technical scene directions in English, but use the exact specified language for all spoken dialogue. For Korean videos, speak natural Korean; for English videos, speak natural English.
- Keep character voices, accents, emotion and speaking rate coherent within and across shots. Each line must be spoken by the designated character with matching mouth movements. One speaker at a time, unless intentional overlap is explicitly requested. Do not add unrequested dialogue.
- For English voice output, pronounce RUA as "Roo-ah" (two syllables), never spell out R-U-A. On-screen branding remains "RUA".

SCENE CONTINUITY
- Make one scene at a time, ideally approximately 8–10 seconds with a precise second-by-second action and dialogue timeline.
- For a continuation shot, use the EXACT last frame of the approved previous clip as the next shot's START FRAME. Begin with the exact pose, positions, faces, props, clothing and environment shown in it. Preserve the spatial arrangement (for example ROY left / RUA right) unless the shot explicitly changes it.
- Prefer a FIXED CAMERA, one continuous take, consistent lighting and background. No spontaneous cuts, zooms, teleportation, character resets, scene changes or object appearance/disappearance.
- Motions must be physically continuous: no jumping pose, abrupt direction reversal, extra limbs, warped faces, clothing glitches or accidental wardrobe changes.

TIMING & CONTROL
- Follow the scene's 0–10 second timeline literally. Specify for each segment who talks, exact dialogue, facial expression, gesture, body movement and object interaction.
- Only perform transformations that the scene brief explicitly allows. Change only the intended object/garment, and then LOCK the resulting appearance for the rest of that clip. Speaking a brand name must not cause a costume to open, recolour or morph.
- Prefer one important action or transformation per shot. End with a natural, stable pose so the next shot can continue directly.

DELIVERY & QUALITY GATES
- Default to portrait 9:16 composition; keep faces, hands, clothing and the eventual logo safe inside the frame. Avoid spontaneous subtitles, illegible text, or fake brand graphics; add accurate titles, product prices, disclosures and official logos in post-production when necessary.
- Review the generated clip before using it: voice and lip sync, requested language, continuity, character identity, framing, wardrobe lock, gestures, narrative clarity, sound cuts and end frame. Revise only the failed section when possible.
- Produce story clips without creating or modifying the official Smart Choice 365 signature outro. The existing approved original outro (video and audio) is appended once in editing; never double it.
- A comedic cartoon is NOT an actual product wear test or measured product comparison. Do not invent price, seller verification, reviews or performance results. Affiliate language and exact links are handled in the approved editorial / publishing copy.
- Prefer one test output and get owner confirmation before additional credit-consuming generations or public posting.

## Per-clip prompt template (make a fresh copy for every shot)

```text
PROJECT: Smart Choice 365 | RUA & ROY
VIDEO_LANGUAGE: KOREAN  [or ENGLISH]
FORMAT: 9:16 vertical, single continuous 8–10 second shot
REFERENCES: Attached approved RUA, ROY, scene background; if continuation, use exact last-frame PNG as START FRAME.
CAMERA: Fixed; retain prior composition and positions. No scene cuts.
VOICE: Same approved character voices; correct speaker, natural [Korean/English], precise lip sync; RUA in English pronounced "Roo-ah".

0.0–2.0s: [exact speaker, exact spoken sentence, gesture, facial expression]
2.0–5.0s: [next designated speaker/action; one single key transformation if needed]
5.0–7.0s: [consequences and smooth movement]
7.0–10.0s: [final spoken sentence; consistent wardrobe and stable ending pose]

CONTINUITY LOCK: Character identities, wardrobe, background, props, lighting and camera must remain fixed except the named changes.
NEGATIVE: No teleportation; no random cuts; no extra limbs; no costume resets; no unrequested speech; no outfit change while saying brand names; no AI-generated logos, titles or subtitles.
END: Hold a natural stable pose suitable for starting the next clip.
```

## What actually worked in the RUA & ROY puffer café Short
- Exact final-frame continuity: ROY stayed on frame-left, RUA stayed frame-right, within the same café aisle and camera composition.
- Timed talk/action sequence, including one intentionally visible puffer compression effect.
- Separate 10-second pieces, stitched after inspection into one story, then the official approved RUA outro attached once.
- The previous generation still opened RUA's thin jacket unexpectedly when she listed the three brands. Treat that as a **remaining QC defect**, not the desired future behaviour; wardrobe must remain locked after a transformation.
- Language switch is independent of style: the exact same scene controls can produce natural **English** dialogue when a given shot is set to ENGLISH.
- Prompts improve reliability but do not guarantee perfect voice, lip sync or morph-free continuity; visually inspect outputs.

## Relationship to other standards
- Preserve existing approved RUA dialogue and signature outro; do not revoice past published assets.
- For separately narrated **English full-length comparison videos**, follow the established Kokoro voice configuration from `CHAT_PUBLICATION_WORKFLOW.md`. Native English dialogue in newly generated Google Flow **character animation Shorts** is allowed when explicitly selected; do not misapply the Korean Sarah voice to English dialogue.
- For future Korean full-length reviews, follow Sarah/F1 editorial policy; Flow-generated short character dialogue and downstream full-video narration are different production stages.
- Follow `BRAND_ASSETS.md` for logo, `VIDEO_EDITORIAL_POLICY.md` for affiliate disclosures and factual product claims, and `CHAT_PUBLICATION_WORKFLOW.md` for final output/audio verification and SNS publishing.
- This instruction records creator preferences only. It does not itself modify a user's Google Flow Agent settings, incur credits, post a video, or authorize publication.
