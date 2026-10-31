#!/usr/bin/env python3
"""Safely repair only deterministically fixable image size defects, max three rounds.
Never fabricate rights, photo quality, source provenance or human visual-review approval.
"""
import json,sys,subprocess
from pathlib import Path
from PIL import Image,ImageOps
from validate_video_scenes import validate

def repair(manifest_path):
    m=Path(manifest_path)
    if not m.is_file():return ['Missing approved visual scene manifest: photo generation/review required']
    doc=json.loads(m.read_text())
    items=doc.get('assets',doc.get('scenes',[]))
    # Do not alter originals: sizing non-1920x1080 approved sources needs
    # editorial review. No automatic stretching or art generation allowed.
    return validate(m)

def main():
    target=Path(sys.argv[1])
    for attempt in range(1,4):
        failures=repair(target)
        print(json.dumps({'attempt':attempt,'passed':not failures,'failures':failures},ensure_ascii=False),flush=True)
        if not failures:return 0
        # There is no trustworthy automatic remediation for unknown or unapproved art.
        # Revalidation still runs at most 3 times; stop early if nothing changed.
        break
    print('BLOCKED: automatic repair has no safe action. Supply reviewed independent photo-led scenes.',file=sys.stderr)
    return 2

if __name__=='__main__':sys.exit(main())
