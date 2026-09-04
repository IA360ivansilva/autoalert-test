"""
kai_voice_landing / scoring.py
Lead qualification & scoring engine for Kai AI BDC (Phil Smith Kia).

Evaluates CRM customer and vehicle data:
- Hard DNC suppression (Stephen Pastore / Rockie Dobson - never contact).
- Equity calculation (Trade value - payoff).
- Payment parity (replacement payment <= current payment).
- Vehicle age & equity scoring (0 - 100 points).
- Tier assignment: HOT (>=70), WARM (>=45), COLD (<45).
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

BLOCKED_SALESPEOPLE = {"STEPHEN PASTORE", "ROCKIE DOBSON"}

@dataclass
class QualificationResult:
    contact_id: str
    name: str
    tier: str              # HOT | WARM | COLD | DNC_BLOCKED
    score: int             # 0 - 100
    is_qualified: bool
    est_equity: float
    current_vehicle: str
    replacement_vehicle: str
    current_payment: float
    new_payment: float
    equity_str: str
    reasons: list[str]
    dnc_blocked: bool
    recommended_action: str

def parse_num(v: Any) -> float:
    if v is None:
        return 0.0
    s = str(v).replace("$", "").replace(",", "").strip()
    try:
        return float(s)
    except Exception:
        return 0.0

def qualify_lead(customer_data: Dict[str, Any], vehicle_data: Optional[Dict[str, Any]] = None) -> QualificationResult:
    """Qualify and score a lead from CRM data."""
    cid = str(customer_data.get("contact_id") or customer_data.get("id") or "")
    first_name = customer_data.get("first_name") or (customer_data.get("full_name", "").split()[0] if customer_data.get("full_name") else "Customer")
    salesperson = str(customer_data.get("salesperson") or customer_data.get("rep") or "").upper().strip()

    reasons = []

    # 1. Hard DNC check
    for blocked in BLOCKED_SALESPEOPLE:
        if blocked in salesperson:
            return QualificationResult(
                contact_id=cid,
                name=first_name,
                tier="DNC_BLOCKED",
                score=0,
                is_qualified=False,
                est_equity=0.0,
                current_vehicle="",
                replacement_vehicle="",
                current_payment=0.0,
                new_payment=0.0,
                equity_str="$0",
                reasons=[f"DNC: Assigned to restricted salesperson {salesperson}"],
                dnc_blocked=True,
                recommended_action="DO_NOT_CONTACT"
            )

    v = vehicle_data or {}
    trade_val = parse_num(v.get("trade_value"))
    payoff = parse_num(v.get("payoff"))
    equity = max(0.0, trade_val - payoff)

    cur_pay = parse_num(v.get("payment")) or parse_num(customer_data.get("current_payment"))
    new_pay = parse_num(v.get("repl_payment")) or parse_num(v.get("new_payment"))

    year = v.get("year", "")
    make = v.get("make", "")
    model = v.get("model", "")
    cur_veh = f"{year} {make} {model}".strip() or customer_data.get("current_vehicle") or "your vehicle"

    repl_year = v.get("repl_year", "2026")
    repl_make = v.get("repl_make", "Kia")
    repl_model = v.get("repl_model", "Sportage")
    repl_veh = f"{repl_year} {repl_make} {repl_model}".strip()

    # 2. Score calculation (0 - 100)
    score = 0

    # Equity scoring (up to 40 pts)
    if equity >= 5000:
        score += 40
        reasons.append(f"High equity (+${equity:,.0f})")
    elif equity >= 2000:
        score += 30
        reasons.append(f"Strong equity (+${equity:,.0f})")
    elif equity >= 900:
        score += 20
        reasons.append(f"Positive equity (+${equity:,.0f})")
    elif equity > 0:
        score += 10
        reasons.append(f"Marginal equity (+${equity:,.0f})")
    else:
        reasons.append("Zero or negative equity")

    # Payment parity scoring (up to 25 pts)
    if new_pay > 0 and cur_pay > 0:
        if new_pay <= cur_pay:
            score += 25
            reasons.append("Payment lower or equal to current")
        elif (new_pay - cur_pay) <= 35:
            score += 18
            reasons.append("Payment within $35/mo parity window")
        elif (new_pay - cur_pay) <= 75:
            score += 10
            reasons.append("Payment within $75/mo upgrade window")
    elif cur_pay > 0:
        score += 15
        reasons.append("Active monthly payment on file")

    # Vehicle age / trade readiness (up to 20 pts)
    try:
        y_int = int(year)
        if y_int <= 2022:
            score += 20
            reasons.append("Vehicle >= 4 years old (prime upgrade cycle)")
        elif y_int <= 2024:
            score += 10
            reasons.append("Vehicle 2-3 years old (mid-lease or equity sweet spot)")
    except Exception:
        score += 10

    # Contactability scoring (up to 15 pts)
    has_phone = bool(customer_data.get("best_phone") or customer_data.get("phone"))
    has_email = bool(customer_data.get("email"))
    if has_phone:
        score += 10
        reasons.append("Direct phone available for SMS")
    if has_email:
        score += 5
        reasons.append("Email available")

    # 3. Tier assignment
    if score >= 70:
        tier = "HOT"
        action = "GENERATE_PAGE_AND_AUDIO_IMMEDIATE"
    elif score >= 45:
        tier = "WARM"
        action = "GENERATE_PAGE_AND_AUDIO"
    else:
        tier = "COLD"
        action = "MONITOR_OR_NURTURE"

    return QualificationResult(
        contact_id=cid,
        name=first_name,
        tier=tier,
        score=score,
        is_qualified=score >= 45,
        est_equity=equity,
        current_vehicle=cur_veh,
        replacement_vehicle=repl_veh,
        current_payment=cur_pay,
        new_payment=new_pay,
        equity_str=f"${equity:,.0f}",
        reasons=reasons,
        dnc_blocked=False,
        recommended_action=action
    )
