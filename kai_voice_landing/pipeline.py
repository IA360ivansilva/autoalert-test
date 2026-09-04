#!/usr/bin/env python3
"""
KAI PIPELINE - Voice pipeline + personalized landing integration
===============================================================
Owner: KAI (the-greatest). Flow: lead -> landing -> audio -> QA -> approval.

AUDIO-ONLY VERSION (27/08 working format).
No video generation. Direct MP3 audio playback.
"""
import argparse, asyncio, csv, json, os, re, sqlite3, sys
from pathlib import Path
from datetime import datetime

BASE = Path("/Users/clawbotlocal/AUTOALERT_CRM/05_campanhas")
DB   = "/Users/clawbotlocal/AUTOALERT_CRM/06_plataforma/ivanalert.db"
TPL  = BASE / "_template" / "index.html"
OUT  = BASE / "kai_out"
OUT.mkdir(parents=True, exist_ok=True)

VOICE = {
    "pt": {"male": "pt-BR-AntonioNeural",  "female": "pt-BR-FranciscaNeural"},
    "en": {"male": "en-US-AndrewNeural",    "female": "en-US-AriaNeural"},
}
PHONE = "(954) 860-0537"
PHONE_HREF = "19548600537"

def select_voice(gender: str, lang: str = "en") -> str:
    g = gender.lower().strip()
    if g in {"f", "female", "woman", "mulher"}:
        return VOICE.get(lang, VOICE["en"])["male"]
    elif g in {"m", "male", "man", "homem"}:
        return VOICE.get(lang, VOICE["en"])["female"]
    return VOICE.get(lang, VOICE["en"])["male"]

def parse_args():
    p = argparse.ArgumentParser(description="KAI Lead Pipeline (Audio-only)")
    p.add_argument("--cid", required=True, help="Contact ID")
    p.add_argument("--lang", default="en", help="Language (en/pt)")
    p.add_argument("--dry-run", action="store_true", default=True, help="Dry run (no send)")
    return p.parse_args()

def get_lead_data(cid: str) -> dict:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE contact_id = ?", (cid,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise ValueError(f"Lead {cid} not found")
    return dict(row)

def generate_audio(lead: dict, out_dir: str, script_text: str = "") -> dict:
    os.makedirs(out_dir, exist_ok=True)
    slug = f"{lead['contact_id']}-{lead['first_name'].lower()}"
    out_path = os.path.join(out_dir, f"{slug}.mp3")
    voice = select_voice(lead.get("gender_guess", "unknown"), lead.get("lang", "en"))
    import subprocess
    cmd = ["edge-tts", "--voice", voice, "--text", script_text, "--write-media", out_path]
    subprocess.run(cmd, capture_output=True, timeout=60)
    duration = 0
    if os.path.exists(out_path):
        dur_proc = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", out_path],
            capture_output=True, text=True, timeout=15
        )
        if dur_proc.returncode == 0:
            duration = float(dur_proc.stdout.strip())
    return {
        "path": out_path,
        "mode": "edge_tts",
        "duration_sec": duration,
        "size_bytes": os.path.getsize(out_path) if os.path.exists(out_path) else 0,
        "voice_label": voice,
    }

def main():
    args = parse_args()
    lead = get_lead_data(args.cid)
    print(f"[KAI] Processing lead: {lead.get('first_name', 'Unknown')} (ID: {args.cid})")
    script = f"Hi {lead.get('first_name', 'there')}, this is Ivan from Phil Smith Kia. I wanted to reach out about your {lead.get('vehicle', 'vehicle')} and see if you'd be interested in a free appraisal. Reply STOP to opt out."
    out_dir = os.path.join(OUT, f"{args.cid}-{lead['first_name'].lower()}", "audios")
    audio = generate_audio(lead, out_dir, script)
    print(f"[KAI] Audio: {audio['duration_sec']:.1f}s, {audio['size_bytes']} bytes")
    qa_pass = audio["duration_sec"] >= 25 and audio["duration_sec"] <= 40
    print(f"[KAI] QA: {'PASS' if qa_pass else 'FAIL'}")
    if not qa_pass:
        print("[KAI] BLOCK_SEND: QA failed")
        return
    print(f"[KAI] BLOCK_SEND: Ready for review")

if __name__ == "__main__":
    main()
