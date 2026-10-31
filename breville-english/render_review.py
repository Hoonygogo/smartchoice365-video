#!/usr/bin/env python3
"""Compatibility entry point for the common Korean-parity English guide renderer."""
import runpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'english-guide'))
if '--request' not in sys.argv:
    raise SystemExit('Pass --request for the reviewed guide JSON. Legacy six-photo layouts are retired; no fallback rendering.')
runpy.run_path(str(ROOT/'english-guide/render_english_guide.py'),run_name='__main__')
