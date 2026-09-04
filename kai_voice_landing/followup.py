"""
kai_voice_landing / followup.py
Automated follow-up cadence engine for Kai AI BDC.

2026 Automotive BDC Cadence:
- Day 0: Intro personalized landing + audio preview (SMS + Email)
- Day 2: Soft touch if unread / no booking ("Did you get a chance to see your Sportage numbers?")
- Day 5: Trade breakdown + 3 equivalent new models comparison
- Day 10: Final courtesy check-in before nurture archive

Automatic cancellation when:
- Lead books appraisal
- Lead replies STOP / opt-out
"""
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from .tracking import get_db, log_event, now_iso, DB_PATH

CADENCE_SCHEDULE = [
    {"step": "DAY_0", "delay_days": 0, "channel": "SMS", "title": "Initial personalized outreach"},
    {"step": "DAY_2", "delay_days": 2, "channel": "SMS", "title": "Soft touch reminder"},
    {"step": "DAY_5", "delay_days": 5, "channel": "EMAIL", "title": "Inventory & equity breakdown"},
    {"step": "DAY_10", "delay_days": 10, "channel": "SMS", "title": "Final courtesy check"},
]

def plan_cadence(contact_id: str, start_time: Optional[datetime] = None, db_path=DB_PATH) -> List[Dict[str, Any]]:
    """Generate and store the follow-up cadence plan for a lead."""
    base = start_time or datetime.now(timezone.utc)
    scheduled = []

    with get_db(db_path) as conn:
        for item in CADENCE_SCHEDULE:
            run_date = (base + timedelta(days=item["delay_days"])).isoformat()
            cur = conn.execute("""
            INSERT INTO bdc_followups (contact_id, step, channel, scheduled_date, status, created_at)
            VALUES (?, ?, ?, ?, 'PENDING', ?)
            """, (contact_id, item["step"], item["channel"], run_date, now_iso()))
            scheduled.append({
                "id": cur.lastrowid,
                "step": item["step"],
                "channel": item["channel"],
                "scheduled_date": run_date,
                "title": item["title"],
                "status": "PENDING"
            })

    log_event(contact_id, "CADENCE_PLANNED", {"steps_count": len(scheduled)}, db_path)
    return scheduled

def cancel_pending_followups(contact_id: str, reason: str, db_path=DB_PATH) -> int:
    """Cancel all pending followups (e.g. appointment booked or opt-out)."""
    with get_db(db_path) as conn:
        cur = conn.execute("""
        UPDATE bdc_followups SET status = 'CANCELLED'
        WHERE contact_id = ? AND status = 'PENDING'
        """, (contact_id,))
        count = cur.rowcount

    log_event(contact_id, "CADENCE_CANCELLED", {"reason": reason, "cancelled_count": count}, db_path)
    return count

def get_followup_message_text(step: str, lead_name: str, vehicle: str, landing_url: str) -> str:
    """Get the text copy for each cadence step."""
    first = (lead_name or "there").split()[0]
    if step == "DAY_2":
        return (
            f"Hi {first}, Ivan here from Phil Smith Kia. Did you get a chance to see "
            f"the trade estimate on your {vehicle}? Link: {landing_url} - Reply STOP to end."
        )
    elif step == "DAY_5":
        return (
            f"Hi {first}, we have 3 new 2026 models matching your current {vehicle} payment range. "
            f"Check your full preview here: {landing_url} - Reply STOP to end."
        )
    elif step == "DAY_10":
        return (
            f"Hi {first}, checking in one last time before archiving your file. "
            f"If you'd still like the free 20-min appraisal on the {vehicle}, let me know: "
            f"{landing_url} - Reply STOP to end."
        )
    return f"Hi {first}, review your {vehicle} preview: {landing_url}"
