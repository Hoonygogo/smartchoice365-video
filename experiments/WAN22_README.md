# Wan 2.2 public ZeroGPU image-to-video experiment

This manual GitHub Action generates an AI video from the **exact source Ninja character image**, using the public `cbensimon/wan2-2-fp8da-aoti-preview2` Space.

**No paid fallback; never uses an inference provider, credit card, Hugging Face PRO, or paid GPU.** Public ZeroGPU is quota-limited and not guaranteed to work for automation. User must check the Space's terms and rights before using outputs commercially.

## How to test

1. Add the original image at `assets/ninja_original.png` to the repository (via GitHub web file upload), OR provide a direct public HTTPS image URL when triggering.
2. (Optional) If unauthenticated usage is blocked, add a fine-grained HF token with only the necessary public Space / inference access as `HF_TOKEN` GitHub Actions secret. Never share tokens in chat.
3. Actions → **Wan 2.2 Ninja AI video - free manual experiment** → Run workflow.
4. Download the `wan22-ninja-ai-generated-test` artifact, and check the character shape and movement. No YouTube publishing.
5. If free pool is busy or quota exhausted, the action fails without making purchases.

Underlying API shape is based on the public NiftyVid worker implementation, not yet validated by a successful GitHub Actions render. Space API may change. This workflow is **manual only** to avoid accidental use of free GPU quota, with a 25 minute job cutoff.
