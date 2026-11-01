#!/usr/bin/env python3
"""Safe read-only verification of Smart Choice 365's Meta system-user credential.

Never print or persist any access token, never publish, never modify Meta data.
"""
import json
import os
import urllib.parse
import urllib.request
import urllib.error

API = "https://graph.facebook.com/v26.0"
TOKEN = os.environ.get("META_SYSTEM_USER_ACCESS_TOKEN", "").strip()
PAGE_ID = os.environ.get("META_FACEBOOK_PAGE_ID", "").strip() or "1424295310764332"
IG_ID = os.environ.get("META_INSTAGRAM_ACCOUNT_ID", "").strip() or "17841475811391464"

if not TOKEN:
    raise SystemExit("FAIL: META_SYSTEM_USER_ACCESS_TOKEN is missing. Confirm repository Actions secret.")
print("PASS: GitHub Actions can read the Meta system-user secret (value hidden).")

def get(path, fields=None):
    url = API + path
    if fields:
        url += "?" + urllib.parse.urlencode({"fields": fields})
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + TOKEN,
        "Accept": "application/json",
        "User-Agent": "SC365-Meta-ReadOnlyCheck/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        print("Meta Graph API request rejected: HTTP " + str(error.code) + " (token and body withheld).")
        return None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        print("Meta Graph API unavailable; no write was attempted.")
        return None

me = get("/me", "id,name")
if me is None or not str(me.get("id", "")):
    raise SystemExit("FAIL: Meta token could not authenticate against /me.")
print("PASS: Meta accepted the system-user token for /me.")

if PAGE_ID and PAGE_ID.isdigit():
    page = get("/" + PAGE_ID, "id,name,instagram_business_account,access_token")
    if page and str(page.get("id")) == PAGE_ID:
        print("PASS: Configured Facebook Page ID is accessible: " + PAGE_ID)
        actual_ig = str((page.get("instagram_business_account") or {}).get("id", ""))
        if actual_ig:
            if IG_ID and IG_ID != actual_ig:
                raise SystemExit("FAIL: META_INSTAGRAM_ACCOUNT_ID does not match the Page-linked Instagram account.")
            print("PASS: Page-linked Instagram professional account ID: " + actual_ig)
            if not IG_ID:
                print("NEXT: Add repository variable META_INSTAGRAM_ACCOUNT_ID with the ID displayed above.")
        derived_token = page.get("access_token", "")
        if not isinstance(derived_token, str) or not derived_token:
            raise SystemExit("FAIL: Could not derive Facebook Page token from system-user token. Check approved Page permissions.")
        req = urllib.request.Request(
            API + "/" + PAGE_ID + "?fields=id,name",
            headers={"Authorization": "Bearer " + derived_token,
                     "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=25) as response:
                check = json.load(response)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            raise SystemExit("FAIL: Derived Facebook Page token did not authenticate. No token data displayed.")
        if str(check.get("id")) != PAGE_ID:
            raise SystemExit("FAIL: Derived Page token refers to an unexpected Page ID.")
        print("PASS: System-user token successfully derived and verified a Facebook Page access token (hidden).")
        else:
            print("CHECK: No Instagram professional account was returned for the configured Facebook Page.")
    else:
        print("CHECK: Page ID exists as variable but is not accessible to the token.")
else:
    print("NEXT: Add repository variable META_FACEBOOK_PAGE_ID (numeric Facebook Page ID, not business portfolio ID).")
    pages = get("/me/accounts", "id,name,instagram_business_account")
    if pages and isinstance(pages.get("data"), list):
        matches = [p for p in pages["data"] if p.get("name") == "Smart Choice 365"]
        if len(matches) == 1:
            p = matches[0]
            print("HINT: An exact-name Smart Choice 365 Page was found: " + str(p.get("id", "")))
            ig = (p.get("instagram_business_account") or {}).get("id")
            if ig:
                print("HINT: Linked Instagram professional account ID: " + str(ig))
        else:
            print("CHECK: No unique exact-name Page found. Retrieve Page ID from Meta Business Settings.")
    else:
        print("CHECK: /me/accounts unavailable for this token; use Meta Business Settings to retrieve Page ID.")

print("SAFE: This check only made read-only GET requests; nothing was posted.")
