"""Run locally with: python -m unittest scripts/test_youtube_ai_disclosure.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from youtube_ai_disclosure import validate_ai_use, apply_upload_disclosure

def approved_review():
    return {"ai_use_review": {
        "classification": "clearly_nonrealistic_animation",
        "final_video_reviewed": True,
        "realistic_synthetic_scene_present": False,
        "real_person_or_event_misrepresented": False,
        "ai_generated_music_main_focus": False,
    }}

class AIUseTests(unittest.TestCase):
    def test_yes_for_realistic_ai_scene(self):
        self.assertIs(validate_ai_use({"status": {"containsSyntheticMedia": True}}, {}), True)
    def test_no_for_reviewed_cartoon(self):
        self.assertIs(validate_ai_use({"status": {"containsSyntheticMedia": False}}, approved_review()), False)
    def test_unknown_setting_cannot_publish(self):
        with self.assertRaises(RuntimeError):
            validate_ai_use({"status": {}}, approved_review())
    def test_no_without_review_cannot_publish(self):
        with self.assertRaises(RuntimeError):
            validate_ai_use({"status": {"containsSyntheticMedia": False}}, {})
    def test_realistic_scene_cannot_be_labeled_no(self):
        review=approved_review()
        review["ai_use_review"]["realistic_synthetic_scene_present"] = True
        with self.assertRaises(RuntimeError):
            validate_ai_use({"status": {"containsSyntheticMedia": False}}, review)
    def test_ai_music_main_focus_cannot_be_labeled_no(self):
        review=approved_review()
        review["ai_use_review"]["ai_generated_music_main_focus"] = True
        with self.assertRaises(RuntimeError):
            validate_ai_use({"status": {"containsSyntheticMedia": False}}, review)
    def test_real_person_misrepresentation_cannot_be_labeled_no(self):
        review=approved_review()
        review["ai_use_review"]["real_person_or_event_misrepresented"] = True
        with self.assertRaises(RuntimeError):
            validate_ai_use({"status": {"containsSyntheticMedia": False}}, review)
    def test_unreviewed_video_cannot_be_labeled_no(self):
        review=approved_review()
        review["ai_use_review"]["final_video_reviewed"] = False
        with self.assertRaises(RuntimeError):
            validate_ai_use({"status": {"containsSyntheticMedia": False}}, review)


    def test_force_no_even_when_cartoon_request_says_yes(self):
        data = {"status": {"containsSyntheticMedia": True, "privacyStatus": "public"}}
        self.assertIs(apply_upload_disclosure(data, approved_review()), False)
        self.assertIs(data["status"]["containsSyntheticMedia"], False)
        self.assertEqual(data["status"]["privacyStatus"], "public")

    def test_force_no_when_missing_for_reviewed_cartoon(self):
        data = {"status": {"privacyStatus": "public"}}
        self.assertIs(apply_upload_disclosure(data, approved_review()), False)
        self.assertIs(data["status"]["containsSyntheticMedia"], False)

    def test_mixed_realistic_cartoon_is_not_silently_marked_no(self):
        req = approved_review()
        req["ai_use_review"]["realistic_synthetic_scene_present"] = True
        with self.assertRaises(RuntimeError):
            apply_upload_disclosure({"status": {"containsSyntheticMedia": True}}, req)

    def test_reject_cartoon_without_documented_final_video_review(self):
        req = approved_review()
        req["ai_use_review"]["final_video_reviewed"] = False
        with self.assertRaises(RuntimeError):
            apply_upload_disclosure({"status": {"containsSyntheticMedia": True}}, req)

    def test_realistic_video_requires_yes(self):
        req = approved_review()
        req["ai_use_review"].update(classification="realistic_synthetic_content",
                                   realistic_synthetic_scene_present=True)
        data = {"status": {"containsSyntheticMedia": False}}
        self.assertIs(apply_upload_disclosure(data, req), True)
        self.assertIs(data["status"]["containsSyntheticMedia"], True)

    def test_unknown_classification_rejected(self):
        req = approved_review()
        req["ai_use_review"]["classification"] = "unclassified"
        with self.assertRaises(RuntimeError):
            apply_upload_disclosure({"status": {}}, req)

    def test_single_use_rua_upload_scripts_are_no(self):
        root = Path(__file__).resolve().parents[1] / "maintenance"
        for name in ("publish_rua_ep00.py", "publish_rua_english_intro.py",
                     "publish_rua_ep01_robot_sock_trial.py",
                     "publish_rua_ep01_v2_20s.py"):
            with self.subTest(filename=name):
                content = (root / name).read_text()
                self.assertIn('"containsSyntheticMedia": False,', content)
                self.assertIn('if META["status"]["containsSyntheticMedia"] is not False:', content)
                self.assertNotIn('"containsSyntheticMedia": True,', content)

if __name__ == "__main__":
    unittest.main()
