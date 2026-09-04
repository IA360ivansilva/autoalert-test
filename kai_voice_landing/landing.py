"""
kai_voice_landing / landing.py
Build a premium mobile-first personalized automotive landing page for a Lead.
Mirrors the approved autoalert-test structure (dark theme, phone #E5E7EB all
states, green #16a34a CTA, avatar 'IS', equivalent models, AI disclosure).
"""
from .registry import (
    PHONE_COLOR, CTA_GREEN, FORBIDDEN_PHONE_BLUES, AVATAR_INITIALS,
    IVAN_PHONE_DISPLAY, IVAN_PHONE_TEL, AI_DISCLOSURE, AI_DISCLOSURE_PT,
)

TPL = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} - Phil Smith Kia Appraisal Preview</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#080b10;--panel:#111722;--panel2:#151d2b;--line:#253044;
  --text:#f8fafc;--soft:#b8c2d2;--muted:#7d889b;
  --green:{cta_green};--phone:{phone_color};--gold:#d6b25e;
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
.hero-content{{position:relative;z-index:1}}
.eyebrow{{display:inline-flex;align-items:center;gap:8px;margin-bottom:14px;color:#ffd9d9;font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase}}
.dot{{width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 0 5px rgba(22,163,74,.15)}}
h1{{font-size:34px;line-height:1.05;font-weight:900;max-width:760px}}
.highlight{{color:#ff6262}}
.sub{{margin-top:13px;color:var(--soft);font-size:16px;line-height:1.5;max-width:680px}}
.numbers{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:18px}}
.metric{{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.11);border-radius:14px;padding:13px}}
.metric span{{display:block;color:var(--muted);font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase}}
.metric b{{display:block;margin-top:3px;font-size:22px;line-height:1.1}}
.metric.equity{{background:rgba(22,163,74,.14);border-color:rgba(74,222,128,.34)}}
.metric.equity b{{color:#4ade80}}
.actions{{display:grid;grid-template-columns:1fr;gap:10px;margin-top:18px}}
.btn{{display:flex;align-items:center;justify-content:center;min-height:52px;border-radius:13px;text-decoration:none;font-size:15px;font-weight:900;text-align:center}}
.btn.primary{{background:var(--green);color:#fff;box-shadow:0 14px 32px rgba(22,163,74,.24)}}
.btn.secondary{{border:1px solid rgba(229,231,235,.22);background:rgba(229,231,235,.08);color:var(--phone)}}
.audio-card{{position:relative;z-index:1;margin-top:16px;border:1px solid rgba(214,178,94,.36);border-radius:18px;background:rgba(8,11,16,.72);padding:15px}}
.audio-head{{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:10px}}
.audio-title{{font-size:14px;font-weight:900}}
.audio-state{{color:var(--gold);font-size:12px;font-weight:800;white-space:nowrap}}
.play-button{{width:100%;min-height:48px;border:0;border-radius:12px;background:#fff;color:#0b111a;font-size:15px;font-weight:900;cursor:pointer;margin-bottom:11px}}
audio{{display:block;width:100%;height:42px}}
.quick-grid{{display:grid;gap:12px}}
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
.avatar{{display:grid;place-items:center;width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,var(--green),#0b5e2a);font-weight:900}}
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
  <section class="hero" aria-label="{name} appraisal preview">
    <div class="hero-card">
      <div class="hero-content">
        <div class="topline">
          <span class="brand">Phil Smith Kia</span>
          <a class="phone phone-pill" href="tel:{phone_tel}">{phone_display}</a>
        </div>
        <div class="eyebrow"><span class="dot"></span>{eyebrow}</div>
        <h1>{h1}</h1>
        <p class="sub">{sub}</p>
        <div class="numbers" aria-label="Vehicle summary">
          <div class="metric equity"><span>{eq_label}</span><b>{equity}</b></div>
          <div class="metric"><span>{pay_label}</span><b>{payment}</b></div>
        </div>
        <div class="actions">
          <a class="btn primary" href="sms:{phone_tel}?&body={sms_body}">{cta}</a>
          <a class="btn secondary phone" href="tel:{phone_tel}">Call Ivan</a>
        </div>
        <div class="audio-card" data-qa="audio-visible">
          <div class="audio-head">
            <div class="audio-title">{audio_title}</div>
            <div id="audioState" class="audio-state">Ready</div>
          </div>
          <button id="playMessage" class="play-button" type="button">{play_label}</button>
          <audio id="personalAudio" controls preload="auto" playsinline>
            <source src="{audio_src}" type="audio/mpeg">
          </audio>
        </div>
      </div>
    </div>
    <div class="quick-grid">
      <section class="panel">
        <div class="label">{cur_label}</div>
        <div class="vehicle">
          <div>
            <h2>{current_vehicle}</h2>
            <p class="meta">{cur_meta}</p>
          </div>
          <span class="tag">Appraisal ready</span>
        </div>
      </section>
      <section class="panel">
        <div class="label">{opt_label}</div>
        <div class="models">
          {models_html}
        </div>
      </section>
      <section class="panel">
        <div class="label">{next_label}</div>
        <p class="trust">{trust}</p>
        <div class="rep">
          <div class="avatar">{avatar}</div>
          <div><b>Ivan Silva</b><span>Sales · Phil Smith Kia · <a class="phone" href="tel:{phone_tel}">{phone_display}</a></span></div>
        </div>
      </section>
    </div>
    <p class="footer">{footer}</p>
  </section>
</main>
<div class="sticky" aria-label="Quick actions">
  <div class="sticky-inner">
    <a class="btn primary" href="sms:{phone_tel}?&body={sms_body}">{cta}</a>
    <a class="btn secondary phone" href="tel:{phone_tel}">Call Ivan</a>
  </div>
</div>
<script>
(function(){{
  var audio=document.getElementById('personalAudio');
  var button=document.getElementById('playMessage');
  var state=document.getElementById('audioState');
  if(!audio||!button||!state)return;
  function setState(t){{state.textContent=t;}}
  function playMessage(){{audio.muted=false;var a=audio.play();if(a&&a.then){{a.then(function(){{setState('Playing');}}).catch(function(){{setState('Tap to play');}});}}}}
  button.addEventListener('click',playMessage);
  audio.addEventListener('play',function(){{setState('Playing');}});
  audio.addEventListener('pause',function(){{if(!audio.ended)setState('Paused');}});
  audio.addEventListener('ended',function(){{setState('Replay');}});
  window.addEventListener('load',function(){{var a=audio.play();if(a&&a.catch){{a.then(function(){{setState('Playing');}}).catch(function(){{setState('Tap to play');}});}});
}})();
</script>
</body>
</html>
"""

# i18n strings (pt / en)
I18N = {
    "pt": {
        "eyebrow": "Pré-visualização pessoal para {name}",
        "h1": "Seu <span class=\"highlight\">{car}</span> pode estar em uma boa posição de troca.",
        "sub": "{name}, fiz esta pré-visualização rápida porque o sistema mostra cerca de <strong>{equity} em equity*</strong>. Uma avaliação de 20 minutos dá o número real.",
        "eq_label": "Equity estimado*",
        "pay_label": "Pagamento atual",
        "cur_label": "Veículo atual",
        "opt_label": "Opções para comparar",
        "next_label": "Próximo passo",
        "audio_title": "Mensagem de áudio pessoal",
        "play_label": "Ouvir mensagem de {name}",
        "trust": "Traga o {car} e inspecionamos estado, opcionais, pneus, histórico e demanda atual do mercado. Sem pressão. Se o número não estiver bom, você fica com o carro.",
        "footer": "Todos os valores são estimativas de dados de mercado e não são oferta nem valor garantido. O valor real de troca é definido apenas após avaliação física e depende de estado, quilometragem, opcionais, histório e demanda. {disclosure}",
    },
    "en": {
        "eyebrow": "Personal preview for {name}",
        "h1": "Your <span class=\"highlight\">{car}</span> may be in a strong trade position.",
        "sub": "{name}, I made this quick preview because the system shows an estimated <strong>{equity} in equity*</strong>. A 20-minute appraisal gives you the real number.",
        "eq_label": "Estimated equity*",
        "pay_label": "Current payment",
        "cur_label": "Current vehicle",
        "opt_label": "Options to compare",
        "next_label": "Next step",
        "audio_title": "Personal audio message",
        "play_label": "Play {name}'s message",
        "trust": "Bring the {car} in and we will inspect condition, options, tires, history and current market demand. No pressure. If the number is not right, you keep your car.",
        "footer": "All figures are estimates from market data and are not an offer or guaranteed value. Actual trade value is determined only after a physical appraisal and depends on vehicle condition, mileage, options, history and current demand. {disclosure}",
    },
}


def build_landing_html(lead, audio_src: str, payment: str = "$XXX/mo", cur_meta: str = "Lighthouse Point, FL") -> str:
    t = I18N.get(lead.lang, I18N["en"])
    models_html = "\n".join(
        f'          <a class="model" href="{m["url"]}" target="_blank" rel="noopener">\n'
        f'            <span><strong>{m["name"]}</strong><span>{m["note"]}</span></span><b>View</b>\n'
        f'          </a>' for m in lead.equivalent_models
    )
    sms_body = lead.sms_body.replace(" ", "%20")
    return TPL.format(
        lang=lead.lang,
        name=lead.name,
        phone_display=lead.phone_display,
        phone_tel=lead.phone_tel,
        cta=lead.cta,
        sms_body=sms_body,
        audio_src=audio_src,
        avatar=AVATAR_INITIALS,
        eyebrow=t["eyebrow"].format(name=lead.name),
        h1=t["h1"].format(car=lead.current_vehicle),
        current_vehicle=lead.current_vehicle,
        sub=t["sub"].format(name=lead.name, equity=lead.equity_estimate),
        equity=lead.equity_estimate,
        payment=payment,
        eq_label=t["eq_label"],
        pay_label=t["pay_label"],
        cur_label=t["cur_label"],
        opt_label=t["opt_label"],
        next_label=t["next_label"],
        audio_title=t["audio_title"],
        play_label=t["play_label"].format(name=lead.name),
        trust=t["trust"].format(car=lead.current_vehicle),
        cur_meta=cur_meta,
        footer=t["footer"].format(disclosure=AI_DISCLOSURE_PT if lead.lang == "pt" else AI_DISCLOSURE),
        models_html=models_html,
        phone_color=PHONE_COLOR,
        cta_green=CTA_GREEN,
    )
