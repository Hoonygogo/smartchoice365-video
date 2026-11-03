"""Run locally with: python -m unittest scripts/test_youtube_ai_disclosure.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from youtube_ai_disclosure import validate_ai_use

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

if __name__ == "__main__":
    unittest.main()
