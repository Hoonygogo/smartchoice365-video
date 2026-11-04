import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

FILE = Path(__file__).with_name("build_homepage_video_index.py")
spec = importlib.util.spec_from_file_location("public_video_index", FILE)
index = importlib.util.module_from_spec(spec)
spec.loader.exec_module(index)

class FormatTests(unittest.TestCase):
    def item(self, video_id="fqM-5HCCRck", fmt="video"):
        return {"status": "published_verified", "privacy": "public",
                "processing_status": "succeeded", "channel_id": index.CHANNEL,
                "video_id": video_id, "format": fmt, "language": "ko",
                "url": "https://www.youtube.com/watch?v=" + video_id}

    def test_full_video_is_verified_full_not_generic(self):
        self.assertEqual(index.classify(self.item())["format"], "video")

    def test_unverified_upload_never_in_index(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "publications/receipts").mkdir(parents=True)
            (root / "publications/receipts/a-youtube.json").write_text(
                json.dumps({**self.item(), "privacy": "private"}), encoding="utf-8")
            self.assertEqual(index.build(root)["videos"], [])

    def test_no_guess_from_watch_url_and_explicit_short_is_accepted(self):
        item = self.item(fmt=None)
        self.assertIsNone(index.classify(item))
        item["url"] = "https://www.youtube.com/shorts/fqM-5HCCRck"
        self.assertEqual(index.classify(item)["format"], "shorts")

    def test_request_format_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "publications/requests").mkdir(parents=True)
            (root / "publications/requests/new-full.json").write_text(
                json.dumps({"video_format": "video"}), encoding="utf-8")
            item = self.item(fmt=None)
            item["id"] = "new-full"
            self.assertEqual(index.classify(item, root)["format"], "video")

    def test_deleted_version_omitted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt_dir = root / "publications/receipts"
            receipt_dir.mkdir(parents=True)
            old = self.item("abcdefghijk")
            new = {**self.item(), "old_video_cleanup":
                   {"status": "deleted_verified", "video_id": old["video_id"]}}
            for name, item in [("a", old), ("b", new)]:
                (receipt_dir / f"{name}-youtube.json").write_text(
                    json.dumps(item), encoding="utf-8")
            self.assertEqual([v["id"] for v in index.build(root)["videos"]],
                             ["fqM-5HCCRck"])

if __name__ == "__main__":
    unittest.main()
