#!/usr/bin/env python3
"""1) Avatar CC -> IS (Ivan Silva initials). 2) Book My Appraisal button red -> green (money/profit psychology)."""
import glob

REPL = [
    ('class="av">CC<', 'class="av">IS<'),
    (".b1{background:#c60f0f;color:#fff}",
     ".b1{background:#16a34a;color:#fff}"),
    # also the green equity card already exists; keep it.
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
