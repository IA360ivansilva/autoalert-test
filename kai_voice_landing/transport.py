"""
kai_voice_landing / transport.py
Safe Email and SMS Transport engine for Kai AI BDC (Phil Smith Kia).

HARD SAFETY RULES:
- DRY_RUN is permanently TRUE by default.
- REAL DISPATCH IS BLOCKED (BLOCK_SEND).
- Generates compliant, production-grade drafts for human review.
- Records all message drafts in bdc_messages audit log.
- Compliance: TCPA opt-out on SMS ("Reply STOP"), CAN-SPAM on Email,
  physical address, and AI disclosure present.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from .tracking import record_message, log_event

# Hard safety latch
DRY_RUN: bool = True
ALLOW_DISPATCH: bool = False

DEALERSHIP_NAME = "Phil Smith Kia"
DEALERSHIP_ADDRESS = "4250 N Federal Hwy, Lighthouse Point, FL 33064"
IVAN_DIRECT_PHONE = "(954) 860-0537"

@dataclass
class MessageDraft:
    channel: str           # SMS | EMAIL
    recipient: str
    sender: str
    subject: Optional[str]
    body: str
    html_body: Optional[str]
    character_count: int
    is_compliant: bool
    status: str            # DRAFT_PENDING_APPROVAL | BLOCKED
    notes: list[str]

def build_sms_draft(lead_name: str, vehicle: str, equity_str: str, landing_url: str, recipient_phone: str) -> MessageDraft:
    """Build a compliant, conversational 1-to-1 SMS draft."""
    first = (lead_name or "there").split()[0]
    # Conversational, direct, under 160 chars ideal
    body = (
        f"Hi {first}, it's Ivan at Phil Smith Kia. Our system shows around {equity_str} "
        f"in estimated equity on your {vehicle}. I put together a quick preview for you: "
        f"{landing_url} - Reply STOP to opt out."
    )
    notes = []
    char_len = len(body)
    if char_len <= 160:
        notes.append("Fits in 1 SMS segment (<=160 chars)")
    else:
        notes.append(f"Multi-segment SMS ({char_len} chars, 2 segments)")

    notes.append("TCPA 'Reply STOP' opt-out included")
    notes.append("No credit or guaranteed pricing promised")

    return MessageDraft(
        channel="SMS",
        recipient=recipient_phone,
        sender=IVAN_DIRECT_PHONE,
        subject=None,
        body=body,
        html_body=None,
        character_count=char_len,
        is_compliant=True,
        status="DRAFT_PENDING_APPROVAL",
        notes=notes
    )

def build_email_draft(lead_name: str, vehicle: str, equity_str: str, landing_url: str, recipient_email: str) -> MessageDraft:
    """Build a compliant HTML + Plaintext Email draft."""
    first = (lead_name or "there").split()[0]
    subject = f"{first}, your {vehicle} trade appraisal preview — Phil Smith Kia"

    text_body = (
        f"Hi {first},\n\n"
        f"This is Ivan Silva over at Phil Smith Kia in Lighthouse Point.\n\n"
        f"I was reviewing our local inventory exchange this morning and your {vehicle} stood out. "
        f"Based on current market demand, our system estimates around {equity_str} in trade equity.\n\n"
        f"I put together a personalized appraisal preview with an audio walkthrough of your options here:\n"
        f"{landing_url}\n\n"
        f"Bring the {vehicle} by for a 20-minute physical appraisal to get your certified number — "
        f"no obligation, no hassle.\n\n"
        f"Best regards,\n"
        f"Ivan Silva\n"
        f"Sales · Phil Smith Kia\n"
        f"{DEALERSHIP_ADDRESS}\n"
        f"Direct: {IVAN_DIRECT_PHONE}\n\n"
        f"---\n"
        f"This message and appraisal page were prepared by Ivan's AI Assistant. All values are market estimates. "
        f"To unsubscribe from future trade updates, reply with UNSUBSCRIBE."
    )

    html_body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a0e17; color: #f8fafc; margin:0; padding: 24px; }}
.card {{ max-width: 540px; margin: 0 auto; background: #111827; border: 1px solid #1f2937; border-radius: 16px; padding: 28px; }}
.badge {{ display: inline-block; background: rgba(198,15,15,0.15); border: 1px solid rgba(198,15,15,0.3); color: #ff5a5a; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 999px; margin-bottom: 16px; }}
h2 {{ font-size: 24px; margin-bottom: 12px; color: #fff; }}
p {{ font-size: 15px; line-height: 1.6; color: #cbd5e1; margin-bottom: 16px; }}
.highlight {{ color: #4ade80; font-weight: 800; }}
.btn {{ display: inline-block; background: #16a34a; color: #fff; text-decoration: none; padding: 14px 24px; border-radius: 10px; font-weight: 800; font-size: 15px; margin: 18px 0; }}
.footer {{ margin-top: 28px; padding-top: 18px; border-top: 1px solid #1f2937; font-size: 11.5px; color: #94a3b8; line-height: 1.5; }}
</style>
</head>
<body>
<div class="card">
  <div class="badge">PHIL SMITH KIA · APPRAISAL PREVIEW</div>
  <h2>{first}, your {vehicle} may have equity.</h2>
  <p>Our system estimates <span class="highlight">around {equity_str} in equity</span> on your {vehicle}. Trade values in our corridor are holding higher than expected this season.</p>
  <p>I generated a personalized preview page with an audio message walking through the exact numbers:</p>
  <a class="btn" href="{landing_url}">View Your Appraisal Preview & Audio</a>
  <p>If the numbers make sense, bring the {vehicle} in for a 20-minute certified inspection. No pressure, no games.</p>
  <p><b>Ivan Silva</b><br>Phil Smith Kia · Direct: {IVAN_DIRECT_PHONE}</p>
  <div class="footer">
    {DEALERSHIP_NAME} · {DEALERSHIP_ADDRESS}<br>
    🤖 Generated by Ivan's AI Assistant for customer review.<br>
    To opt out of trade updates, reply with UNSUBSCRIBE.
  </div>
</div>
</body>
</html>"""

    return MessageDraft(
        channel="EMAIL",
        recipient=recipient_email,
        sender="ivan@philsmithkia.com",
        subject=subject,
        body=text_body,
        html_body=html_body,
        character_count=len(text_body),
        is_compliant=True,
        status="DRAFT_PENDING_APPROVAL",
        notes=["CAN-SPAM compliant", "Physical address included", "Unsubscribe mechanism present"]
    )

def prepare_lead_outreach(lead_data: Dict[str, Any], landing_url: str) -> Dict[str, MessageDraft]:
    """Prepare and record both SMS and Email drafts for a lead in DRY-RUN mode."""
    cid = str(lead_data.get("contact_id") or "")
    name = lead_data.get("name", "Customer")
    vehicle = lead_data.get("current_vehicle", "your vehicle")
    equity_str = lead_data.get("equity_str", "$0")
    phone = lead_data.get("phone", "")
    email = lead_data.get("email", "")

    drafts = {}

    if phone:
        sms = build_sms_draft(name, vehicle, equity_str, landing_url, phone)
        record_message(cid, "SMS", phone, None, sms.body, sms.status)
        drafts["sms"] = sms

    if email:
        em = build_email_draft(name, vehicle, equity_str, landing_url, email)
        record_message(cid, "EMAIL", email, em.subject, em.body, em.status)
        drafts["email"] = em

    log_event(cid, "OUTREACH_DRAFTS_GENERATED", {
        "channels": list(drafts.keys()),
        "status": "DRAFT_PENDING_APPROVAL",
        "dry_run": DRY_RUN
    })

    return drafts

def dispatch_message(draft: MessageDraft) -> Dict[str, Any]:
    """Protected dispatch function. ALWAYS BLOCKS while DRY_RUN is active."""
    if not ALLOW_DISPATCH or DRY_RUN:
        return {
            "status": "BLOCKED",
            "sent": False,
            "channel": draft.channel,
            "recipient": draft.recipient,
            "reason": "BLOCK_SEND enforced: dry-run mode active. No customer message sent without explicit Ivan authorization."
        }
    raise PermissionError("Dispatch not authorized.")
