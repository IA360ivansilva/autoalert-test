#!/usr/bin/env python3
"""
Generate personalized Ivan's Agent landing pages from AutoAlert CSV
Usage: python3 generate-lead-pages.py --csv /path/to/csv --limit 5
"""

import csv
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Template for landing pages
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ivan Preview - {customer_first_name} {vehicle_year} {vehicle_model} Opportunity</title>
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
.metric.highlight{{background:rgba(22,163,74,.14);border-color:rgba(74,222,128,.34)}}
.metric.highlight b{{color:#4ade80}}
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
  <section class="hero" aria-label="{customer_first_name} opportunity preview">
    <div class="hero-card">
      <div class="hero-content">
        <div class="topline">
          <span class="brand">Phil Smith Kia</span>
          <a class="phone phone-pill" href="tel:19548600537">(954) 860-0537</a>
        </div>
        <div class="eyebrow"><span class="dot"></span>{opportunity_label}</div>
        <h1>{headline}</h1>
        <p class="sub">{message}</p>

        <div class="numbers" aria-label="Key comparison">
          {metrics_html}
        </div>

        <div class="actions">
          <a class="btn primary" href="tel:19548600537">Talk to Ivan</a>
          <a class="btn secondary phone" href="tel:19548600537">Call</a>
        </div>
      </div>
    </div>

    <div class="quick-grid">
      <section class="panel">
        <div class="label">Your vehicle</div>
        <div class="vehicle">
          <div>
            <h2>{vehicle_year} Kia {vehicle_model}</h2>
            <p class="meta">{customer_first_name} · {city}, FL · Score {lead_score}/100</p>
          </div>
          <span class="tag">{vehicle_tag}</span>
        </div>
      </section>

      <section class="panel">
        <div class="label">Next step</div>
        <p class="trust">Call Ivan or book a quick appointment to review your options. No pressure—we'll walk through everything and make sure the timing and numbers work for you.</p>
        <div class="rep">
          <div class="avatar">IS</div>
          <div><b>Ivan Silva</b><span>Sales · Phil Smith Kia · <a class="phone" href="tel:19548600537">(954) 860-0537</a></span></div>
        </div>
      </section>
    </div>

    <p class="footer">All figures are estimates from AutoAlert data and are not an offer. Actual values depend on vehicle condition, mileage, options, payoff, and market demand. This page was generated to explore your options with Ivan.</p>
  </section>
</main>

<div class="sticky" aria-label="Quick actions">
  <div class="sticky-inner">
    <a class="btn primary" href="tel:19548600537">Talk to Ivan</a>
    <a class="btn secondary phone" href="tel:19548600537">Call</a>
  </div>
</div>
</body>
</html>
"""

def classify_opportunity(row):
    """Determine the best opportunity type based on CSV data"""
    # Parse values safely
    try:
        current_payment = float(row.get('Pagamento Atual', 0) or 0)
        new_payment = float(row.get('Novo Pagamento', 0) or 0)
        equity = float(row.get('EQUITY', 0) or 0)
        fim_contrato = row.get('Fim Contrato', '')
    except:
        return None, None

    # Lease ending (within 6 months)
    if fim_contrato and '2026-09' in fim_contrato or '2026-10' in fim_contrato or '2026-11' in fim_contrato:
        if new_payment < current_payment:
            return 'LEASE_ENDING', f"Lease ending soon with lower payment option"
        else:
            return 'LEASE_ENDING', f"Lease ending — explore your options"

    # Positive equity
    if equity > 500:
        return 'POSITIVE_EQUITY', f"Your vehicle has {equity}+ in equity"

    # Lower payment
    if current_payment > 0 and new_payment > 0 and new_payment < current_payment:
        savings = current_payment - new_payment
        return 'LOWER_PAYMENT', f"Save ${savings:.0f}/month with an upgrade"

    return 'GENERAL', "Explore your vehicle options"

def generate_page(row, output_dir, customer_id):
    """Generate a single landing page from a CSV row"""
    # Extract data
    nome = row.get('Nome', '').strip()
    primeiro_nome = row.get('Primeiro Nome', '').strip()
    nao_ligar = row.get('Nao Ligar', '').strip().upper()

    # Skip if opted-out
    if nao_ligar == 'SIM':
        print(f"  ⊘ {primeiro_nome} - opted out (Nao Ligar)")
        return None

    try:
        lead_score = int(float(row.get('Score', 0) or 0))
    except:
        lead_score = 75

    carro_atual = row.get('Carro Atual', 'Vehicle').strip()
    parts = carro_atual.split()
    vehicle_year = parts[0] if len(parts) > 0 else '2023'
    vehicle_model = ' '.join(parts[2:]) if len(parts) > 2 else 'Kia'

    city = row.get('Cidade', 'FL').strip()

    try:
        current_payment = float(row.get('Pagamento Atual', 0) or 0)
        new_payment = float(row.get('Novo Pagamento', 0) or 0)
    except:
        current_payment = 0
        new_payment = 0

    # Classify opportunity
    opp_code, opp_label = classify_opportunity(row)
    if not opp_code:
        print(f"  ⊘ {primeiro_nome} - insufficient data")
        return None

    # Generate headline and message
    if opp_code == 'LEASE_ENDING':
        headline = f"{primeiro_nome}, your {vehicle_year} Kia is lease-ending soon—check your upgrade."
        if new_payment < current_payment:
            message = f"Based on AutoAlert data, you may qualify for a new Kia at approximately ${new_payment:.0f}/month, which is about ${current_payment - new_payment:.0f} less than your current ${current_payment:.0f} payment."
            metrics = f'<div class="metric"><span>Current payment</span><b>${current_payment:.0f}/mo</b></div><div class="metric highlight"><span>Estimated new</span><b>${new_payment:.0f}/mo</b></div>'
            vehicle_tag = "Time-sensitive"
        else:
            message = f"Your lease is ending soon. Let's explore your best options—new model, better features, or upgraded features."
            metrics = f'<div class="metric"><span>Current payment</span><b>${current_payment:.0f}/mo</b></div><div class="metric"><span>Lease ends</span><b>Soon</b></div>'
            vehicle_tag = "Lease ending"

    elif opp_code == 'POSITIVE_EQUITY':
        equity = float(row.get('EQUITY', 0) or 0)
        headline = f"{primeiro_nome}, your {vehicle_year} Kia may have ${equity:.0f}+ in equity."
        message = f"You might have an opportunity to trade up, pay down, or access that equity. Let's run a quick appraisal to see what makes sense for you."
        metrics = f'<div class="metric highlight"><span>Estimated equity</span><b>${equity:.0f}</b></div><div class="metric"><span>Lead score</span><b>{lead_score}/100</b></div>'
        vehicle_tag = "Appraisal ready"

    elif opp_code == 'LOWER_PAYMENT':
        savings = current_payment - new_payment
        headline = f"{primeiro_nome}, we found a way to lower your Kia payment by ${savings:.0f}/month."
        message = f"Your {vehicle_year} Kia upgrade option is estimated at ${new_payment:.0f}/month—that's ${savings:.0f} less than your current ${current_payment:.0f}. Let's see if this works for you."
        metrics = f'<div class="metric"><span>Current</span><b>${current_payment:.0f}/mo</b></div><div class="metric highlight"><span>Estimated new</span><b>${new_payment:.0f}/mo</b></div>'
        vehicle_tag = "Payment opportunity"

    else:
        headline = f"{primeiro_nome}, explore your {vehicle_year} Kia options."
        message = "Let's see what we can do for you. Book a quick appointment with Ivan to review your best options."
        metrics = f'<div class="metric"><span>Lead score</span><b>{lead_score}/100</b></div><div class="metric"><span>Status</span><b>Ready</b></div>'
        vehicle_tag = "Review options"

    # Create filename (safe URL)
    filename = f"{primeiro_nome.lower()}-{customer_id}.html".replace(' ', '-')
    filepath = os.path.join(output_dir, filename)

    # Generate HTML
    html = HTML_TEMPLATE.format(
        customer_first_name=primeiro_nome,
        vehicle_year=vehicle_year,
        vehicle_model=vehicle_model,
        opportunity_label=opp_label,
        headline=headline,
        message=message,
        metrics_html=metrics,
        customer_name=nome,
        city=city,
        lead_score=lead_score,
        vehicle_tag=vehicle_tag
    )

    # Write file
    with open(filepath, 'w') as f:
        f.write(html)

    # Also create SMS summary
    sms_file = filepath.replace('.html', '-SMS.txt')
    sms_content = f"""{primeiro_nome} - {opp_code}
URL: askivan.co/{filename}
Payment: ${current_payment:.0f} → ${new_payment:.0f}
Score: {lead_score}/100
Nao Ligar: {nao_ligar or 'NO'}
Generated: {datetime.now().isoformat()}
"""
    with open(sms_file, 'w') as f:
        f.write(sms_content)

    print(f"  ✓ {primeiro_nome} ({opp_code}) → {filename}")
    return {
        'html_file': filepath,
        'customer_name': primeiro_nome,
        'opportunity_code': opp_code,
        'url': f"askivan.co/{filename}",
        'sms_file': sms_file
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate personalized Ivan landing pages from CSV')
    parser.add_argument('--csv', required=True, help='Path to AUTOALERT CSV file')
    parser.add_argument('--limit', type=int, default=5, help='Max pages to generate')
    parser.add_argument('--output', default='./', help='Output directory')

    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"❌ CSV not found: {args.csv}")
        sys.exit(1)

    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n📄 Generating up to {args.limit} personalized landing pages...\n")

    generated = []
    skipped = 0

    with open(args.csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= args.limit:
                break

            customer_id = row.get('Customer ID', str(i))
            result = generate_page(row, output_dir, customer_id)
            if result:
                generated.append(result)
            else:
                skipped += 1

    print(f"\n✅ Generated: {len(generated)}")
    print(f"⊘ Skipped: {skipped}\n")

    if generated:
        print("📋 Manifest:\n")
        manifest = {
            'generated_at': datetime.now().isoformat(),
            'total_pages': len(generated),
            'pages': generated
        }

        manifest_file = os.path.join(output_dir, 'manifest.json')
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)

        for item in generated:
            print(f"  {item['customer_name']:20} {item['opportunity_code']:15} {item['url']}")

        print(f"\nManifest saved: {manifest_file}")

    print()

if __name__ == '__main__':
    main()
