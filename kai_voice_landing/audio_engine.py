"""
kai_voice_landing / audio_engine.py

Audio backend for the Kai voice+landing pipeline.

Baseline voice (Approved 2026-09-04):
  Chatterbox Turbo (200 WPM, pitch-preserving rubberband, MIT license).
  Opposite-gender rule:
    - F lead -> Ivan male voice
    - M lead -> Zara female voice

Fallbacks:
  - CosyVoice3 per-client clone
  - Approved fixed clone copy
"""
import os
import shutil
import subprocess
import json
from dataclasses import dataclass
from pathlib import Path

from .registry import select_voice, is_forbidden_voice, APPROVED_CLONE

AUDIO_MIN_SEC = 25.0
AUDIO_MAX_SEC = 40.0
AUDIO_MIN_SIZE = 1024

TURBO_SCRIPT = Path("/Users/clawbotlocal/.hermes/profiles/the-greatest/skills/sales-agent/sales_landing_builder/scripts/kai_voice_pipeline.py")
TURBO_PYTHON = Path("/Users/clawbotlocal/.hermes/voice-sandbox/chatterbox/bin/python")

@dataclass
class AudioResult:
    path: str
    mode: str            # chatterbox_turbo_200wpm | cosyvoice_per_client | approved_clone_copy | unavailable
    duration_sec: float
    size_bytes: int
    voice_label: str
    detail: str

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

def generate_audio(lead, out_dir: str, script_text: str = "") -> AudioResult:
    """Generate customer audio using the approved Chatterbox Turbo baseline."""
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{lead.slug}.mp3")

    voice = select_voice(lead.gender)

    # 0) Hard guard: unknown gender -> no audio + BLOCK_SEND
    if voice["mode"] == "ask_ivan":
        return AudioResult(path=out_path, mode="unavailable", duration_sec=0.0,
                           size_bytes=0, voice_label=voice["label"],
                           detail="unknown gender -> ask Ivan; no audio generated (BLOCK_SEND)")

    # 1) Try Chatterbox Turbo (Approved baseline)
    if TURBO_SCRIPT.exists() and TURBO_PYTHON.exists() and script_text:
        try:
            cmd = [
                str(TURBO_PYTHON), str(TURBO_SCRIPT),
                "--lead-name", lead.name,
                "--lead-gender", lead.gender,
                "--campaign", "kai_bdc",
                "--slug", lead.slug,
                "--script", script_text,
                "--out-dir", out_dir,
                "--engine", "turbo",
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if proc.returncode == 0 and os.path.isfile(out_path) and os.path.getsize(out_path) > AUDIO_MIN_SIZE:
                dur = _ffprobe_duration(out_path)
                return AudioResult(
                    path=out_path,
                    mode="chatterbox_turbo_200wpm",
                    duration_sec=dur,
                    size_bytes=os.path.getsize(out_path),
                    voice_label=voice["label"],
                    detail=f"Chatterbox Turbo 200wpm baseline OK ({dur:.1f}s)"
                )
        except Exception as e:
            detail_turbo = f"Turbo failed: {e}"

    # 2) Fallback: CosyVoice3 clone
    try:
        from .cosyvoice_clone import clone_per_client
        cloned = clone_per_client(lead, voice, script_text, out_path)
        if cloned and os.path.isfile(cloned) and os.path.getsize(cloned) > 0:
            dur = _ffprobe_duration(cloned)
            return AudioResult(path=cloned, mode="cosyvoice_per_client",
                               duration_sec=dur, size_bytes=os.path.getsize(cloned),
                               voice_label=voice["label"],
                               detail=f"CosyVoice3 per-client clone OK ({dur:.1f}s)")
    except Exception as e:
        detail_cosy = f"CosyVoice3 failed: {e}"

    # 3) Fallback: approved fixed clone copy
    src = voice["file"]
    if not src or not os.path.isfile(src):
        return AudioResult(path=out_path, mode="unavailable", duration_sec=0.0,
                           size_bytes=0, voice_label=voice["label"],
                           detail=f"approved clone source missing: {src}")
    shutil.copyfile(src, out_path)
    dur = _ffprobe_duration(out_path)
    return AudioResult(path=out_path, mode="approved_clone_copy", duration_sec=dur,
                       size_bytes=os.path.getsize(out_path),
                       voice_label=voice["label"],
                       detail=f"copied approved clone {os.path.basename(src)}")
