# Image-first automation / GitHub storage contract

Once a separately AI-generated full scene image is accepted, store its **binary PNG/JPG** in the video repository **before** narration or editing. The archived file, scene metadata and SHA-256 become the source of truth. No later stage may silently redraw it as shapes or text.

1. Generate a single complete image for every photographic scene, without collages or embedded titles. Collect twelve individually approved scenes, at least eight original AI photographic scenes, each at least 1280×720.
2. For each `scene_00.png` to `scene_11.png`, write a matching `scene_00.json` (etc.) containing:
   `{"source_kind":"single_full_frame_photo","generation_method":"individual_ai_generated","visual_review_passed":true,"usage_approved":true,"contact_sheet":false,"contains_crop_loss":false,"baked_in_storyboard_labels":false}`.
   For original comparison charts use `source_kind: "editorial_chart"` and `generation_method: "programmatic_comparison"`, with the same approval/quality flags. **Never assert visual_review_passed=true without checking that actual image.**
3. In a runtime with authenticated **contents:write** access to the repo, call `GITHUB_TOKEN=... python scripts/store_generated_scenes.py --topic breville-english --input /path/to/scenes --approved`. Keep the token private, do not check it in. The uploader uses GitHub blobs, an atomic tree+commit and post-commit readback verification; it fails rather than saying images were saved when they were not.
4. Archive path: `videos/<topic>/images/scene_00.png` ... and `videos/<topic>/approved_visual_manifest.json`. Never overwrite already-approved files silently: any replacement requires a fresh review and a new commit.
5. When committed to `main`, the Breville workflow checks out these **exact files**, verifies checksums and original logo, and renders with Kokoro `af_heart` at 0.96. It must not fall back to espeak or a placeholder.
6. Verify actual decoded audio, full uncropped logo, full image visibility, correct read-out, and iPhone playback before presenting an MP4 for approval. Only publish YouTube after explicit approval of the exact preview.

**Scope and limitation:** Generation inside a ChatGPT conversation does not automatically mean GitHub has the bytes. The authenticated upload command must actually run on the image files. GitHub Actions cannot read local ChatGPT sandbox assets by itself. Until an upload reports `VERIFIED_GITHUB_SAVED`, the user must be told that image transfer is pending; never claim a final video exists.
