"""kai_voice_landing / cosyvoice_clone.py

Per-client cloned-voice audio via CosyVoice3 (Apache-2.0, MLX on Apple Silicon).

WHY THIS REPLACES xtts_clone.py:
  - Coqui XTTS v2 is licensed non-commercial (CPML) -> blocks dealership use.
  - CosyVoice3 (FunAudioLLM, Apache-2.0) is commercially permitted.
  - MLX build (mlx-community/Fun-CosyVoice3-0.5B-2512-fp16) runs on MPS, no CUDA,
    no 1.8GB XTTS weight download, supports Portuguese.
  - Verified working 2026-08-28: cloned Ivan's voice from 12s ref_wav -> 22.8s PT audio.

Environment (verified):
  venv: /Users/clawbotlocal/.venvs/stableaudio  (torch 2.7.1 + transformers 5.9 + mlx-audio-plus)
  HF_HOME: /Users/clawbotlocal/.cache/hf  (weights cached after first fetch)
  ref_audio MUST be 24kHz WAV, <=30s, clean speech.

Usage: clone_per_client(lead, voice, script_text, out_path) -> out_path (mp3)
"""
import os
import subprocess
import sys
import tempfile

# Use the verified venv python for the actual generation (it has mlx-audio-plus).
_STABLEAUDIO_PY = "/Users/clawbotlocal/.venvs/stableaudio/bin/python"
_MODEL = "mlx-community/Fun-CosyVoice3-0.5B-2512-fp16"

# Known reference clips (clean speech, PT-BR). These are the approved voices.
REF_WAV = {
    "M": "/Users/clawbotlocal/voice_clone/ivan_ref.wav",        # Ivan (male)
    "F": "/Users/clawbotlocal/Desktop/Mp3ZARAMAYA/MP3ZARAMAYA.mp3",  # Zaramaya (female)
}
# ref_text used for zero-shot alignment (timbre still clones from audio).
REF_TEXT = {
    "M": "Eu sou o Ivan, da Phil Smith Kia, aqui para te ajudar com sua troca de carro.",
    "F": "Ola, eu sou a Zara, da Phil Smith Kia, tudo bem?",
}


def _ref_to_wav_24k(src: str) -> str:
    """Return a clean 24kHz mono WAV slice (~12s, middle) for CosyVoice3.

    CosyVoice3 wants <=30s clean speech. Long MP3s (e.g. Zara's 34s clip) may
    contain music/fades at the edges, so we take a 12s middle slice.
    """
    dst = tempfile.mkstemp(suffix=".wav")[1]
    # probe duration, take middle 12s
    try:
        dur = float(subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", src]).decode().strip())
    except Exception:
        dur = 0.0
    if dur > 14:
        start = max(0.0, (dur - 12.0) / 2.0)
        ss = ["-ss", f"{start:.1f}"]
    else:
        ss = []
    subprocess.run(["ffmpeg", "-y", "-i", src, *ss, "-t", "12", "-ar", "24000",
                    "-ac", "1", dst], capture_output=True, timeout=60, check=True)
    return dst


def clone_per_client(lead, voice: dict, script_text: str, out_path: str) -> str:
    """Generate a per-client cloned-voice MP3. Returns out_path on success."""
    if not script_text:
        raise ValueError("per-client script required for CosyVoice3")
    g = (voice.get("gender_key") or voice.get("gender") or "M").upper()
    ref_src = REF_WAV.get(g) or REF_WAV.get("M")
    if not ref_src or not os.path.isfile(ref_src):
        raise ValueError(f"CosyVoice3 reference missing: {ref_src}")
    ref_wav = _ref_to_wav_24k(ref_src)
    ref_text = REF_TEXT.get(g, "")

    # Write a tiny driver script and run it under the verified venv.
    drv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cosy_run.py")
    with open(drv, "w") as f:
        f.write(_DRIVER.format(
            text=script_text.replace('"', "'"),
            model=_MODEL,
            ref=ref_wav,
            reftext=ref_text,
            out=out_path,
        ))
    env = dict(os.environ, HF_HOME="/Users/clawbotlocal/.cache/hf")
    r = subprocess.run([_STABLEAUDIO_PY, drv], capture_output=True, text=True,
                       timeout=600, env=env)
    if r.returncode != 0 or not (os.path.isfile(out_path) and os.path.getsize(out_path) > 0):
        raise RuntimeError(f"CosyVoice3 failed: {r.stderr[-500:]}")
    return out_path


_DRIVER = '''import sys, subprocess, os
from mlx_audio.tts.generate import generate_audio
generate_audio(
    text="{text}",
    model="{model}",
    ref_audio="{ref}",
    ref_text="{reftext}",
    stt_model=None,
    language="Portuguese",
    file_prefix=os.path.splitext("{out}")[0],
    audio_format="wav",
)
wav = os.path.splitext("{out}")[0] + "_000.wav"
if os.path.isfile(wav):
    subprocess.run(["ffmpeg","-y","-i",wav,"-ar","24000","-b:a","72k","{out}"],
                   capture_output=True, timeout=120)
    os.remove(wav)
'''


if __name__ == "__main__":
    # quick self-test
    out = "/tmp/_cosy_selftest.mp3"
    class L: gender_key = "M"; gender = "male"
    print(clone_per_client(L(), {"gender_key": "M", "gender": "male"},
                            "Teste de voz clonada Ivan.", out))
