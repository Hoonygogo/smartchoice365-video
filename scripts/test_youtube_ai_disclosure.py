"""AI disclosure upload regression tests — no network or YouTube credentials needed."""
import unittest
from pathlib import Path
from youtube_ai_disclosure import validate_ai_use, apply_upload_disclosure


def reviewed_cartoon():
    return {"ai_use_review": {
        "classification": "clearly_nonrealistic_animation",
        "final_video_reviewed": True,
        "realistic_synthetic_scene_present": False,
        "real_person_or_event_misrepresented": False,
        "ai_generated_music_main_focus": False,
    }}


class AIUseTests(unittest.TestCase):
    def choose(self, request, initial=None):
        metadata = {"status": {"privacyStatus": "public"}}
        if initial is not None:
            metadata["status"]["containsSyntheticMedia"] = initial
        selected = apply_upload_disclosure(metadata, request)
        self.assertIs(metadata["status"]["containsSyntheticMedia"], selected)
        self.assertEqual(metadata["status"]["privacyStatus"], "public")
        return selected

    def test_confirmed_fictional_cartoon_always_no_even_with_previous_yes(self):
        self.assertIs(self.choose(reviewed_cartoon(), True), False)

    def test_confirmed_fictional_cartoon_no_when_checkbox_absent(self):
        self.assertIs(self.choose(reviewed_cartoon()), False)

    def test_shorts_format_alone_not_sufficient_for_no(self):
        self.assertIs(self.choose({"video_format": "shorts"}), True)

    def test_full_video_format_alone_not_sufficient_for_no(self):
        self.assertIs(self.choose({"video_format": "video"}), True)

    def test_missing_review_uses_yes_without_blocking(self):
        self.assertIs(self.choose({}, False), True)

    def test_empty_review_uses_yes_without_blocking(self):
        self.assertIs(self.choose({"ai_use_review": {}}, False), True)

    def test_incomplete_final_review_uses_yes_without_blocking(self):
        req = reviewed_cartoon()
        req["ai_use_review"]["final_video_reviewed"] = False
        self.assertIs(self.choose(req, False), True)

    def test_missing_review_flag_uses_yes_without_blocking(self):
        req = reviewed_cartoon()
        del req["ai_use_review"]["realistic_synthetic_scene_present"]
        self.assertIs(self.choose(req, False), True)

    def test_unknown_classification_uses_yes_without_blocking(self):
        req = reviewed_cartoon()
        req["ai_use_review"]["classification"] = "unclassified"
        self.assertIs(self.choose(req, False), True)

    def test_mixed_cartoon_with_realistic_scenes_uses_yes(self):
        req = reviewed_cartoon()
        req["ai_use_review"]["realistic_synthetic_scene_present"] = True
        self.assertIs(self.choose(req, False), True)

    def test_cartoon_with_real_person_misrepresentation_uses_yes(self):
        req = reviewed_cartoon()
        req["ai_use_review"]["real_person_or_event_misrepresented"] = True
        self.assertIs(self.choose(req, False), True)

    def test_cartoon_with_focal_ai_music_uses_yes(self):
        req = reviewed_cartoon()
        req["ai_use_review"]["ai_generated_music_main_focus"] = True
        self.assertIs(self.choose(req, False), True)

    def test_realistic_video_uses_yes(self):
        req = reviewed_cartoon()
        req["ai_use_review"].update(classification="realistic_synthetic_content",
                                   realistic_synthetic_scene_present=True)
        self.assertIs(self.choose(req, False), True)

    def test_realistic_classification_even_without_flags_uses_yes(self):
        req = reviewed_cartoon()
        req["ai_use_review"]["classification"] = "realistic_synthetic_content"
        self.assertIs(self.choose(req, False), True)

    def test_minor_production_assistance_only_can_be_no_if_reviewed(self):
        req = reviewed_cartoon()
        req["ai_use_review"]["classification"] = "minor_edits_or_production_assistance_only"
        self.assertIs(self.choose(req, True), False)

    def test_minor_edits_mixed_with_reportable_content_uses_yes(self):
        req = reviewed_cartoon()
        req["ai_use_review"]["classification"] = "minor_edits_or_production_assistance_only"
        req["ai_use_review"]["realistic_synthetic_scene_present"] = True
        self.assertIs(self.choose(req, False), True)

    def test_legacy_validator_uses_same_default_yes(self):
        metadata = {"status": {"containsSyntheticMedia": False}}
        self.assertIs(validate_ai_use(metadata, {}), True)
        self.assertIs(metadata["status"]["containsSyntheticMedia"], True)

    def test_invalid_metadata_structure_is_blocked_not_missing_review(self):
        with self.assertRaises(RuntimeError):
            apply_upload_disclosure({}, {})

    def test_one_off_rua_cartoon_uploads_remain_no(self):
        root = Path(__file__).resolve().parents[1] / "maintenance"
        for name in ("publish_rua_ep00.py", "publish_rua_english_intro.py",
                     "publish_rua_ep01_robot_sock_trial.py",
                     "publish_rua_ep01_v2_20s.py"):
            with self.subTest(filename=name):
                source = (root / name).read_text()
                self.assertIn('"containsSyntheticMedia": False,', source)
                self.assertIn('if META["status"]["containsSyntheticMedia"] is not False:', source)
                self.assertNotIn('"containsSyntheticMedia": True,', source)


if __name__ == "__main__":
    unittest.main()
