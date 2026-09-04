"""
kai_voice_landing / pipeline.py  -- Kai orchestrator

Runs the FULL pipeline for one lead (internal test only, never customer send):
  lead -> landing HTML -> audio (cloned voice) -> full QA -> BLOCK_SEND gate.

Usage:
  python3 -m kai_voice_landing.pipeline \
      --slug maria-silva --name "Maria Silva" --gender F --lang pt \
      --car "2024 Kia Sportage" --equity "$18,400" \
      --out-dir /Users/clawbotlocal/autoalert-pages/kai_test \
      --audio-mode-report

It writes:
  <out-dir>/<slug>.html
  <out-dir>/audios/<slug>.mp3
  <out-dir>/<slug>_qa.json
and prints the QA verdict + BLOCK_SEND decision.
"""
import argparse
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kai_voice_landing import (
    Lead, build_landing_html, generate_audio, run_qa, write_qa,
)

SCRIPT_PER_CLIENT_PT = (
    "{name} — nosso sistema mostra que seu {car} pode estar em boa posição "
    "de troca, com valor estimado perto de {equity}. Essa é a estimativa. "
    "O número real vem de uma avaliação de vinte minutos, sem compromisso. "
    "Traga o {car} na loja e um especialista confere estado, pneus e histórico. "
    "Se não estiver bom, você fica com o carro. Meu nome é Ivan, da Phil Smith Kia. "
    "Pode me ligar ou mandar mensagem no (954) 860-0537. "
    "Mensagem preparada pelo assistente de IA do Ivan."
)


def run(lead: Lead, out_dir: str, audio_mode_only: bool = False) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    audios_dir = os.path.join(out_dir, "audios")
    os.makedirs(audios_dir, exist_ok=True)

    # 1) per-client script (only used by XTTS per-client mode)
    script = SCRIPT_PER_CLIENT_PT.format(
        name=lead.name, equity=lead.equity_estimate, car=lead.current_vehicle
    )
    lead.script = script

    # 2) audio (approved clone copy or per-client XTTS)
    audio = generate_audio(lead, audios_dir, script)
    audio_dict = {
        "path": audio.path, "mode": audio.mode, "duration_sec": audio.duration_sec,
        "size_bytes": audio.size_bytes, "voice_label": audio.voice_label,
    }

    # 3) landing HTML (audio src uses ../audios/<slug>.mp3)
    audio_src = f"../audios/{lead.slug}.mp3"
    html = build_landing_html(lead, audio_src)
    html_path = os.path.join(out_dir, f"{lead.slug}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # 4) QA
    qa = run_qa(audio_dict, html, lead, mode=audio.mode)
    qa_path = os.path.join(out_dir, f"{lead.slug}_qa.json")
    write_qa(qa_path, qa)

    # 5) BLOCK_SEND
    blocked = qa["verdict"] != "PASS"
    return {
        "lead": lead.name, "slug": lead.slug, "gender": lead.gender,
        "audio": audio_dict, "html_path": html_path, "qa_path": qa_path,
        "qa_verdict": qa["verdict"], "blocked": blocked,
        "failures": qa["failures"], "qa": qa,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--slug", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--gender", required=True, choices=["M", "F", "unknown"])
    p.add_argument("--lang", default="pt", choices=["pt", "en"])
    p.add_argument("--car", default="2024 Kia Sportage")
    p.add_argument("--equity", default="$18,400")
    p.add_argument("--payment", default="$XXX/mo")
    p.add_argument("--out-dir", default="/Users/clawbotlocal/autoalert-pages/kai_test")
    args = p.parse_args()

    lead = Lead(slug=args.slug, name=args.name, gender=args.gender, lang=args.lang,
                current_vehicle=args.car, equity_estimate=args.equity)
    res = run(lead, args.out_dir)
    print(json.dumps({k: v for k, v in res.items() if k != "qa"}, indent=2, ensure_ascii=False))
    print("\n[QA VERDICT]", res["qa_verdict"])
    if res["blocked"]:
        print("[BLOCK_SEND] Not sent. Failures:", res["failures"])
    else:
        print("[READY] Passed QA. SEND ONLY AFTER Ivan approval (test link to Ivan).")
    sys.exit(0 if not res["blocked"] else 2)


if __name__ == "__main__":
    main()
