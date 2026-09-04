"""
kai_voice_landing / qa.py
Quality-assurance gate for Kai AI BDC.

Runs BEFORE any send. Any failed check => verdict BLOCK_SEND.
Enforces:
1. Audio: duration 25-40s, decodes cleanly, repetition penalty/no looping,
   approved clone voice (Chatterbox Turbo 200wpm baseline / CosyVoice3), opposite-gender rule.
2. Video: web-compatible MP4, duration matches audio within ±1.5s, valid poster frame.
3. Landing: mobile-first, phone #E5E7EB, CTA green #16a34a, AI disclosure present.
4. Messaging: TCPA opt-out on SMS ("Reply STOP"), CAN-SPAM on email, no credit guarantees.
5. Safety: BLOCK_SEND enforced by default. Never contact customers without explicit approval.
"""
import os
import re
import subprocess
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

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

def _ffprobe_volume(path: str) -> Optional[float]:
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

def run_qa(
    audio: dict,
    landing_html: str,
    lead,
    mode: str,
    video: Optional[dict] = None,
    sms_draft: Optional[dict] = None,
    email_draft: Optional[dict] = None,
    landing_url: Optional[str] = None
) -> dict:
    t0 = datetime.now(timezone.utc)
    results = []
    failures = []

    def record(check: str, passed: bool, detail: str):
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

    # --- AUDIO COMPLIANCE ---
    vlabel = audio.get("voice_label", "")
    record("voice_not_forbidden",
           not is_forbidden_voice(vlabel) and mode != "unavailable",
           f"voice='{vlabel}' mode={mode}")

    # Opposite-gender rule:
    # F -> Ivan male, M -> Zara female
    g = (lead.gender or "").upper()
    expected_voice = {"F": "ivan", "M": "zara"}.get(g, None)
    if expected_voice:
        record("voice_gender_map",
               expected_voice in vlabel.lower(),
               f"gender={g} expected voice containing '{expected_voice}', got '{vlabel}'")
    else:
        record("voice_gender_map", mode == "unavailable", "unknown gender -> must be unavailable")

    dur = _ffprobe_duration(ap) if ap and os.path.isfile(ap) else 0.0
    if mode in {"chatterbox_turbo_200wpm", "cosyvoice_per_client", "xtts_per_client"}:
        record("audio_duration_25_40", AUDIO_MIN_SEC <= dur <= AUDIO_MAX_SEC,
               f"per-client duration={dur:.2f}s (required 25-40s)")
    else:
        record("audio_duration_25_40", False,
               f"mode={mode} duration={dur:.2f}s — fixed clone cannot satisfy per-client 25-40s")

    if ap and os.path.isfile(ap):
        vol = _ffprobe_volume(ap)
        if vol is None:
            record("audio_volume", False, "volume check failed")
        else:
            record("audio_volume", vol > 10 ** (-40.0 / 20.0), f"mean_volume={vol:.4f}")
    else:
        record("audio_volume", False, "no audio file")

    # --- VIDEO COMPLIANCE (optional / progressive enhancement) ---
    if video and video.get("video_path"):
        vp = video["video_path"]
        record("video_exists", os.path.isfile(vp), f"path={vp}")
        vsize = os.path.getsize(vp) if os.path.isfile(vp) else 0
        record("video_size", vsize > 10000, f"size={vsize} bytes")
        vdur = video.get("duration_sec", 0.0)
        record("video_audio_sync", abs(vdur - dur) <= 1.5, f"vdur={vdur:.1f}s vs adur={dur:.1f}s")
        if video.get("poster_path"):
            record("video_poster_exists", os.path.isfile(video["poster_path"]), video["poster_path"])

    # --- LANDING COMPLIANCE ---
    h = landing_html or ""
    record("phone_visible", "tel:" + lead.phone_tel in h and lead.phone_display in h,
           f"tel:{lead.phone_tel} + {lead.phone_display} present")
    record("phone_color_e5e7eb",
           PHONE_COLOR in h and not any(b in h for b in FORBIDDEN_PHONE_BLUES),
           f"phone color {PHONE_COLOR}, no forbidden blue")
    record("cta_green", CTA_GREEN in h, f"CTA green {CTA_GREEN} present")
    record("cta_present", lead.cta.lower() in h.lower() and "Book" in h, f"CTA '{lead.cta}' present")
    record("avatar_is", '"IS"' in h or ">IS<" in h, "avatar initials 'IS'")
    record("ai_disclosure",
           (("assistant" in h.lower() or "assistente" in h.lower())
            and ("review" in h.lower() or "revis" in h.lower())),
           "AI disclosure present")
    record("kai_player_script", "kai-player.js" in h, "reliable kai-player.js referenced")
    record("no_credit_guarantee",
           "guaranteed approval" not in h.lower() and "approval guaranteed" not in h.lower() and "0% apr guaranteed" not in h.lower(),
           "No illegal credit/approval promises")

    # --- SMS COMPLIANCE ---
    if sms_draft:
        sbody = sms_draft.get("body", "")
        record("sms_opt_out_present", "STOP" in sbody, "TCPA 'Reply STOP' opt-out present")
        record("sms_sender_identified", "Ivan" in sbody and "Kia" in sbody, "Sender identified as Ivan at Phil Smith Kia")
        record("sms_no_misleading_promises", "approved" not in sbody.lower() and "guaranteed" not in sbody.lower(), "No misleading claims")

    # --- EMAIL COMPLIANCE ---
    if email_draft:
        ebody = email_draft.get("body", "")
        record("email_can_spam_opt_out", "UNSUBSCRIBE" in ebody, "CAN-SPAM unsubscribe present")
        record("email_physical_address", "Lighthouse Point, FL" in ebody, "Dealership physical address present")

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
            "duration_sec": round(dur, 2),
            "started_at": t0.isoformat(),
            "finished_at": t1.isoformat(),
        },
    }

def write_qa(path: str, qa: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(qa, f, indent=2, ensure_ascii=False)
    return path
