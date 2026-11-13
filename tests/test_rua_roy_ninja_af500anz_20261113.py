"""Offline preflight for approved Ninja RUA & ROY one-file release metadata (no publication)."""
import ast
import hashlib
import json
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
ID="rua-roy-ninja-af500anz-20261113"
SHA="5db49b1061e56e23f270784e8812bbc4ea2728ec5d40b3899678ab59733de019"
VIDEO="uploads/SmartChoice365_Ninja_AF500ANZ_RUA_ROY_Official_Outro_30s.mp4"
GUIDE="2026-ninja-af500anz-curated-buying-australia"
YOUTUBE=ROOT/"publications/requests"/(ID+"-youtube.json")
META=ROOT/"publications/staged-meta-requests"/(ID+".json")
WORKFLOW=ROOT/".github/workflows/rua-roy-ninja-af500anz-20261113-one-file-publish.yml"
PUBLISHER=ROOT/"maintenance/publish_rua_roy_ninja_af500anz_20261113.py"

class ApprovedNinjaTest(unittest.TestCase):
    def test_exact_metadata_and_hash(self):
        y=json.loads(YOUTUBE.read_text(encoding="utf-8"))
        m=json.loads(META.read_text(encoding="utf-8"))
        self.assertEqual(y["id"],ID)
        self.assertEqual(m["id"],ID)
        for item in (y,m):
            self.assertEqual(item["approval"],"publish")
            self.assertEqual(item["sha256"],SHA)
            self.assertEqual(item["media_path"],VIDEO)
            self.assertEqual(item["channel_id"],"UC4DzAW-Hbd45bIECwGV7-uA")
        self.assertEqual(y["size_bytes"],26213477)
        self.assertEqual(y["metadata"]["status"]["privacyStatus"],"public")
        self.assertEqual(m["platforms"],["instagram","facebook"])
        self.assertTrue(m["share_to_instagram_story"])

    def test_sales_disclosures_on_all_destinations(self):
        y=json.loads(YOUTUBE.read_text(encoding="utf-8"))
        m=json.loads(META.read_text(encoding="utf-8"))
        text={"YouTube":y["metadata"]["snippet"]["description"], **m["captions"]}
        for platform,caption in text.items():
            with self.subTest(platform=platform):
                for part in ("https://link.amazon/B0iDDqoqj","https://ebay.us/Rg5QFm",
                             GUIDE,"As an Amazon Associate I earn from qualifying purchases.",
                             "affiliate","commission"):
                    self.assertIn(part,caption)
                self.assertLess(len(caption),5000 if platform=="YouTube" else 1800)
        self.assertLess(len(y["metadata"]["snippet"]["title"]),100)
        self.assertIn("link in bio",text["instagram"])

    def test_publish_only_on_exact_uploaded_movie(self):
        w=WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('branches: [main]',w)
        self.assertIn('- "'+VIDEO+'"',w)
        self.assertIn('needs: preflight',w)
        self.assertIn('sha256',w)
        self.assertIn('ffmpeg -hide_banner -v error -xerror',w)
        self.assertIn('META_PUBLISH_ENABLED: "true"',w)
        self.assertIn('python maintenance/publish_meta_story_from_reel.py',w)
        self.assertIn('publications/staged-meta-requests/'+ID+'.json',w)
        self.assertIn('published_verified',w)
        self.assertNotIn('workflow_dispatch:',w)

    def test_youtube_publisher_syntax_and_duplicate_lock(self):
        p=PUBLISHER.read_text(encoding="utf-8")
        ast.parse(p)
        for term in (VIDEO.split("/")[-1],SHA,ID,"receipt_read(RECEIPT)",
                     "receipt_write(RECEIPT","published_verified","processing_failed"):
            self.assertIn(term,p)

    def test_approved_video_locally_when_present(self):
        f=ROOT/VIDEO
        if not f.is_file():
            self.skipTest("MP4 is intentionally not committed on PR; owner upload is the publication trigger")
        self.assertEqual(f.stat().st_size,26213477)
        self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),SHA)

if __name__=="__main__":
    unittest.main()
