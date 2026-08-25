#!/usr/bin/env python3
"""Fix all landing pages in autoalert-pages repo:
1. Lighten low-contrast BLUE/GRAY font colors so text is readable.
2. Make the AI voice audio AUTO-PLAY on open (keeps tap-to-replay fallback).
Audio src stays ../audios/{slug}.mp3 (resolved at repo root after audios/ upload).
"""
import os, re, glob

# (old substring, new substring) — applied to every html file
REPLACEMENTS = [
    # dark grayish-blue labels -> readable light blue-gray
    ("color:#5f6b80", "color:#9aa7bd"),
    # mid gray-blue meta text -> lighter
    ("color:#8b96ab", "color:#aeb8c7"),
    # blue accent text (apr heading + footer disclosure) -> brighter blue
    ("color:#60a5fa", "color:#79c0ff"),
    # blue border on appraisal box -> brighter
    ("border:1.5px solid #2563eb;", "border:1.5px solid #3b82f6;"),
]

AUDIO_OLD = '<audio id="au" controls preload="none">'
AUDIO_NEW = '<audio id="au" controls autoplay playsinline preload="auto">'

AUTOPLAY_SCRIPT = (
    '<script>window.addEventListener("load",function(){'
    'var a=document.getElementById("au");'
    'if(a){var p=a.play();if(p&&p.catch){p.catch(function(){});}}});'
    '</script>\n</body>'
)

files = glob.glob("top50/*.html") + glob.glob("top200/*.html")
changed = 0
for f in files:
    with open(f, "r", encoding="utf-8") as fh:
        html = fh.read()
    original = html
    for old, new in REPLACEMENTS:
        html = html.replace(old, new)
    html = html.replace(AUDIO_OLD, AUDIO_NEW)
    # inject autoplay script right before </body> (only once)
    if "</body>" in html and "getElementById(\"au\")" not in html:
        html = html.replace("</body>", AUTOPLAY_SCRIPT, 1)
    if html != original:
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(html)
        changed += 1

print(f"Processed {len(files)} html files, changed {changed}.")
