#!/usr/bin/env python3
"""
Generate 10 personalized landing pages for pilot campaign
"""

import json
import os

# Pilot leads data
PILOT_LEADS = [
    {
        "nome": "GIOVANNI SCHIAVINATO",
        "primeiro_nome": "Giovanni",
        "telefone": "(561) 485-9147",
        "veiculo_atual": "2023 Kia Stinger",
        "data_vencimento": "08/27/2028",
        "pagamento_atual": 789,
        "pagamento_novo": 139,
        "economia": 650,
        "veiculo_novo": "2027 Kia Telluride",
        "arquivo": "giovanni-schiavinato-telluride.html",
        "destaque": "Upgrade de $650/mês"
    },
    {
        "nome": "KIMBERLI SEXTON",
        "primeiro_nome": "Kimberli",
        "telefone": "(305) 316-0735",
        "veiculo_atual": "2025 Kia Sorento",
        "data_vencimento": "09/01/2030",
        "pagamento_atual": 770,
        "pagamento_novo": 162,
        "economia": 608,
        "equity": "$3,415",
        "veiculo_novo": "2026 Kia Sorento",
        "arquivo": "kimberli-sexton-sorento.html",
        "destaque": "Economia de $608/mês + Equity na mão"
    },
    {
        "nome": "PATRICIA NESSLER",
        "primeiro_nome": "Patricia",
        "telefone": "(954) 205-7988",
        "veiculo_atual": "2020 Kia Sportage",
        "data_vencimento": "09/15/2028",
        "pagamento_atual": 357,
        "pagamento_novo": 0,
        "economia": 357,
        "equity": "$900",
        "veiculo_novo": "2022 Kia Sportage",
        "arquivo": "patricia-nessler-sportage.html",
        "destaque": "Praticamente GRATUITO com seu trade-in"
    },
    {
        "nome": "TERRI GERMAIN-WILLIAMS",
        "primeiro_nome": "Terri",
        "telefone": "(917) 699-9656",
        "veiculo_atual": "2023 Kia Carnival",
        "data_vencimento": "06/04/2030",
        "pagamento_atual": 904,
        "pagamento_novo": 249,
        "economia": 655,
        "equity": "$4,875",
        "veiculo_novo": "2026 Kia Carnival",
        "arquivo": "terri-germain-williams-carnival.html",
        "destaque": "Economia de $655/mês + $4.8k na mão"
    },
    {
        "nome": "JENNIFER GARBIZO",
        "primeiro_nome": "Jennifer",
        "telefone": "(954) 729-4611",
        "veiculo_atual": "2023 Kia Sorento",
        "data_vencimento": "10/18/2028",
        "pagamento_atual": 657,
        "pagamento_novo": 8,
        "economia": 649,
        "equity": "$8,000",
        "veiculo_novo": "2026 Kia Sorento",
        "arquivo": "jennifer-garbizo-sorento.html",
        "destaque": "Praticamente GRÁTIS + $8k de equity!"
    },
    {
        "nome": "LOUIS GREEN",
        "primeiro_nome": "Louis",
        "telefone": "(954) 999-2360",
        "veiculo_atual": "2021 Kia Forte",
        "data_vencimento": "05/15/2024",
        "pagamento_atual": 323,
        "pagamento_novo": 323,
        "economia": 0,
        "urgencia": "JÁ VENCEU",
        "veiculo_novo": "2026 Kia K4",
        "arquivo": "louis-green-k4.html",
        "destaque": "Upgrade a mesmo preço - carro novo!"
    },
    {
        "nome": "JASON BOURQUE",
        "primeiro_nome": "Jason",
        "telefone": "(954) 682-1453",
        "veiculo_atual": "2020 Kia Forte",
        "data_vencimento": "08/01/2023",
        "pagamento_atual": 380,
        "pagamento_novo": 380,
        "economia": 0,
        "urgencia": "JÁ VENCEU",
        "veiculo_novo": "2026 Kia K4",
        "arquivo": "jason-bourque-k4.html",
        "destaque": "Mesmo preço, carro NOVO"
    },
    {
        "nome": "CHRISTOPHER NOVOA",
        "primeiro_nome": "Christopher",
        "telefone": "(862) 324-4441",
        "veiculo_atual": "2020 Kia Telluride",
        "data_vencimento": "02/06/2024",
        "pagamento_atual": 893,
        "pagamento_novo": 893,
        "economia": 0,
        "urgencia": "JÁ VENCEU",
        "veiculo_novo": "2027 Kia Telluride",
        "arquivo": "christopher-novoa-telluride.html",
        "destaque": "Upgrade modelo 2027 - mesmo preço"
    },
    {
        "nome": "JESSE KOVEN",
        "primeiro_nome": "Jesse",
        "telefone": "(954) 573-4609",
        "veiculo_atual": "2019 Kia Forte",
        "data_vencimento": "05/26/2025",
        "pagamento_atual": 427,
        "pagamento_novo": 427,
        "economia": 0,
        "urgencia": "VENCE EM MESES",
        "veiculo_novo": "2026 Kia K4",
        "arquivo": "jesse-koven-k4.html",
        "destaque": "Carro de 2019 → 2026 NOVO"
    },
    {
        "nome": "ROSALYN YOUNG",
        "primeiro_nome": "Rosalyn",
        "telefone": "(754) 235-8850",
        "veiculo_atual": "2017 Kia Sportage",
        "data_vencimento": "04/28/2021",
        "pagamento_atual": 537,
        "pagamento_novo": 537,
        "economia": 0,
        "urgencia": "JÁ VENCEU",
        "veiculo_novo": "2026 Kia Sportage",
        "arquivo": "rosalyn-young-sportage.html",
        "destaque": "7 anos → NOVO (2026) - sem dor de cabeça"
    }
]

def generate_html(lead):
    """Generate personalized HTML landing page"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ivan Preview - {lead['primeiro_nome']} Upgrade</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#080b10;
  --panel:#111722;
  --line:#253044;
  --text:#f8fafc;
  --soft:#b8c2d2;
  --muted:#7d889b;
  --red:#c60f0f;
  --green:#16a34a;
  --phone:#E5E7EB;
  --gold:#d6b25e;
}}
html,body{{min-height:100%;background:var(--bg);color:var(--text)}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:hidden}}
a{{color:inherit}}
a.phone,a.phone:link,a.phone:visited,a.phone:hover,a.phone:active{{color:var(--phone);text-decoration:none}}
.page{{max-width:1120px;margin:0 auto;padding:18px 16px 92px}}
.hero{{display:grid;gap:16px;min-height:calc(100svh - 92px);align-content:start}}
.topline{{display:flex;justify-content:space-between;align-items:center;gap:12px;color:var(--soft);font-size:12px;letter-spacing:.08em;text-transform:uppercase}}
.brand{{color:#fff;font-weight:800}}
.phone-pill{{display:inline-flex;align-items:center;gap:8px;padding:9px 12px;border:1px solid rgba(229,231,235,.24);border-radius:999px;background:rgba(229,231,235,.07);font-weight:800;white-space:nowrap}}
.hero-card{{position:relative;overflow:hidden;border:1px solid var(--line);border-radius:22px;background:linear-gradient(145deg,#151d2a 0%,#0d121b 58%,#11090a 100%);padding:24px 18px 18px;box-shadow:0 24px 70px rgba(0,0,0,.32)}}
.hero-card:before{{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(198,15,15,.18),transparent 45%),radial-gradient(circle at 88% 12%,rgba(214,178,94,.2),transparent 28%);pointer-events:none}}
.hero-content{{position:relative;z-index:1}}
.eyebrow{{display:inline-flex;align-items:center;gap:8px;margin-bottom:14px;color:#ffd9d9;font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase}}
.dot{{width:8px;height:8px;border-radius:50%;background:var(--red);box-shadow:0 0 0 5px rgba(198,15,15,.15)}}
h1{{font-size:34px;line-height:1.05;letter-spacing:0;font-weight:900;max-width:760px}}
.highlight{{color:#4ade80}}
.sub{{margin-top:13px;color:var(--soft);font-size:16px;line-height:1.5;max-width:680px}}
.numbers{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:18px}}
.metric{{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.11);border-radius:14px;padding:13px}}
.metric span{{display:block;color:var(--muted);font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase}}
.metric b{{display:block;margin-top:3px;font-size:22px;line-height:1.1}}
.metric.savings{{background:rgba(22,163,74,.14);border-color:rgba(74,222,128,.34)}}
.metric.savings b{{color:#4ade80}}
.actions{{display:grid;grid-template-columns:1fr;gap:10px;margin-top:18px}}
.btn{{display:flex;align-items:center;justify-content:center;min-height:52px;border-radius:13px;text-decoration:none;font-size:15px;font-weight:900;text-align:center}}
.btn.primary{{background:var(--green);color:#fff;box-shadow:0 14px 32px rgba(22,163,74,.24)}}
.btn.secondary{{border:1px solid rgba(229,231,235,.22);background:rgba(229,231,235,.08);color:var(--phone)}}
.quick-grid{{display:grid;grid-template-columns:1fr;gap:12px}}
.panel{{border:1px solid var(--line);border-radius:18px;background:var(--panel);padding:16px}}
.label{{font-size:11px;color:var(--muted);font-weight:900;letter-spacing:.12em;text-transform:uppercase;margin-bottom:10px}}
.vehicle{{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}}
.vehicle h2{{font-size:20px;line-height:1.15}}
.tag{{color:#0b111a;background:var(--gold);border-radius:999px;padding:7px 10px;font-size:12px;font-weight:900;white-space:nowrap}}
.meta{{margin-top:7px;color:var(--soft);font-size:13px;line-height:1.45}}
.models{{display:grid;gap:9px}}
.model{{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:11px 12px;border:1px solid rgba(255,255,255,.09);border-radius:12px;background:rgba(255,255,255,.04);text-decoration:none}}
.model strong{{display:block;font-size:14px}}
.model span{{display:block;color:var(--muted);font-size:12px;margin-top:2px}}
.model b{{color:#fff;font-size:13px;white-space:nowrap}}
.trust{{color:var(--soft);font-size:13px;line-height:1.5}}
.rep{{display:flex;align-items:center;gap:12px;margin-top:13px}}
.avatar{{display:grid;place-items:center;width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,var(--red),#6f0707);font-weight:900}}
.rep b{{display:block}}
.rep span{{display:block;color:var(--soft);font-size:12px;margin-top:2px}}
.sticky{{position:fixed;left:0;right:0;bottom:0;z-index:20;padding:12px 14px;background:rgba(8,11,16,.96);border-top:1px solid var(--line);backdrop-filter:blur(14px)}}
.sticky-inner{{max-width:520px;margin:0 auto;display:grid;grid-template-columns:1fr 112px;gap:9px}}
.footer{{padding:20px 4px;color:var(--muted);font-size:11px;line-height:1.55;text-align:center}}
@media (min-width:780px){{
  .page{{padding:28px 28px 34px}}
  .hero{{min-height:auto;grid-template-columns:minmax(0,1.25fr) minmax(320px,.75fr);align-items:start}}
  .hero-card{{grid-row:1 / span 2;padding:34px}}
  h1{{font-size:52px}}
  .actions{{grid-template-columns:1fr 170px;max-width:520px}}
  .quick-grid{{align-self:stretch}}
  .sticky{{display:none}}
  .footer{{text-align:left;grid-column:1 / -1}}
}}
</style>
</head>
<body>
<main class="page">
  <section class="hero" aria-label="{lead['primeiro_nome']} upgrade preview">
    <div class="hero-card">
      <div class="hero-content">
        <div class="topline">
          <span class="brand">Phil Smith Kia</span>
          <a class="phone phone-pill" href="tel:+19548600537">(954) 860-0537</a>
        </div>
        <div class="eyebrow"><span class="dot"></span>{lead['destaque']}</div>
        <h1>{lead['primeiro_nome']}, seu <span class="highlight">{lead['veiculo_atual']}</span> tem uma oportunidade.</h1>
        <p class="sub">Baseado em dados AutoAlert, você pode fazer upgrade pra um <strong>{lead['veiculo_novo']}</strong> por <strong>${lead['pagamento_novo']:.0f}/mês</strong> (economiza ${lead['economia']:.0f}/mês em relação aos ${lead['pagamento_atual']:.0f} que você paga agora).</p>

        <div class="numbers" aria-label="Payment comparison">
          <div class="metric"><span>Pagamento Atual</span><b>${lead['pagamento_atual']}/mês</b></div>
          <div class="metric savings"><span>Estimado Novo</span><b>${lead['pagamento_novo']}/mês</b></div>
        </div>

        <div class="actions">
          <a class="btn primary" href="tel:+19548600537">Agenda Rápido</a>
          <a class="btn secondary phone" href="tel:+19548600537">Ligar Ivan</a>
        </div>
      </div>
    </div>

    <div class="quick-grid">
      <section class="panel">
        <div class="label">Veículo Atual</div>
        <div class="vehicle">
          <div>
            <h2>{lead['veiculo_atual']}</h2>
            <p class="meta">{lead['primeiro_nome']} · Vence {lead['data_vencimento']}</p>
          </div>
          <span class="tag">Time-sensitive</span>
        </div>
      </section>

      <section class="panel">
        <div class="label">Upgrade Sugerido</div>
        <div class="models">
          <div style="text-align:center;padding:12px;color:var(--soft)">
            <strong style="display:block;color:var(--text);font-size:18px">{lead['veiculo_novo']}</strong>
            <p style="font-size:12px;margin-top:4px">Carro novo, todas as garantias</p>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="label">Como funciona</div>
        <p class="trust">Traz seu {lead['veiculo_atual'].split()[-1]} pra fazer uma avaliação rápida. Checamos o estado, manutenção, e te mostramos a proposta. Sem pressão—se não funcionar pra você agora, tudo bem.</p>
        <div class="rep">
          <div class="avatar">IS</div>
          <div><b>Ivan Silva</b><span>Sales · Phil Smith Kia · <a class="phone" href="tel:+19548600537">(954) 860-0537</a></span></div>
        </div>
      </section>
    </div>

    <p class="footer">Todos os valores são estimados usando dados AutoAlert e não são uma oferta garantida. O pagamento real, multas por manutenção, excesso de quilometragem, e outras condições dependem da avaliação do veículo, condições de mercado, e sua aprovação. Esta proposta personalizada foi gerada para {lead['primeiro_nome']} verificar antes da data de vencimento.</p>
  </section>
</main>

<div class="sticky" aria-label="Quick actions">
  <div class="sticky-inner">
    <a class="btn primary" href="tel:+19548600537">Agenda Rápido</a>
    <a class="btn secondary phone" href="tel:+19548600537">Ligar Ivan</a>
  </div>
</div>
</body>
</html>
"""
    return html

# Generate all 10 pages
output_dir = "/tmp/autoalert-test"
generated = []

for lead in PILOT_LEADS:
    html_content = generate_html(lead)
    file_path = os.path.join(output_dir, lead['arquivo'])

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    generated.append({
        "arquivo": lead['arquivo'],
        "nome": lead['nome'],
        "caminho": file_path
    })
    print(f"✅ Gerado: {lead['arquivo']}")

print(f"\n📋 TOTAL: {len(generated)} landing pages criadas")
print(f"📁 Localização: {output_dir}")

# Save manifest
manifest = {
    "pilot_10_campaign": {
        "criado_em": "2026-09-09",
        "total_paginas": len(generated),
        "paginas_geradas": generated
    }
}

manifest_path = os.path.join(output_dir, "PILOT_10_MANIFEST.json")
with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=2)

print(f"✅ Manifesto salvo: {manifest_path}")
