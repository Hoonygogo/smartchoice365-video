"""Check saved OAuth credentials and the target channel without uploading."""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def request_json(url, *, data=None, token=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        # Never log the response body, request, or credentials.
        raise RuntimeError(f"Google request failed (HTTP {exc.code}); check credentials and API permissions.") from None
    except (urllib.error.URLError, ValueError):
        raise RuntimeError("Google connection or JSON response failed.") from None


def main():
    names = ["YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"]
    missing = [name for name in names if not os.environ.get(name, "").strip()]
    if missing:
        raise RuntimeError("Missing repository secrets: " + ", ".join(missing))
    payload = {name.removeprefix("YOUTUBE_").lower(): os.environ[name].strip() for name in names}
    payload["grant_type"] = "refresh_token"
    result = request_json("https://oauth2.googleapis.com/token", data=urllib.parse.urlencode(payload).encode())
    token = result.get("access_token")
    if not token:
        raise RuntimeError("Google did not return an access token.")
    print("::add-mask::" + token, flush=True)
    channels = request_json("https://www.googleapis.com/youtube/v3/channels?part=id,snippet&mine=true&fields=items(id,snippet(title,customUrl))", token=token).get("items", [])
    if len(channels) != 1:
        raise RuntimeError("Expected exactly one authorized YouTube channel.")
    channel = channels[0]
    snippet = channel.get("snippet", {})
    if snippet.get("customUrl", "").lower() != "@smartchoice365":
        raise RuntimeError("Authorized channel does not match @SmartChoice365; publication blocked.")
    print(json.dumps({"check": "passed", "channel_id": channel["id"], "title": snippet.get("title"), "handle": snippet.get("customUrl"), "uploaded": False}, ensure_ascii=False))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as out:
            out.write("YouTube OAuth check passed. Refresh token exchanged successfully and @SmartChoice365 channel verified. No video uploaded.\n")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
