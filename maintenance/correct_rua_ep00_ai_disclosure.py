#!/usr/bin/env python3
"""Correct the synthetic-media checkbox on ONE user-identified non-photorealistic RUA cartoon Short.

YouTube's containsSyntheticMedia property discloses *realistic* altered or
synthetic content. The original RUA EP00 is a clearly illustrated cartoon.
Do not use this script for photorealistic video, real people or other content
that requires the disclosure. Do not edit title, description, privacy or media.
"""
import json
import os
import urllib.parse

from check_youtube import request_json
from publish_youtube_generic import api, CHANNEL

VIDEO_ID = "05yTkr0lBj0"
EXPECTED_CHANNEL = "UC4DzAW-Hbd45bIECwGV7-uA"
EXPECTED_TITLE = "쇼핑하기 전에 잠깐!"
MUTABLE_STATUS = ("privacyStatus", "embeddable", "license",
                  "publicStatsViewable", "selfDeclaredMadeForKids")


def main():
    assert CHANNEL == EXPECTED_CHANNEL
    creds = {name: os.environ["YOUTUBE_" + name.upper()].strip()
             for name in ("client_id", "client_secret", "refresh_token")}
    if not all(creds.values()):
        raise RuntimeError("YouTube OAuth secrets not configured.")
    creds["grant_type"] = "refresh_token"
    token = request_json(
        "https://oauth2.googleapis.com/token",
        data=urllib.parse.urlencode(creds).encode()
    )["access_token"]
    print("::add-mask::" + token, flush=True)

    channels = request_json(
        "https://www.googleapis.com/youtube/v3/channels?part=id&mine=true",
        token=token
    ).get("items", [])
    if [c.get("id") for c in channels] != [EXPECTED_CHANNEL]:
        raise RuntimeError("Unexpected YouTube channel; not changing video.")

    url = ("https://www.googleapis.com/youtube/v3/videos?part=snippet,status&id="
           + urllib.parse.quote(VIDEO_ID))
    items = request_json(url, token=token).get("items", [])
    if len(items) != 1:
        raise RuntimeError("Target Short not found in the authenticated channel.")
    video = items[0]
    title = video.get("snippet", {}).get("title", "")
    status = video.get("status", {})
    if video.get("snippet", {}).get("channelId") != EXPECTED_CHANNEL:
        raise RuntimeError("Video does not belong to approved channel.")
    if not title.startswith(EXPECTED_TITLE):
        raise RuntimeError("Unexpected video title; refusing to update.")
    if status.get("privacyStatus") != "public":
        raise RuntimeError("Video no longer public; refusing to update.")
    if status.get("containsSyntheticMedia") is False:
        print("ALREADY_CORRECT: Video AI use explicitly set to No.")
        return
    if status.get("containsSyntheticMedia") is not True:
        raise RuntimeError("AI use setting not explicitly Yes; refusing to overwrite.")

    # The status portion overwrites other mutable status fields; preserve all
    # values returned by the owner-authorized API before changing only this one.
    new_status = {key: status[key] for key in MUTABLE_STATUS if key in status}
    new_status["containsSyntheticMedia"] = False
    if new_status.get("privacyStatus") != "public":
        raise RuntimeError("Privacy status changed unexpectedly.")
    body = json.dumps({"id": VIDEO_ID, "status": new_status}).encode("utf-8")
    update_url = "https://www.googleapis.com/youtube/v3/videos?part=status"
    response, _ = api(update_url, "PUT", body, token,
                      {"Content-Type": "application/json; charset=UTF-8"})
    if isinstance(response, bytes):
        response = json.loads(response.decode("utf-8"))
    elif isinstance(response, str):
        response = json.loads(response)
    if response.get("id") != VIDEO_ID:
        raise RuntimeError("YouTube update response did not confirm target video.")
    verify = request_json(url, token=token).get("items", [])
    if len(verify) != 1:
        raise RuntimeError("YouTube did not return the video for verification.")
    after = verify[0].get("status", {})
    if after.get("containsSyntheticMedia") is not False:
        raise RuntimeError("YouTube did not persist the AI use setting change.")
    if any(after.get(k) != status.get(k) for k in MUTABLE_STATUS):
        raise RuntimeError("Other mutable video-status settings changed; inspect immediately.")
    print("CORRECTED_AND_VERIFIED: RUA EP00 'AI use' checkbox now No in YouTube Data API.")
    print("Note: YouTube may independently apply mandatory/automated on-player labels.")


if __name__ == "__main__":
    main()
