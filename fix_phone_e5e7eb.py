#!/usr/bin/env python3
"""Force phone-number link/text color to #E5E7EB in ALL states (link/visited/hover/active)
and on the two visible numbers + Ivan card. Applies to all 250 pages."""
import glob

REPL = [
    # global <a> link states -> light
    ('a{color:#aeb8c7;font-size:13px;margin-top:5px}',
     'a{color:#E5E7EB;font-size:13px;margin-top:5px}a:link,a:visited,a:hover,a:active{color:#E5E7EB;text-decoration:none}'),
    # Ivan card number
    ('.me .rl{font-size:12px;color:#e5e9f0;margin-top:1px}',
     '.me .rl{font-size:12px;color:#E5E7EB;margin-top:1px}'),
    # footer
    ('.ftr{padding:26px 22px 34px;border-top:1px solid #1f2937;color:#e5e9f0;font-size:11.5px;line-height:1.65;text-align:center}',
     '.ftr{padding:26px 22px 34px;border-top:1px solid #1f2937;color:#E5E7EB;font-size:11.5px;line-height:1.65;text-align:center}'),
    ('.ftr b{color:#e5e9f0}', '.ftr b{color:#E5E7EB}'),
    # Call Ivan button (tel link) already #fff -> set explicit light + states
    ('.b2{background:rgba(255,255,255,.09);color:#fff;border:1px solid rgba(255,255,255,.16);flex:0 0 118px}',
     '.b2{background:rgba(255,255,255,.09);color:#E5E7EB;border:1px solid rgba(255,255,255,.16);flex:0 0 118px}.b2:link,.b2:visited,.b2:hover,.b2:active{color:#E5E7EB}'),
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
