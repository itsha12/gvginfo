"""Fetch YouTube transcripts listed in transcripts/requests.txt into <store>/transcripts/<id>.json.
Usage: python3 tools/fetch_transcripts.py <store dir>"""
import json, os, re, sys, time
from youtube_transcript_api import YouTubeTranscriptApi

store = os.path.join(sys.argv[1] if len(sys.argv) > 1 else "store", "transcripts")
os.makedirs(store, exist_ok=True)
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
api = YouTubeTranscriptApi()
for line in open(os.path.join(root, "transcripts", "requests.txt"), encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"): continue
    m = re.search(r"(?:v=|youtu\.be/|^)([A-Za-z0-9_-]{11})", line)
    if not m: continue
    vid = m.group(1)
    out = os.path.join(store, vid + ".json")
    if os.path.exists(out): print(vid, "already stored"); continue
    report = (re.search(r"gvg\.report/report/([0-9a-f-]{36})", line) or [None, None])[1]
    try:
        tr = api.fetch(vid, languages=["en", "en-US", "en-GB"])
        lines = [{"t": round(s.start, 1), "d": round(s.duration, 1), "text": s.text} for s in tr]
        json.dump({"video": vid, "report": report, "language": tr.language_code, "generated": tr.is_generated,
                   "lines": lines}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print(vid, f"{len(lines)} lines")
    except Exception as e:
        print(vid, "failed:", type(e).__name__, str(e)[:300])
    time.sleep(2)
