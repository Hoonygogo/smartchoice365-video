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
