import importlib.util
from pathlib import Path
import tempfile
import unittest
import json

spec=importlib.util.spec_from_file_location('clip',Path(__file__).parents[1]/'maintenance/prepare_naver_clip.py')
clip=importlib.util.module_from_spec(spec);spec.loader.exec_module(clip)
class SafetyTests(unittest.TestCase):
    def request(self):
        return dict(id='new-product',sha256='a'*64,naver_clip=dict(enabled=True,mode='draft',title='제목',description='설명',blog_url='https://blog.naver.com/smartchoice365/224469034521',blog_title='로보락',category_primary='테크',category_secondary='인터넷, AI',ai_used=True,advertising=False))
    def test_public_mode_is_rejected(self):
        r=self.request();r['naver_clip']['mode']='public'
        with self.assertRaises(ValueError):clip.prepare(r)
    def test_existing_hash_cannot_be_queued_again(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'publications/naver-clip-receipts';p.mkdir(parents=True)
            (p/'other.json').write_text(json.dumps({'id':'other','sha256':'a'*64}))
            self.assertIsNone(clip.prepare(self.request(),Path(d)))
    def test_description_limit_and_explicit_ai(self):
        r=self.request();r['naver_clip']['description']='x'*3001
        with self.assertRaises(ValueError):clip.prepare(r)
        r=self.request();del r['naver_clip']['ai_used']
        with self.assertRaises(ValueError):clip.prepare(r)
    def test_safe_job_is_not_published(self):
        with tempfile.TemporaryDirectory() as d:
            j=clip.prepare(self.request(),Path(d))
            self.assertFalse(j['public_publish_enabled']);self.assertEqual(j['privacy'],'private')
if __name__=='__main__':unittest.main()
