"""kai_voice_landing package init."""
from .registry import Lead, select_voice
from .landing import build_landing_html
from .audio_engine import generate_audio, AudioResult
from .video_engine import generate_video_preview, VideoResult
from .scoring import qualify_lead, QualificationResult
from .tracking import upsert_lead, get_lead_history, transition_state, log_event
from .transport import build_sms_draft, build_email_draft, prepare_lead_outreach, MessageDraft
from .followup import plan_cadence, cancel_pending_followups
from .qa import run_qa, write_qa
from .pipeline import run_bdc_pipeline

__all__ = [
    "Lead", "select_voice", "build_landing_html", "generate_audio",
    "AudioResult", "generate_video_preview", "VideoResult",
    "qualify_lead", "QualificationResult", "upsert_lead", "get_lead_history",
    "transition_state", "log_event", "build_sms_draft", "build_email_draft",
    "prepare_lead_outreach", "MessageDraft", "plan_cadence",
    "cancel_pending_followups", "run_qa", "write_qa", "run_bdc_pipeline"
]
