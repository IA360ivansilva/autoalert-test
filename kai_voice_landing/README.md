# Kai Voice + Landing Pipeline

Integración del pipeline de voz con generación de landing pages personalizadas
para Phil Smith Kia. Kai orquestra: lead → landing → áudio (voz clonada) → QA → BLOCK_SEND.

## Módulos (pasta `kai_voice_landing/`)
- `registry.py` — voz aprovada (Ivan♂ / Zaramaya♀), mapa de gender, cores/CTA, `Lead`.
- `landing.py` — gera HTML premium mobile-first (telefone #E5E7EB, CTA verde #16a34a, avatar IS, modelos equivalentes, disclosure IA). PT/EN.
- `audio_engine.py` — seleciona voz; tenta XTTS per-client, cai no clone fixo aprovado. NUNCA edge-tts/Fred/Samantha.
- `xtts_clone.py` — clone XTTS v2 por cliente (precisa numpy<1.27 + HF_TOKEN + CDN LFS).
- `qa.py` — gate de QA; qualquer falha → BLOCK_SEND.
- `pipeline.py` — orquestrador end-to-end (teste interno, nunca envia).

## Gender map (APROVADO por Ivan — especificação de campanha)
- F (cliente feminino) → Zaramaya (female clone)
- M (cliente masculino) → Ivan (male clone)
- unknown → pergunta Ivan / sem áudio + BLOCK_SEND

> NOTA: isto é o mapa *same-gender* dos assets aprovados (cloned-voice-and-dispatch-spec.md),
> que difere da nota "opposite gender" do corpo do kanban. Kai segue o spec aprovado; confirmar com Ivan.

## Como rodar (teste interno — Ivan só)
```
cd /Users/clawbotlocal/autoalert-pages
python3 -m kai_voice_landing.pipeline \
  --slug maria-silva --name "Maria Silva" --gender F --lang pt \
  --car "2024 Kia Sportage" --equity '$18,400' \
  --out-dir /Users/clawbotlocal/autoalert-pages/kai_test
```
Saída: `<out>/<slug>.html`, `<out>/audios/<slug>.mp3`, `<out>/<slug>_qa.json`.
Exit 0 = PASS (pronto p/ aprovação do Ivan, NÃO envia). Exit 2 = BLOCK_SEND (não envia).

## BLOCK_SEND (regra HARD)
Se QA falha QUALQUER check → não envia. Log do motivo em `<slug>_qa.json`. Ivan decide corrigir ou abortar.

## Bloqueio conhecido (27/08) — áudio por cliente 25-40s
O ambiente NÃO consegue gerar voz clonada por cliente 25-40s hoje:
- `coqui-tts` (XTTS v2) quebra com numpy 2.0.2 (librosa/_ARRAY_API). Precisa venv com numpy<1.27.
- Pesos XTTS exigem HF_TOKEN (401 sem token) e o CDN LFS falha DNS aqui.
- Os clones fixos aprovados (`ivan_tts`/`zaramaya_tts`) têm ~6s → não aguentam script por cliente.

Por isso o pipeline BLOCK_SENDa em `audio_per_client_25_40s` até Ivan decidir:
(a) upgrade ElevenLabs (clone por cliente), ou (b) XTTS com numpy pinado + HF_TOKEN.
Enquanto isso, as landings usam o clone fixo aprovado como áudio hero (igual à campanha autoalert-test).
