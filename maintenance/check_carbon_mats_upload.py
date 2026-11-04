#!/usr/bin/env python3
"""Read-only YouTube recent-upload audit after uncertain HTTP 502 video PUT.
No upload / update / delete operations. Do not repeat an uncertain upload.
"""
import json,os,sys,urllib.parse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from check_youtube import request_json
CHANNEL="UC4DzAW-Hbd45bIECwGV7-uA"
def main():
    keys=("client_id","client_secret","refresh_token")
    cred={k:os.environ["YOUTUBE_"+k.upper()].strip() for k in keys}
    result=request_json("https://oauth2.googleapis.com/token",
          data=urllib.parse.urlencode({**cred,"grant_type":"refresh_token"}).encode())
    token=result.get("access_token")
    if not token:raise RuntimeError("No YouTube token")
    print("::add-mask::"+token,flush=True)
    rows=request_json("https://www.googleapis.com/youtube/v3/channels?part=id,contentDetails&mine=true",
                      token=token).get("items",[])
    if len(rows)!=1 or rows[0].get("id")!=CHANNEL:
        raise RuntimeError("Unexpected authorized YouTube channel")
    playlist=rows[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    q=urllib.parse.urlencode({"part":"snippet,contentDetails","playlistId":playlist,"maxResults":"50"})
    items=request_json("https://www.googleapis.com/youtube/v3/playlistItems?"+q,token=token).get("items",[])
    keywords=("탄소매트","전기장판","온수매트","carbon mat")
    matches=[]
    for it in items:
        s=it.get("snippet",{})
        title=s.get("title","")
        if any(k in title.casefold() for k in keywords):
            matches.append({"id":s.get("resourceId",{}).get("videoId"),
                            "title":title,"published_at":s.get("publishedAt","")})
    output={"audit":"READ_ONLY","channel_id":CHANNEL,"recent_upload_count":len(items),
            "matches":matches,"target_title_visible":len(matches)>0,
            "warning":"No match in last 50 is not absolute proof that the upload was not created."}
    print("YOUTUBE_UPLOAD_AUDIT "+json.dumps(output,ensure_ascii=False),flush=True)
    summary=os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary,"a",encoding="utf-8") as f:
            f.write("# Carbon mat upload audit (read-only)\n\n")
            f.write("Checked authenticated channel recent uploads; no video uploaded by this job.\n")
            for m in matches:
                f.write("\n- "+m["title"]+" — https://www.youtube.com/watch?v="+m["id"]+"\n")
            if not matches:f.write("\nNo matching title among latest 50 uploads.\n")
if __name__=="__main__":
    try:main()
    except (RuntimeError,KeyError,ValueError) as exc:
        print("AUDIT_ERROR: "+str(exc),file=sys.stderr)
        raise SystemExit(1)
