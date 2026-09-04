"""kai_voice_landing / audio_engine.py

Audio backend for the Kai voice+landing pipeline.

Voice cloning backend (verified working 2026-08-28):
  CosyVoice3 (Apache-2.0, MLX on Apple Silicon) via cosyvoice_clone.py.
  Replaces the old Coqui XTTS v2 path, which was non-commercial licensed
  (CPML) and broken in this env (numpy 2.x + missing weights).

Per-client mode speaks the customer-specific 25-40s script in the approved
cloned voice (Ivan male / Zaramaya female), opposite-gender per Ivan override.

The pipeline NEVER uses edge-tts / Fred / Samantha / system voices.
"""
import os
import shutil
import subprocess
from dataclasses import dataclass

from .registry import select_voice, is_forbidden_voice, APPROVED_CLONE

AUDIO_MIN_SEC = 25.0
AUDIO_MAX_SEC = 40.0
AUDIO_MIN_SIZE = 1024


@dataclass
class AudioResult:
    path: str
    mode: str            # cosyvoice_per_client | approved_clone_copy | unavailable | forbidden
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
    """Generate the customer-audio file and return an AudioResult."""
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{lead.slug}.mp3")

    voice = select_voice(lead.gender)

    # 0) Hard guard: unknown gender -> no audio + BLOCK_SEND
    if voice["mode"] == "ask_ivan":
        return AudioResult(path=out_path, mode="unavailable", duration_sec=0.0,
                           size_bytes=0, voice_label=voice["label"],
                           detail="unknown gender -> ask Ivan; no audio generated (BLOCK_SEND)")

    # 1) Try per-client CosyVoice3 clone (fully compliant 25-40s path)
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
        detail_cosy = f"CosyVoice3 failed: {type(e).__name__}: {e}"

    # 2) Fallback: approved fixed clone copy (~6s hero audio, cannot meet 25-40s)
    src = voice["file"]
    if not src or not os.path.isfile(src):
        return AudioResult(path=out_path, mode="unavailable", duration_sec=0.0,
                           size_bytes=0, voice_label=voice["label"],
                           detail=f"approved clone source missing: {src}")
    shutil.copyfile(src, out_path)
    dur = _ffprobe_duration(out_path)
    extra = " (CosyVoice3 per-client unavailable -> using approved fixed clone)" if "detail_cosy" in dir() else ""
    return AudioResult(path=out_path, mode="approved_clone_copy", duration_sec=dur,
                       size_bytes=os.path.getsize(out_path),
                       voice_label=voice["label"],
                       detail=f"copied approved clone {os.path.basename(src)}{extra}")

