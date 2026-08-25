#!/usr/bin/env python3
"""Lighten ONLY the phone-number text colors (Ivan's number area).
Target classes: .me .rl (next to "Ivan Silva") and .ftr / .ftr b (footer).
Leave everything else (voices, autoplay, other colors) untouched.
"""
import glob

REPL = [
    (".me .rl{font-size:12px;color:#aeb8c7;margin-top:1px}",
     ".me .rl{font-size:12px;color:#e5e9f0;margin-top:1px}"),
    (".ftr{padding:26px 22px 34px;border-top:1px solid #1f2937;color:#9aa7bd;font-size:11.5px;line-height:1.65;text-align:center}",
     ".ftr{padding:26px 22px 34px;border-top:1px solid #1f2937;color:#e5e9f0;font-size:11.5px;line-height:1.65;text-align:center}"),
    (".ftr b{color:#aeb8c7}", ".ftr b{color:#e5e9f0}"),
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
