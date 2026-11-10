# Smart Choice 365 — Google Flow RUA & ROY bilingual continuity playbook

Updated 2026-11-10 **after the owner supplied the existing 365-line "RUA — SMART CHOICE 365 MASTER PRODUCTION RULES."** That existing master is the **authoritative Flow Agent Instructions for the registered RUA character**. This file is a **supplementary episode-prompt / continuation playbook**, NOT a replacement and NOT a second conflicting agent instruction to paste over the master.

## Instruction priority

The owner-supplied RUA master defines this order:
1. **Critical registered RUA identity and permanent clothing-branding protection.**
2. **Explicit instructions in the current episode's script.**
3. **Project-wide defaults.**

An episode may intentionally change RUA's actions, outfit, scene, camera, spoken language, props, accessories, visual effects, teleportation or magic. The master protects identity and clothing logos, **not static outfits or fixed cameras**. Do not use sweeping prompts such as "never change clothing", "no teleportation ever", "always fixed camera", "always append the outro" or "every clip must be exactly 10 seconds". Disallow only **unrequested** changes unless an episode explicitly requires them.

## Preserve the original registered @RUA — not a regenerated substitute

- Select and verify the actual registered `@RUA` asset and its Character Profile, Portrait and Body reference when accessible. Do not claim verification without access.
- RUA is a beautiful stylized **adult** 3D cartoon with natural adult head/body proportions, big brown eyes and freckles, a dark-brown high ponytail with pink/purple highlights, and feminine athletic/curvy body proportions. Keep recognizable face/personality; **not** a real actress, generic replacement, chibi, disproportionate big-head or photorealistic figure.
- Her default signature costume (only **when the episode does not override it**) is: white crop top with **complete approved Smart Choice 365 chest logo**, hot-pink off-shoulder jacket, black cargo joggers with pink straps, white/pink sneakers. Preserve its normal construction. If front-facing, let the jacket naturally expose the complete logo without deforming her movement. Intentional temporary occlusion from motion is OK.
- **Critical permanent clothing rule:** The **only brand logo allowed anywhere on RUA's clothing is the official Smart Choice 365 logo.** Never add invented or third-party clothing marks, unrequested text, fake sponsors, duplicate/misshapen Smart Choice 365 logos, decorative logo patches or emblems. Do not replace a removed bad logo with a different symbol. Other costumes are allowed if scripted and still respect the branding rule; move the official logo to another garment only when explicitly requested.
- Sunglasses are **optional**. If present, only **one pair** (preferably on top of her head). Do not randomly create them or switch their position; intentional scripted appearance/removal/transformation is allowed.
- Floating LIKE/SUBSCRIBE/FOLLOW icons, hearts, magic particles, set signage, appropriate product packaging and approved branding are **not clothing logos** and may appear intentionally.

## ROY and other characters

Use **their own verified episode-specific or registered reference assets**; RUA's registered specification does not automatically define ROY's appearance or registered voice. In a continuation, preserve every approved character's identity, pose and relative positions unless the episode intentionally changes them.

## Language control: KOREAN and ENGLISH are equally supported

- Every new shot specifies `VIDEO_LANGUAGE: KOREAN` **or** `VIDEO_LANGUAGE: ENGLISH`. Silent comedy may specify `VIDEO_LANGUAGE: SILENT` when no one speaks.
- Technical direction may be written in English regardless of voice language. Speak the **exact episode dialogue**, naturally in the selected language. No extra or reused sample dialogue. If the chosen language is English, **do not silently translate to Korean**; if Korean, don't produce English.
- Prefer the actual registered RUA voice whenever available/compatible. RUA's delivery is youthful, bright, playful, expressive, charming and confident. Preserve previously approved audio/voices. Lip movement and expression must match each assigned speaker.
- RUA is pronounced **"Roo-ah" (two syllables)**, **not** individually spelled out "R-U-A"; title/logo/on-screen character name remains RUA.
- Do not force speech onto a requested silent episode. Short generated character dialogue is different from long-form narrated reviews (existing Sarah/Kokoro policy still applies where relevant).

## Successful café-puffer continuation method — use when relevant, not universally

For closely connected 8–10 second clips like the approved lightweight-puffer comedy:

1. Generate / approve one clip at a time.
2. Export its **actual last frame** as the next clip's **start frame**. Reattach the correct registered character and matching scene references when supported.
3. State the first frame's exact pose, hand positions, props, wardrobe, accessories, background, lighting and where ROY/RUA are standing. The café example kept ROY left and RUA right. For another episode, follow **its actual frame** instead of forcing that arrangement.
4. Prefer one continuous stable camera when **the episode calls for continuity without cinematic cuts**. Dolly moves, cuts, different locations and intentional teleportation are **permitted when scripted**.
5. Write a **second-by-second timeline** where useful: character, literal spoken line, gesture/expression, action, object transformation and end pose. Timing must fit the requested duration; **10 seconds is a default, not a hard rule**.
6. Make intentionally magical/comedic effects visually clear. Allow scripted costume change, cartoon duplication, appearance/disappearance and exaggerated physics. Reject only accidental morphs, surprise outfit resets, unexpected extra limbs, unauthorized patches, random props and unscripted position changes.
7. After a scripted transformation, the resulting look stays consistent **until the script requests a further change**. In the puffer café clip a jacket opened unexpectedly when the three brands were spoken: **that was a defect in that episode**, not a general ban on clothing changes.
8. Prefer a clear setup → amusing surprise → satisfying/funny conclusion, but defer to episode-specific storytelling.

## Suggested per-episode prompt (the master stays in Agent Instructions)

```text
PROJECT: Smart Choice 365 | @RUA & [verified ROY asset if present]
VIDEO_LANGUAGE: KOREAN [or ENGLISH or SILENT]
EPISODE CONTEXT: [the specific setup, joke, character motivation]
MODE: CONTINUATION [or NEW SCENE]
REFERENCE: [registered @RUA, other characters, previous clip final-frame PNG as start frame when supported]
DURATION: 10 seconds [or exact episode duration]
FORMAT: 9:16, Omni 1.1 Flash, 720p, 1 output [unless requested otherwise]
CAMERA: [fixed in café scene OR intentionally tracked/cut/moved for this story]
COSTUMES: [default approved costume OR describe exact authorized change]
ACCESSORIES: [absent/present; planned change if any]
INTENTIONAL EFFECTS: [explicit allowed transformations/teleportation/magic, or none]

0.0–2.0s: [speaker + exact dialogue + expression + starting pose]
2.0–5.0s: [speaker/action + motion + intended visual effect]
5.0–7.0s: [reaction and physically clear consequence]
7.0–10.0s: [payoff + end pose for next clip]

CONTINUITY: Keep the actual accepted character identities, background and objects unless this episode explicitly directs a change.
BRANDING: Absolutely no unauthorized logos or invented marks on @RUA's clothing. Official logo only when required and faithfully placed.
VOICE: Exact requested language and dialogue, RUA pronounced "Roo-ah", coherent natural lip sync. No extra lines.
NEGATIVE ERRORS: No accidental continuity changes, random props, unexpected sunglasses, costume/logo morph, duplicated accessories or unrelated text.
CREDIT GATE: Show this plan and obtain approval before spending generation credits.
```

## Original master default generation settings

- Model: **Omni 1.1 Flash**
- Duration: **10 seconds**
- Aspect ratio: **9:16 portrait**
- Resolution: **720p**
- Outputs: **1**
- Style: **premium stylized 3D animation**

These are defaults, **not restrictions on the episode**. Do not silently choose a paid/expensive model. Seek approval before any credit-consuming generation, additional variation or retry. If something fails, fix the smallest section possible without destroying the approved clip's successful parts.

## Outro and publishing boundaries

The existing RUA master states:
- **Use the approved signature outro when explicitly requested; do not automatically attach it to every Flow generation.**
- Preserve its original audio; never modify, double or fabricate it.
- If a **final Smart Choice 365 published Short** must contain the outro under a separate owner-approved publication brief / editorial policy, append it **once in post-production** rather than forcing Google Flow to re-create it. This reconciles the Flow master with downstream publishing requirements.
- No automatic SNS publication without approval. Existing published video/audio remains unchanged without new approval.
- Cartoon storytelling need not advertise products. For commerce projects, use genuine evidence, accurate network-specific affiliate disclosures, voluntary support copy, and distinguish fictional animation from product tests.

## Quality checks

Before spending credits: correct registered asset; voice and language; requested/default outfit; complete approved logo where shown; no unauthorized clothing branding; optional sunglasses logic; initial/final poses; camera/prop continuity; intended vs accidental effects; model/resolution/output settings; credit budget and user approval.

After rendering: inspect whole video for RUA identity and proportions, dialogue/lip sync, correct language, logo on all visible clothing frames, unintended third-party text, accessories, prop movement, valid scripted special effects, sound cuts, beginning/end completeness and comedy quality. **Do not label a defective video successful.** Preserve good shots and recommend a targeted correction; no unapproved credit expenditure.

## Relation to other repository policies

Read the existing owner-supplied **RUA — SMART CHOICE 365 MASTER PRODUCTION RULES** as the controlling Flow Agent Instructions. This document only adds a tested prompt technique and bilingual per-episode details. Respect `BRAND_ASSETS.md` for official assets, `VIDEO_EDITORIAL_POLICY.md` for buyer claims, `CHAT_PUBLICATION_WORKFLOW.md` for SNS/encoding and original voice. No claims that this GitHub document edited the user's live Google Flow settings.
