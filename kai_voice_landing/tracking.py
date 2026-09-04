"""
kai_voice_landing / tracking.py
State tracking & observability engine for Kai AI BDC.

Maintains SQLite persistence for lead lifecycle, messaging audit logs,
event streams, and scheduled follow-up cadences.
"""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

DB_PATH = Path("/Users/clawbotlocal/autoalert-pages/kai_bdc.db")

def get_db(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Path = DB_PATH) -> None:
    """Initialize the BDC tracking schema."""
    with get_db(db_path) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS bdc_leads (
            contact_id TEXT PRIMARY KEY,
            slug TEXT UNIQUE,
            name TEXT NOT NULL,
            gender TEXT DEFAULT 'unknown',
            phone TEXT,
            email TEXT,
            current_vehicle TEXT,
            replacement_vehicle TEXT,
            equity REAL DEFAULT 0.0,
            equity_str TEXT,
            score INTEGER DEFAULT 0,
            tier TEXT DEFAULT 'COLD',
            current_state TEXT DEFAULT 'NEW',
            landing_path TEXT,
            audio_path TEXT,
            video_path TEXT,
            qa_verdict TEXT DEFAULT 'PENDING',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS bdc_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload_json TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (contact_id) REFERENCES bdc_leads (contact_id)
        );

        CREATE TABLE IF NOT EXISTS bdc_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id TEXT NOT NULL,
            channel TEXT NOT NULL,          -- 'SMS' | 'EMAIL'
            recipient TEXT NOT NULL,
            subject TEXT,
            body TEXT NOT NULL,
            status TEXT DEFAULT 'DRAFT',    -- 'DRAFT' | 'BLOCKED' | 'APPROVED' | 'SENT'
            block_reason TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (contact_id) REFERENCES bdc_leads (contact_id)
        );

        CREATE TABLE IF NOT EXISTS bdc_followups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id TEXT NOT NULL,
            step TEXT NOT NULL,             -- 'DAY_0' | 'DAY_2' | 'DAY_5' | 'DAY_10'
            channel TEXT NOT NULL,          -- 'SMS' | 'EMAIL'
            scheduled_date TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',  -- 'PENDING' | 'DISPATCHED' | 'CANCELLED'
            created_at TEXT NOT NULL,
            FOREIGN KEY (contact_id) REFERENCES bdc_leads (contact_id)
        );

        CREATE INDEX IF NOT EXISTS idx_leads_tier ON bdc_leads (tier);
        CREATE INDEX IF NOT EXISTS idx_leads_state ON bdc_leads (current_state);
        CREATE INDEX IF NOT EXISTS idx_events_cid ON bdc_events (contact_id);
        CREATE INDEX IF NOT EXISTS idx_msgs_cid ON bdc_messages (contact_id);
        """)

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def upsert_lead(data: Dict[str, Any], db_path: Path = DB_PATH) -> None:
    init_db(db_path)
    now = now_iso()
    with get_db(db_path) as conn:
        conn.execute("""
        INSERT INTO bdc_leads (
            contact_id, slug, name, gender, phone, email,
            current_vehicle, replacement_vehicle, equity, equity_str,
            score, tier, current_state, landing_path, audio_path, video_path,
            qa_verdict, created_at, updated_at
        ) VALUES (
            :contact_id, :slug, :name, :gender, :phone, :email,
            :current_vehicle, :replacement_vehicle, :equity, :equity_str,
            :score, :tier, :current_state, :landing_path, :audio_path, :video_path,
            :qa_verdict, :created_at, :updated_at
        )
        ON CONFLICT(contact_id) DO UPDATE SET
            slug=excluded.slug,
            name=excluded.name,
            gender=excluded.gender,
            phone=excluded.phone,
            email=excluded.email,
            current_vehicle=excluded.current_vehicle,
            replacement_vehicle=excluded.replacement_vehicle,
            equity=excluded.equity,
            equity_str=excluded.equity_str,
            score=excluded.score,
            tier=excluded.tier,
            current_state=excluded.current_state,
            landing_path=coalesce(excluded.landing_path, bdc_leads.landing_path),
            audio_path=coalesce(excluded.audio_path, bdc_leads.audio_path),
            video_path=coalesce(excluded.video_path, bdc_leads.video_path),
            qa_verdict=coalesce(excluded.qa_verdict, bdc_leads.qa_verdict),
            updated_at=:updated_at
        """, {
            "contact_id": str(data["contact_id"]),
            "slug": data.get("slug", ""),
            "name": data.get("name", ""),
            "gender": data.get("gender", "unknown"),
            "phone": data.get("phone", ""),
            "email": data.get("email", ""),
            "current_vehicle": data.get("current_vehicle", ""),
            "replacement_vehicle": data.get("replacement_vehicle", ""),
            "equity": float(data.get("equity", 0.0)),
            "equity_str": data.get("equity_str", "$0"),
            "score": int(data.get("score", 0)),
            "tier": data.get("tier", "COLD"),
            "current_state": data.get("current_state", "NEW"),
            "landing_path": data.get("landing_path"),
            "audio_path": data.get("audio_path"),
            "video_path": data.get("video_path"),
            "qa_verdict": data.get("qa_verdict", "PENDING"),
            "created_at": now,
            "updated_at": now,
        })

def log_event(contact_id: str, event_type: str, payload: Optional[Dict[str, Any]] = None, db_path: Path = DB_PATH) -> None:
    init_db(db_path)
    with get_db(db_path) as conn:
        conn.execute("""
        INSERT INTO bdc_events (contact_id, event_type, payload_json, timestamp)
        VALUES (?, ?, ?, ?)
        """, (contact_id, event_type, json.dumps(payload or {}, ensure_ascii=False), now_iso()))

def transition_state(contact_id: str, new_state: str, details: Optional[Dict[str, Any]] = None, db_path: Path = DB_PATH) -> None:
    init_db(db_path)
    now = now_iso()
    with get_db(db_path) as conn:
        conn.execute("""
        UPDATE bdc_leads SET current_state = ?, updated_at = ? WHERE contact_id = ?
        """, (new_state, now, contact_id))
    log_event(contact_id, f"STATE_TRANSITION_{new_state}", details, db_path)

def record_message(contact_id: str, channel: str, recipient: str, subject: Optional[str], body: str, status: str = "DRAFT", block_reason: Optional[str] = None, db_path: Path = DB_PATH) -> int:
    init_db(db_path)
    with get_db(db_path) as conn:
        cur = conn.execute("""
        INSERT INTO bdc_messages (contact_id, channel, recipient, subject, body, status, block_reason, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (contact_id, channel.upper(), recipient, subject, body, status, block_reason, now_iso()))
        return cur.lastrowid

def get_lead_history(contact_id: str, db_path: Path = DB_PATH) -> Dict[str, Any]:
    init_db(db_path)
    with get_db(db_path) as conn:
        lead = conn.execute("SELECT * FROM bdc_leads WHERE contact_id = ?", (contact_id,)).fetchone()
        events = conn.execute("SELECT * FROM bdc_events WHERE contact_id = ? ORDER BY id ASC", (contact_id,)).fetchall()
        msgs = conn.execute("SELECT * FROM bdc_messages WHERE contact_id = ? ORDER BY id ASC", (contact_id,)).fetchall()
        followups = conn.execute("SELECT * FROM bdc_followups WHERE contact_id = ? ORDER BY id ASC", (contact_id,)).fetchall()

        return {
            "lead": dict(lead) if lead else None,
            "events": [dict(e) for e in events],
            "messages": [dict(m) for m in msgs],
            "followups": [dict(f) for f in followups],
        }
