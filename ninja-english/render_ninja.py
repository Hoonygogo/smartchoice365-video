#!/usr/bin/env python3
"""Compatibility entry point: all new English previews use the common guide renderer.
Pass --request PATH with a reviewed independent-photo manifest. Historic one-off
owner-approved publishing code is separate and is not changed by this wrapper.
"""
import runpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'english-guide'))
if '--request' not in sys.argv:
    raise SystemExit('Use --request with the reviewed guide JSON. Old Ninja hard-coded slides are retired; no fallback rendering is allowed.')
runpy.run_path(str(ROOT/'english-guide/render_english_guide.py'),run_name='__main__')
