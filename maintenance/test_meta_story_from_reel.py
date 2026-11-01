#!/usr/bin/env python3
"""Offline tests: never use a real Meta token or publish a real Instagram Story."""
import contextlib
import io
import os
import unittest
from unittest import mock

import publish_meta_story_from_reel as followup
import publish_meta_stories as standalone

DIGEST = "a" * 64
REQUEST = {
    "id": "verified-future-reel",
    "approval": "publish",
    "platforms": ["instagram", "facebook"],
    "sha256": DIGEST,
    "media_path": "uploads/approved.mp4",
    "channel_id": "UC4DzAW-Hbd45bIECwGV7-uA",
}
VERIFIED = {
    "status": "published_verified",
    "platform": "instagram",
    "sha256": DIGEST,
    "permalink": "https://www.instagram.com/reel/ExamplePublic123/",
}


class FollowUpTest(unittest.TestCase):
    def run_main(self, *, enabled="true", request=None, receipt=VERIFIED):
        with mock.patch.dict(os.environ, {"META_PUBLISH_ENABLED": enabled}, clear=True), \
             mock.patch.object(followup, "validate_request", return_value=dict(REQUEST if request is None else request)) as validate, \
             mock.patch.object(followup, "receipt_read", return_value=(receipt, "sha")) as read, \
             mock.patch.object(followup, "checked_file", return_value=("https://example.com/video.mp4", {"duration": 11.833,"size": 300000})) as check, \
             mock.patch.object(followup, "publish_story") as publish, \
             contextlib.redirect_stdout(io.StringIO()):
            self.result = (validate, read, check, publish)
            followup.main()

    def test_disabled_dry_run_never_publishes(self):
        self.run_main(enabled="false")
        self.result[0].assert_not_called()
        self.result[1].assert_not_called()
        self.result[3].assert_not_called()

    def test_only_approved_reels_create_stories(self):
        bad = dict(REQUEST, approval="prepare")
        with self.assertRaises(RuntimeError):
            self.run_main(request=bad)
        self.result[3].assert_not_called()

    def test_facebook_only_does_not_create_instagram_story(self):
        self.run_main(request=dict(REQUEST, platforms=["facebook"]))
        self.result[1].assert_not_called()
        self.result[3].assert_not_called()

    def test_opt_out(self):
        self.run_main(request=dict(REQUEST, share_to_instagram_story=False))
        self.result[3].assert_not_called()

    def test_unverified_reel_cannot_publish_story(self):
        with self.assertRaises(RuntimeError):
            self.run_main(receipt=dict(VERIFIED, status="published_unverified"))
        self.result[3].assert_not_called()

    def test_mismatched_reel_media_cannot_publish_story(self):
        with self.assertRaises(RuntimeError):
            self.run_main(receipt=dict(VERIFIED, sha256="b" * 64))
        self.result[3].assert_not_called()

    def test_verified_reel_is_shared_using_exact_same_media(self):
        self.run_main()
        self.result[3].assert_called_once()
        story, url, meta = self.result[3].call_args.args
        self.assertEqual(story["id"], REQUEST["id"])
        self.assertEqual(story["sha256"], DIGEST)
        self.assertEqual(story["media_path"], REQUEST["media_path"])
        self.assertEqual(story["platform"], "instagram_story")
        self.assertEqual(story["instagram_account_id"], "17841475811391464")
        self.assertEqual(story["parent_instagram_reel"], VERIFIED["permalink"])
        self.assertEqual(url, "https://example.com/video.mp4")

    def test_previously_published_story_is_not_posted_again(self):
        published = {
            "status": "published_verified",
            "platform": "instagram_story",
            "sha256": DIGEST,
            "media_id": "1234567890",
        }
        story = dict(REQUEST, platform="instagram_story")
        with mock.patch.object(standalone, "receipt_read", return_value=(published, "sha")), \
             mock.patch.object(standalone, "token_for") as token, \
             mock.patch.object(standalone, "json_request") as meta_call, \
             contextlib.redirect_stdout(io.StringIO()):
            standalone.publish(story, "https://example.com/video.mp4", {"size": 300000})
            token.assert_not_called()
            meta_call.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
