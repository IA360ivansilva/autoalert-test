#!/usr/bin/env python3
"""Lighten the remaining blue (#79c0ff) in the footer disclosure + appraisal header
to white (#e5e9f0) so NO blue remains near the phone number."""
import glob

REPL = [
    (".apr-h{font-size:12px;letter-spacing:1.1px;color:#79c0ff;font-weight:800;margin-bottom:11px}",
     ".apr-h{font-size:12px;letter-spacing:1.1px;color:#e5e9f0;font-weight:800;margin-bottom:11px}"),
    ('<span style="color:#79c0ff">', '<span style="color:#e5e9f0">'),
]

files = glob.glob("top50/*.html") + glob.glob("top200/*.html")
changed = 0
for f in files:
    with open(f, encoding="utf-8") as fh:
        h = fh.read()
    o = h
    for a, b in REPL:
        h = h.replace(a, b)
    if h != o:
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(h)
        changed += 1
print(f"changed {changed}/{len(files)} files")
