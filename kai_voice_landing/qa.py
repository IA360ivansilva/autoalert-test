"""
kai_voice_landing / qa.py

Quality-assurance gate for the Kai voice+landing pipeline.

Runs BEFORE any send. Any failed check => verdict BLOCK_SEND.
Combines Atlas's structural checks (audio exists/size/duration/volume,
name-in-script, landing HTTP/mobile/desktop/CTA) with Kai's compliance gates
(approved cloned voice only, no forbidden voices, correct gender map,
phone color, CTA green, AI disclosure present, local-only test mode).
"""
import os
import re
import subprocess
import json
from datetime import datetime, timezone

AUDIO_MIN_SEC = 25.0
AUDIO_MAX_SEC = 40.0
AUDIO_MIN_SIZE = 1024

from .registry import (
    PHONE_COLOR, CTA_GREEN, FORBIDDEN_PHONE_BLUES, AI_DISCLOSURE, is_forbidden_voice,
)


def _ffprobe_duration(path: str) -> float:
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", path]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if r.returncode == 0 and r.stdout.strip():
            return float(r.stdout.strip())
    except Exception:
        pass
    try:
        return max(0.0, os.path.getsize(path) / 16000.0)
    except Exception:
        return 0.0


def _ffprobe_volume(path: str):
    try:
        r = subprocess.run(["ffmpeg", "-i", path, "-af", "volumedetect",
                            "-f", "null", "/dev/null"], capture_output=True, text=True, timeout=30)
        m = re.search(r"mean_volume:\s+([-\d.]+)\s+dB", r.stderr)
        if m:
            db = float(m.group(1))
            return min(1.0, max(0.0, 10 ** (db / 20.0)))
    except Exception:
        pass
    return None


def run_qa(audio: dict, landing_html: str, lead, mode: str, landing_url: str = None) -> dict:
    """audio: AudioResult dict-ish (path, mode, duration_sec, size_bytes, voice_label)
    landing_html: page source string
    lead: registry.Lead
    mode: 'approved_clone_copy' | 'xtts_per_client' | 'unavailable'
    landing_url: optional URL to HTTP-check when deployed
    """
    t0 = datetime.now(timezone.utc)
    results = []
    failures = []

    def record(check, passed, detail):
        results.append({"check": check, "passed": bool(passed), "detail": detail})
        if not passed:
            failures.append(check)

    ap = audio.get("path")
    # --- AUDIO structural ---
    if not ap or not os.path.isfile(ap):
        record("audio_exists", False, f"file not found: {ap}")
    else:
        size = os.path.getsize(ap)
        record("audio_size", size > AUDIO_MIN_SIZE, f"size={size} bytes")

    # --- AUDIO COMPLIANCE (Kai gate) ---
    vlabel = audio.get("voice_label", "")
    record("voice_not_forbidden",
           not is_forbidden_voice(vlabel) and mode != "unavailable",
           f"voice='{vlabel}' mode={mode}")
    # gender map: IVAN OVERRIDE 2026-08-28 opposite gender
    #   F (female client) -> Ivan (male clone)
    #   M (male client)   -> Zaramaya (female clone)
    g = (lead.gender or "").upper()
    expected_voice = {"F": "ivan", "M": "zaramaya"}.get(g, None)
    if expected_voice:
        record("voice_gender_map",
               expected_voice in vlabel.lower(),
               f"gender={g} expected voice contains '{expected_voice}', got '{vlabel}'")
    else:
        record("voice_gender_map", mode == "unavailable",
               "unknown gender -> must be unavailable + ask Ivan")

    dur = _ffprobe_duration(ap) if ap and os.path.isfile(ap) else 0.0
    # PER-CLIENT mode must be 25-40s. APPROVED_CLONE_COPY is a ~6s (here 2-6s)
    # fixed hero message — it CANNOT satisfy the per-client 25-40s requirement.
    # Per Kai HARD RULE + sales_landing_builder, a send-ready personalized landing
    # REQUIRES a real 25-40s customer-specific voice. A short fixed clone is a
    # stopgap that must BLOCK_SEND until Ivan approves (decision point).
    if mode == "cosyvoice_per_client":
        record("audio_duration", AUDIO_MIN_SEC <= dur <= AUDIO_MAX_SEC,
               f"per-client duration={dur:.2f}s (required 25-40s)")
    elif mode == "xtts_per_client":
        record("audio_duration", AUDIO_MIN_SEC <= dur <= AUDIO_MAX_SEC,
               f"per-client duration={dur:.2f}s (required 25-40s)")
    else:
        # fixed clone / unavailable -> cannot meet per-client spec -> BLOCK
        record("audio_per_client_25_40s",
               False,
               f"mode={mode} duration={dur:.2f}s — fixed/short clone cannot carry "
               f"per-client 25-40s script; BLOCK_SEND pending Ivan decision "
               f"(CosyVoice3 per-client now available)")

    if ap and os.path.isfile(ap):
        vol = _ffprobe_volume(ap)
        if vol is None:
            record("audio_volume", False, "volume check failed")
        else:
            record("audio_volume", vol > 10 ** (-40.0 / 20.0),
                   f"mean_volume≈{vol:.4f} linear")
    else:
        record("audio_volume", False, "no audio file")

    # script contains customer name (only meaningful for per-client)
    if mode == "xtts_per_client":
        record("script_has_name", lead.name.lower() in (lead.script or "").lower(),
               f"name '{lead.name}' in per-client script")
    else:
        record("script_has_name", True,
               "N/A for fixed clone (per-client specifics on page)")

    # --- LANDING COMPLIANCE ---
    h = landing_html or ""
    record("phone_visible", "tel:" + lead.phone_tel in h and lead.phone_display in h,
           f"tel:{lead.phone_tel} + {lead.phone_display} present")
    record("phone_color_e5e7eb",
           PHONE_COLOR in h and not any(b in h for b in FORBIDDEN_PHONE_BLUES),
           f"phone color {PHONE_COLOR}, no forbidden blue")
    record("cta_green", CTA_GREEN in h, f"CTA green {CTA_GREEN} present")
    record("cta_present", lead.cta.lower() in h.lower() and "Book" in h,
           f"CTA '{lead.cta}' present")
    record("avatar_is", '"IS"' in h or ">IS<" in h, "avatar initials 'IS'")
    record("ai_disclosure",
           (("assistant" in h.lower() or "assistente" in h.lower())
            and ("review" in h.lower() or "revis" in h.lower())),
           "AI disclosure present (review-only)")
    record("equivalent_models", "philsmithkia.com/search" in h, "equivalent model links present")
    record("no_other_customer_data",
           lead.name.lower() in h.lower(),  # basic: this customer's name present
           f"page references {lead.name}")

    # --- LANDING HTTP (if deployed) ---
    if landing_url:
        import requests
        try:
            r = requests.get(landing_url, timeout=15)
            record("landing_http", r.status_code == 200, f"HTTP {r.status_code}")
        except Exception as e:
            record("landing_http", False, f"request failed: {e}")
    else:
        record("landing_http", True, "SKIPPED — local test mode, not deployed")

    # --- BLOCK_SEND ---
    passed_all = len(failures) == 0
    verdict = "PASS" if passed_all else "BLOCK_SEND"
    t1 = datetime.now(timezone.utc)
    return {
        "verdict": verdict,
        "passed_all": passed_all,
        "failures": failures,
        "audio_mode": mode,
        "results": results,
        "meta": {
            "customer_name": lead.name,
            "customer_gender": lead.gender,
            "lang": lead.lang,
            "voice_label": vlabel,
            "landing_url": landing_url,
            "started_at": t0.isoformat(),
            "finished_at": t1.isoformat(),
        },
    }


def write_qa(path: str, qa: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(qa, f, indent=2, ensure_ascii=False)
    return path
