"""YouTube altered/synthetic disclosure selection for future video publishing.

A confirmed non-realistic cartoon without reportable elements is No.
If a video mixes in realistic AI scenes, or if the review is incomplete or
ambiguous, choose the conservative Yes rather than blocking an approved upload.

Format is a contextual hint, NOT a final disclosure decision:
Smart Choice 365 Shorts are mostly animations and full videos are mostly
realistic AI-assisted buying guides. Check actual finished content when possible.
This helper does NOT bypass the existing video quality, owner-approval or hash
checks in the upload pipeline.
"""
from collections.abc import Mapping

REPORTABLE_FLAGS = (
    "realistic_synthetic_scene_present",
    "real_person_or_event_misrepresented",
    "ai_generated_music_main_focus",
)
EXEMPT_CLASSIFICATIONS = frozenset({
    "clearly_nonrealistic_animation",
    "minor_edits_or_production_assistance_only",
})


def apply_upload_disclosure(metadata, request):
    """Write the AI-use setting directly into YouTube API upload metadata.

    Only a completed and internally consistent exempt-content assessment can
    yield No. Mixed, realistic, unclear or unreviewed content yields Yes.
    Do not reject an otherwise approved upload solely for missing AI review.
    """
    if not isinstance(metadata, dict) or not isinstance(metadata.get("status"), dict):
        raise RuntimeError("YouTube upload metadata requires a valid status object.")

    review = request.get("ai_use_review") if isinstance(request, Mapping) else None
    reviewed = isinstance(review, Mapping) and review.get("final_video_reviewed") is True
    clear_exemption = (
        reviewed
        and review.get("classification") in EXEMPT_CLASSIFICATIONS
        and all(review.get(flag) is False for flag in REPORTABLE_FLAGS)
    )
    setting = not clear_exemption
    metadata["status"]["containsSyntheticMedia"] = setting
    return setting


def validate_ai_use(metadata, request):
    """Backward-compatible validation entry: enforce the same upload setting."""
    return apply_upload_disclosure(metadata, request)
