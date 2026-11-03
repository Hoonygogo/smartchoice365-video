"""Fail-closed review of YouTube AI use disclosure for future video publications.

The boolean is about YouTube's disclosure requirement for realistic
altered/synthetic media, not whether AI tools helped in production.
"""
from collections.abc import Mapping

EXEMPT_CLASSIFICATIONS = {
    "clearly_nonrealistic_animation",
    "minor_edits_or_production_assistance_only",
}

def validate_ai_use(metadata, request):
    status = metadata.get("status", {}) if isinstance(metadata, Mapping) else {}
    value = status.get("containsSyntheticMedia")
    if type(value) is not bool:
        raise RuntimeError(
            "YouTube AI use is not explicitly reviewed. Set containsSyntheticMedia "
            "to true for realistic synthetic media, or false after documented "
            "review of an exempt final video."
        )
    if value is True:
        return True
    assessment = request.get("ai_use_review") if isinstance(request, Mapping) else None
    if not isinstance(assessment, Mapping):
        raise RuntimeError(
            "AI use No requires an explicit ai_use_review for the final rendered video."
        )
    if assessment.get("classification") not in EXEMPT_CLASSIFICATIONS:
        raise RuntimeError(
            "AI use No is allowed only for explicitly reviewed, clearly unreal "
            "animation or minor/assistance-only changes."
        )
    if assessment.get("final_video_reviewed") is not True:
        raise RuntimeError("AI use No requires a completed review of the final video.")
    required_facts = (
        "realistic_synthetic_scene_present",
        "real_person_or_event_misrepresented",
        "ai_generated_music_main_focus",
    )
    if any(assessment.get(fact) is not False for fact in required_facts):
        raise RuntimeError(
            "AI use No blocked: realistic synthetic scenes, real-person/event "
            "misrepresentation or AI-generated focal music must be ruled out."
        )
    return False


def apply_upload_disclosure(metadata, request):
    """Set the correct YouTube AI-use checkbox before a new upload.

    For a confirmed clearly unreal cartoon, No is mandatory; a caller cannot
    accidentally leave a stale Yes. Reportable realistic or mixed media cannot
    use the cartoon rule. Unknown content blocks uploading until classified.
    """
    if not isinstance(metadata, dict) or not isinstance(metadata.get("status"), dict):
        raise RuntimeError("Upload metadata requires a YouTube status object.")
    review = request.get("ai_use_review") if isinstance(request, Mapping) else None
    if not isinstance(review, Mapping) or review.get("final_video_reviewed") is not True:
        raise RuntimeError("Review the final video and supply ai_use_review before upload.")
    classification = review.get("classification")
    facts = ("realistic_synthetic_scene_present",
             "real_person_or_event_misrepresented",
             "ai_generated_music_main_focus")
    if any(type(review.get(flag)) is not bool for flag in facts):
        raise RuntimeError("AI-use review needs explicit Yes/No answers for all content flags.")
    reportable = any(review[flag] for flag in facts)
    if classification == "clearly_nonrealistic_animation":
        if reportable:
            raise RuntimeError("Mixed realistic/synthetic content cannot use cartoon AI-use No.")
        metadata["status"]["containsSyntheticMedia"] = False
        return False
    if classification == "minor_edits_or_production_assistance_only":
        if reportable:
            raise RuntimeError("Reportable synthetic elements require a different classification.")
        metadata["status"]["containsSyntheticMedia"] = False
        return False
    if classification == "realistic_synthetic_content":
        if not reportable:
            raise RuntimeError("Realistic synthetic classification requires a reportable element.")
        metadata["status"]["containsSyntheticMedia"] = True
        return True
    raise RuntimeError("Unrecognized AI-use classification; upload blocked.")
