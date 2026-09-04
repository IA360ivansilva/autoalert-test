"""
kai_voice_landing / xtts_clone.py

Per-client cloned-voice audio via Coqui XTTS v2.

Speaks the per-client script (customer name + car + offer) in the approved
cloned voice. Requires coqui-tts importable (numpy<1.27) AND the XTTS_v2
weights reachable (HF_TOKEN + LFS CDN). If anything is missing this raises,
and audio_engine falls back to the approved fixed clone.

Reference speakers (from registry.XTTS_REFERENCE):
  M -> /Users/clawbotlocal/voice_clone/ivan_ref.wav
  F -> /Users/clawbotlocal/Desktop/Mp3ZARAMAYA/MP3ZARAMAYA.mp3
"""
import os
import tempfile
import subprocess
from TTS.api import TTS

_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"


def _to_wav_24k_mono(src_path: str) -> str:
    """Return a 24kHz mono WAV path for the reference speaker (XTTS needs WAV)."""
    if src_path.lower().endswith(".wav"):
        # ensure 24k mono
        dst = src_path
    else:
        dst = tempfile.mktemp(suffix=".wav")
        subprocess.run(
            ["ffmpeg", "-y", "-i", src_path, "-ar", "24000", "-ac", "1", dst],
            capture_output=True, timeout=60, check=True,
        )
    return dst


_tts = None


def _get_tts():
    global _tts
    if _tts is None:
        _tts = TTS(_MODEL)
    return _tts


def clone_per_client(lead, voice: dict, script_text: str, out_path: str) -> str:
    from .registry import XTTS_REFERENCE
    if not script_text:
        raise ValueError("per-client script required for XTTS")
    ref = XTTS_REFERENCE.get(voice["gender_key"]) or XTTS_REFERENCE.get(voice["gender"])
    if not ref:
        raise ValueError("no XTTS reference for gender")
    speaker_wav = ref.get("speaker_wav") or ref.get("speaker_mp3")
    if not speaker_wav or not os.path.isfile(speaker_wav):
        raise ValueError(f"XTTS reference missing: {speaker_wav}")
    wav = _to_wav_24k_mono(speaker_wav)
    tts = _get_tts()
    tmp = out_path
    if not tmp.lower().endswith(".wav"):
        tmp = out_path + ".tmp.wav"
    tts.tts_to_file(
        text=script_text,
        speaker_wav=wav,
        language="pt" if lead.lang == "pt" else "en",
        file_path=tmp,
    )
    # encode to mp3 for the page
    subprocess.run(
        ["ffmpeg", "-y", "-i", tmp, "-ar", "24000", "-b:a", "64k", out_path],
        capture_output=True, timeout=120, check=True,
    )
    if tmp != out_path and os.path.isfile(tmp):
        os.remove(tmp)
    return out_path
