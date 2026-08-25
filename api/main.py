from __future__ import annotations
import json, os, re, uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from data.case_schema import load_cases
from checker.rule_checker import run_all_checks
from runner.run_diagnosis import _call_anthropic, _load_prompts, _parse_ai_json, _validate_ai_diagnosis

ROOT = Path(__file__).resolve().parent.parent
STORE = ROOT / "sessions" / "live_sessions.json"
PROMPT = ROOT / "prompts" / "diagnose_prompt_v2.md"
app = FastAPI(title="NetSage Live API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])

class SessionInput(BaseModel):
    case_id: str; symptom: str = ""; topology_note: str = ""; show_output: str = ""
class ReviewInput(BaseModel):
    decision: Literal["ACCEPTED", "EDITED", "REJECTED"]; reviewer: str = Field(min_length=1); corrected_diagnosis: dict[str, Any] | None = None; reason: str = ""
class VerificationInput(BaseModel):
    verification_output: str; verified_by: str = Field(min_length=1); explicit_human_confirmation: bool = False

def now() -> str: return datetime.now(timezone.utc).isoformat()
def read_store() -> list[dict]:
    if not STORE.exists(): return []
    try: return json.loads(STORE.read_text(encoding="utf-8"))
    except json.JSONDecodeError: return []
def write_store(rows: list[dict]) -> None:
    STORE.parent.mkdir(exist_ok=True); STORE.write_text(json.dumps(rows, indent=2), encoding="utf-8")
def get_session(session_id: str) -> dict:
    for row in read_store():
        if row["session_id"] == session_id: return row
    raise HTTPException(404, "Live session not found")
def save(session: dict) -> dict:
    rows = [r for r in read_store() if r["session_id"] != session["session_id"]]; rows.append(session); write_store(rows); return session
def public(session: dict) -> dict: return session

@app.get("/api/health")
def health(): return {"status":"ok", "ai_configured": bool(os.getenv("ANTHROPIC_API_KEY")), "rule_checker":"ready"}
@app.get("/api/cases")
def cases(): return [{k:v for k,v in c.items() if k != "show_output"} for c in load_cases(ROOT / "data" / "cases.csv")]
@app.get("/api/cases/{case_id}")
def case(case_id: str):
    for c in load_cases(ROOT / "data" / "cases.csv"):
        if c["case_id"] == case_id: return c
    raise HTTPException(404, "Case not found")
@app.get("/api/history")
def history():
    path=ROOT/"dashboard"/"src"/"data.json"
    return {"mode":"HISTORICAL_RESULTS", "message":"No live AI call was made.", "results":json.loads(path.read_text(encoding="utf-8"))}
@app.get("/api/sessions")
def sessions(): return read_store()
@app.post("/api/sessions")
def create_session(payload: SessionInput):
    base = next((c for c in load_cases(ROOT/"data"/"cases.csv") if c["case_id"] == payload.case_id), None)
    if not base: raise HTTPException(404,"Case not found")
    session={"session_id":str(uuid.uuid4()),"mode":"LIVE_SESSION","created_at":now(),"updated_at":now(),"final_status":"OPEN","case":{**base,**payload.model_dump(exclude_none=True)},"ai_status":"NOT_RUN","rule_findings":[],"review":None,"verification":None}
    return save(session)
@app.post("/api/sessions/{session_id}/rule-check")
def rule_check(session_id: str):
    s=get_session(session_id); s["rule_findings"]=[f._asdict() for f in run_all_checks(s["case"])]; s["updated_at"]=now(); return save(s)
@app.post("/api/sessions/{session_id}/diagnose")
def diagnose(session_id: str):
    s=get_session(session_id); key=os.getenv("ANTHROPIC_API_KEY")
    if not key:
        s["ai_status"]="API_ERROR"; s["api_error_category"]="Missing API key"; save(s); raise HTTPException(503, detail="Missing API key")
    try:
        from anthropic import Anthropic
        system, template=_load_prompts(PROMPT); raw=_call_anthropic(Anthropic(api_key=key), system, template.format(**s["case"]))
        diagnosis, status=_validate_ai_diagnosis(_parse_ai_json(raw or ""))
        if not diagnosis: raise ValueError("Malformed response")
        s.update({"ai_status":"COMPLETED","diagnosis":diagnosis,"api_error_category":"","final_status":"AWAITING REVIEW"})
    except Exception as exc:
        text=str(exc).lower(); category="Rate limited" if "rate" in text else "Timeout" if "timeout" in text else "Network error"
        if "malformed" in text: category="Malformed response"
        s.update({"ai_status":"API_ERROR","api_error_category":category})
    s["updated_at"]=now(); return save(s)
@app.post("/api/sessions/{session_id}/review")
def review(session_id: str, payload: ReviewInput):
    s=get_session(session_id)
    if not s.get("diagnosis"): raise HTTPException(409,"A completed live AI diagnosis is required")
    if payload.decision == "REJECTED" and not payload.reason.strip(): raise HTTPException(422,"A rejection reason is required")
    if payload.decision == "EDITED" and not payload.corrected_diagnosis: raise HTTPException(422,"Edited diagnosis is required")
    s["review"]={**payload.model_dump(),"timestamp":now(),"original_ai_diagnosis":s["diagnosis"]}; s["final_status"]="REJECTED" if payload.decision=="REJECTED" else "APPROVED"; return save(s)
@app.post("/api/sessions/{session_id}/verification")
def verification(session_id: str, payload: VerificationInput):
    s=get_session(session_id)
    if not s.get("review") or s["review"]["decision"]=="REJECTED": raise HTTPException(409,"Approved human review required")
    # Honest policy: only explicit human confirmation plus non-empty evidence resolves a session.
    status="RESOLVED" if payload.explicit_human_confirmation and payload.verification_output.strip() else "INSUFFICIENT_EVIDENCE"
    s["verification"]={**payload.model_dump(),"verification_status":status,"timestamp":now()}; s["final_status"]=status; return save(s)
