#!/usr/bin/env python3
"""One-time, owner-approved affiliate-link update for existing product videos.
Only explicitly matched publications and website-existing Associates links.
No new videos, no changed media, no reuploads.
"""
import json
import os
import pathlib
import urllib.parse
import urllib.request
import urllib.error

CHANNEL = "UC4DzAW-Hbd45bIECwGV7-uA"
TAG = "smartchoice36-22"
SITE = "https://smartchoice365-web.pages.dev"
AMZ = "https://www.amazon.com.au/s?k="
NINJA_GUIDE = SITE + "/guides/2026-ninja-af141-vs-af400-australia-single-dual-basket.html"
ICE_GUIDE = SITE + "/guides/2026-ice-maker-australia-summer-bullet-vs-dispenser.html"
NINJA_LINKS = [
    ("Ninja AF141", AMZ + "Ninja+AF141+air+fryer&tag=" + TAG),
    ("Ninja AF400", AMZ + "Ninja+AF400+air+fryer&tag=" + TAG),
]
ICE_LINKS = [
    ("Devanti IM-ZB12K-BK", AMZ + "Devanti+IM-ZB12K-BK+ice+maker&tag=" + TAG),
    ("Devanti IM-ZB12E-SR", AMZ + "Devanti+IM-ZB12E-SR+ice+maker+dispenser&tag=" + TAG),
]
TARGETS = [
    {"id":"2R5Nyt42hRs", "title":"Ninja", "guide":NINJA_GUIDE, "links":NINJA_LINKS},
    {"id":"SVtgsad_XsU", "title":"Ice Maker", "guide":ICE_GUIDE, "links":ICE_LINKS},
]
MARKER = "Smart Choice 365 · affiliate shopping links"
RESULTS = []

def http_json(url, form=None, bearer=None, method=None):
    headers = {"Accept":"application/json", "User-Agent":"SmartChoice365-ApprovedMetadata/1.0"}
    if bearer:
        headers["Authorization"] = "Bearer " + bearer
    data = None
    if form is not None:
        data = urllib.parse.urlencode(form).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

def http_json_payload(url, body, token):
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="PUT", headers={
        "Authorization":"Bearer "+token, "Accept":"application/json",
        "Content-Type":"application/json; charset=UTF-8",
        "User-Agent":"SmartChoice365-ApprovedMetadata/1.0"})
    with urllib.request.urlopen(req, timeout=35) as response:
        return json.loads(response.read().decode("utf-8"))

def section(links):
    lines = ["", "", "🛒 " + MARKER, "Advertisement · Amazon AU product searches (paid affiliate links)."]
    for name, url in links:
        p = urllib.parse.urlparse(url)
        q = urllib.parse.parse_qs(p.query)
        if p.hostname != "www.amazon.com.au" or q.get("tag") != [TAG] or not q.get("k"):
            raise ValueError("Invalid approved affiliate search link")
        lines.append(name + " (paid link): " + url)
    lines.extend([
        "As an Amazon Associate I earn from qualifying purchases.",
        "You pay no separate affiliate commission fee; normal seller, delivery and other charges may apply.",
        "These links show search results, not a guaranteed in-stock exact model or lowest price.",
    ])
    return "\n".join(lines)

def yt_token():
    values = {x:os.environ.get("YOUTUBE_"+x.upper(),"").strip()
              for x in ("client_id","client_secret","refresh_token")}
    if not all(values.values()):
        raise RuntimeError("YouTube OAuth secrets missing")
    values["grant_type"] = "refresh_token"
    return http_json("https://oauth2.googleapis.com/token", form=values)["access_token"]

def update_youtube():
    try:
        token = yt_token()
    except Exception as exc:
        RESULTS.append({"platform":"youtube","status":"blocked","reason":type(exc).__name__})
        return
    for t in TARGETS:
        item = {"platform":"youtube","id":t["id"],"status":"unverified"}
        try:
            data = http_json(
                "https://www.googleapis.com/youtube/v3/videos?"+
                urllib.parse.urlencode({"part":"snippet,status","id":t["id"]}),bearer=token)
            videos = data.get("items",[])
            if len(videos) != 1:
                raise ValueError("Video not found")
            vid = videos[0]
            meta = vid["snippet"]
            desc = meta.get("description","")
            if (meta.get("channelId") != CHANNEL or vid["status"].get("privacyStatus") != "public"
                or t["title"].lower() not in meta.get("title","").lower()
                or t["guide"] not in desc):
                raise ValueError("Video identity or exact website guide mismatch")
            if MARKER in desc:
                item["readback"] = {"marker":True,"links":[url in desc for _,url in t["links"]],
                                    "guide_first_line":t["guide"] in desc.splitlines()[0]}
                item["status"] = ("already_present_verified" if all(item["readback"]["links"])
                                  else "partial_missing_link")
                RESULTS.append(item)
                continue
            updated = desc.rstrip() + section(t["links"])
            if len(updated.encode("utf-8")) > 5000:
                raise ValueError("YouTube 5000-byte description limit")
            sn = {"title":meta["title"],"categoryId":meta["categoryId"],"description":updated}
            for key in ("tags","defaultLanguage"):
                if key in meta:
                    sn[key] = meta[key]
            http_json_payload("https://www.googleapis.com/youtube/v3/videos?part=snippet",
                              {"id":t["id"],"snippet":sn},token)
            after = http_json(
                "https://www.googleapis.com/youtube/v3/videos?"+
                urllib.parse.urlencode({"part":"snippet","id":t["id"]}),bearer=token)
            newdesc = after["items"][0]["snippet"].get("description","")
            item["readback"] = {"marker":MARKER in newdesc,
                                "links":[url in newdesc for _,url in t["links"]],
                                "same_first_line":desc.splitlines()[0] == newdesc.splitlines()[0],
                                "description_bytes":len(newdesc.encode("utf-8"))}
            if not item["readback"]["marker"] or not all(item["readback"]["links"]):
                raise RuntimeError("Metadata readback missing marker or link")
            if not item["readback"]["same_first_line"]:
                raise RuntimeError("Original first description line changed unexpectedly")
            item["status"] = "updated_verified"
            item["url"] = "https://www.youtube.com/watch?v=" + t["id"]
        except Exception as exc:
            item["status"] = "failed_or_unverified"
            item["reason"] = str(exc) if isinstance(exc,(RuntimeError,ValueError)) else type(exc).__name__
        RESULTS.append(item)

def meta_token(page_id):
    system = os.environ.get("META_SYSTEM_USER_ACCESS_TOKEN","").strip()
    page = os.environ.get("META_PAGE_ACCESS_TOKEN","").strip()
    if system:
        try:
            data = http_json("https://graph.facebook.com/v26.0/"+page_id+"?"+
                             urllib.parse.urlencode({"fields":"id,access_token"}),
                             bearer=system)
            if str(data.get("id")) == page_id and data.get("access_token"):
                return data["access_token"]
        except Exception:
            pass
    if page:
        return page
    raise RuntimeError("Meta Page access token unavailable")

def update_facebook():
    page_id = os.environ.get("META_FACEBOOK_PAGE_ID","1424295310764332").strip()
    video_id = "2693707811060236"
    report = {"platform":"facebook","id":video_id,"status":"unverified"}
    try:
        token = meta_token(page_id)
        base = "https://graph.facebook.com/v26.0/" + video_id
        old = http_json(base+"?"+urllib.parse.urlencode({"fields":"id,description,permalink_url"}),bearer=token)
        if str(old.get("id")) != video_id:
            raise ValueError("Facebook Reel identity mismatch")
        olddesc = old.get("description")
        if not isinstance(olddesc,str) or NINJA_GUIDE not in olddesc or "Ninja" not in olddesc:
            raise ValueError("Existing Reel caption cannot be safely validated")
        if MARKER in olddesc:
            report["status"] = "already_present"
            RESULTS.append(report)
            return
        affiliate_message = section(NINJA_LINKS).strip()
        updated = olddesc.rstrip() + "\n\n" + affiliate_message
        try:
            posted = http_json(base, form={"description":updated},bearer=token,method="POST")
            if posted.get("success") is not True:
                raise RuntimeError("Meta did not confirm edit")
            reread = http_json(base+"?"+urllib.parse.urlencode({"fields":"id,description"}),bearer=token)
            if MARKER not in reread.get("description",""):
                raise RuntimeError("Meta edit readback failed")
            report["status"] = "caption_updated_verified"
        except Exception:
            # If the API rejects editing an already-published Reel, do not replace,
            # delete or re-upload. A single properly disclosed Page comment is a fallback.
            existing = http_json(base+"/comments?"+
                urllib.parse.urlencode({"fields":"id,message","limit":100}),bearer=token)
            if any(MARKER in x.get("message","") for x in existing.get("data",[])):
                report["status"] = "comment_already_present"
            else:
                content = ("📖 Detailed comparison: "+NINJA_GUIDE+"\n\n"+affiliate_message)
                response = http_json(base+"/comments",form={"message":content},bearer=token,method="POST")
                cid = response.get("id")
                if not cid:
                    raise RuntimeError("Meta comment creation unconfirmed")
                check = http_json("https://graph.facebook.com/v26.0/"+cid+"?"+
                     urllib.parse.urlencode({"fields":"id,message"}),bearer=token)
                if MARKER not in check.get("message",""):
                    raise RuntimeError("Meta comment readback failed")
                report["status"] = "comment_published_verified"
                report["comment_id"] = cid
        report["url"] = "https://www.facebook.com/reel/" + video_id + "/"
    except Exception as exc:
        report["status"] = "failed_or_unverified"
        report["reason"] = type(exc).__name__
    RESULTS.append(report)

def main():
    update_youtube()
    update_facebook()
    path = pathlib.Path("publications/affiliate-metadata-results/2026-11-07.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"purpose":"approved product-video affiliate URL rollout",
                                "youtube_count":len(TARGETS),"results":RESULTS},
                               ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for result in RESULTS:
        print(json.dumps(result,ensure_ascii=False))
    if not any(x["status"] in ("updated_verified","already_present_verified","caption_updated_verified",
                                "comment_published_verified","comment_already_present")
               for x in RESULTS):
        raise SystemExit("No confirmed product-video affiliate metadata update")

if __name__ == "__main__":
    main()
