import asyncio
import json
import uuid
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import PlainTextResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

from app.agents.workflow import blueprint_graph
from app.agents.state import BlueprintState, SECTION_THRESHOLDS
from app.services.llm_provider import llm_provider
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Blueprint"])

# In-memory store for jobs
jobs: Dict[str, Dict[str, Any]] = {}

class GenerateRequest(BaseModel):
    raw_idea: str
    user_constraints: Optional[Dict[str, Any]] = {}
    preferred_provider: Optional[str] = "groq"

class KeysUpdateRequest(BaseModel):
    groq_key: Optional[str] = None
    gemini_key: Optional[str] = None
    mistral_key: Optional[str] = None
    cohere_key: Optional[str] = None

async def run_blueprint_workflow(job_id: str, raw_idea: str, constraints: dict):
    """Background execution of LangGraph blueprint workflow."""
    initial_state: BlueprintState = {
        "job_id": job_id,
        "raw_idea": raw_idea,
        "user_constraints": constraints,
        "logs": [f"Pipeline initialized for job {job_id}"],
        "expansion_attempts": {},
    }

    job_entry = jobs[job_id]
    job_entry["status"] = "processing"
    
    try:
        async for output in blueprint_graph.astream(initial_state):
            for node_name, state_update in output.items():
                job_entry["current_step"] = state_update.get("current_step", f"Completed {node_name}")
                job_entry["active_agent"] = state_update.get("active_agent", node_name)
                
                if "logs" in state_update and state_update["logs"]:
                    job_entry["logs"] = state_update["logs"]
                if "word_counts" in state_update:
                    job_entry["word_counts"] = state_update["word_counts"]
                if "total_words" in state_update:
                    job_entry["total_words"] = state_update["total_words"]
                if "final_blueprint" in state_update:
                    job_entry["final_blueprint"] = state_update["final_blueprint"]
                if "is_complete" in state_update:
                    job_entry["is_complete"] = state_update["is_complete"]

                # Copy completed sections into job state
                for k, v in state_update.items():
                    if k.startswith("section_"):
                        job_entry["sections"][k] = v

        job_entry["status"] = "completed"
        job_entry["is_complete"] = True
    except Exception as e:
        logger.exception(f"Error executing blueprint workflow for job {job_id}: {e}")
        job_entry["status"] = "failed"
        job_entry["error"] = str(e)
        job_entry["logs"].append(f"[Error] Pipeline execution failed: {e}")

@router.post("/blueprint/generate")
async def generate_blueprint(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Trigger the autonomous multi-agent swarm to generate a 15,000+ word Master Blueprint."""
    if not request.raw_idea.strip():
        raise HTTPException(status_code=400, detail="raw_idea cannot be empty.")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "raw_idea": request.raw_idea,
        "current_step": "Queued in swarm engine",
        "active_agent": "Initializing",
        "logs": ["Job queued."],
        "sections": {},
        "word_counts": {},
        "total_words": 0,
        "final_blueprint": "",
        "is_complete": False,
        "error": None
    }

    background_tasks.add_task(run_blueprint_workflow, job_id, request.raw_idea, request.user_constraints)
    return {"job_id": job_id, "status": "queued", "message": "Multi-agent swarm launched successfully."}

@router.get("/blueprint/stream/{job_id}")
async def stream_blueprint(job_id: str):
    """Server-Sent Events (SSE) stream broadcasting live agent progress and logs."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found.")

    async def event_generator():
        last_log_count = 0
        while True:
            job = jobs.get(job_id)
            if not job:
                break

            current_logs = job.get("logs", [])
            new_logs = current_logs[last_log_count:]
            last_log_count = len(current_logs)

            data = {
                "job_id": job_id,
                "status": job.get("status"),
                "current_step": job.get("current_step"),
                "active_agent": job.get("active_agent"),
                "new_logs": new_logs,
                "word_counts": job.get("word_counts", {}),
                "total_words": job.get("total_words", 0),
                "sections_ready": list(job.get("sections", {}).keys()),
                "is_complete": job.get("is_complete", False),
                "error": job.get("error")
            }

            yield {"event": "progress", "data": json.dumps(data)}

            if job.get("status") in ["completed", "failed"]:
                yield {"event": "done", "data": json.dumps({"status": job.get("status"), "final_blueprint": job.get("final_blueprint", "")})}
                break

            await asyncio.sleep(1.0)

    return EventSourceResponse(event_generator())

@router.get("/blueprint/{job_id}")
async def get_blueprint(job_id: str):
    """Fetch complete blueprint details and sections for a specific job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found.")
    return jobs[job_id]

@router.get("/blueprint/{job_id}/export")
async def export_blueprint(job_id: str, format: str = Query("markdown", pattern="^(markdown|cursor|claude|antigravity)$")):
    """Export the Master Blueprint tailored for specific AI IDEs."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found.")
    
    job = jobs[job_id]
    blueprint = job.get("final_blueprint", "")
    if not blueprint:
        raise HTTPException(status_code=400, detail="Blueprint has not completed generation yet.")

    if format == "cursor":
        header = """# CURSOR PROJECT RULES & MASTER ARCHITECT SPECIFICATION
# Place this file in your project root as `.cursorrules` or feed it to Cursor Composer.
# INSTRUCTION FOR CURSOR: Execute the 8-Phase implementation plan sequentially without skipping verifications.
--------------------------------------------------------------------------------
"""
        content = header + blueprint
        return PlainTextResponse(content, media_type="text/markdown", headers={"Content-Disposition": "attachment; filename=CURSOR_MASTER_PROMPT.md"})

    elif format == "claude":
        header = """# CLAUDE CODE CLI MASTER DIRECTIVE
# INSTRUCTION FOR CLAUDE: You are the lead engineer. Follow the 12-section architecture with zero deviations.
--------------------------------------------------------------------------------
"""
        content = header + blueprint
        return PlainTextResponse(content, media_type="text/markdown", headers={"Content-Disposition": "attachment; filename=CLAUDE_MASTER_SPEC.md"})

    elif format == "antigravity":
        header = """# GOOGLE ANTIGRAVITY MASTER PROMPT
# DIRECTIVE: Autonomous fullstack execution with zero degrees of freedom.
--------------------------------------------------------------------------------
"""
        content = header + blueprint
        return PlainTextResponse(content, media_type="text/markdown", headers={"Content-Disposition": "attachment; filename=ANTIGRAVITY_BLUEPRINT.md"})

    return PlainTextResponse(blueprint, media_type="text/markdown", headers={"Content-Disposition": "attachment; filename=MASTER_BLUEPRINT.md"})

@router.get("/config/providers")
async def get_providers():
    """Returns live availability status of LLM providers."""
    return {
        "providers": llm_provider.get_status(),
        "section_thresholds": SECTION_THRESHOLDS
    }

@router.post("/config/providers")
async def update_providers(req: KeysUpdateRequest):
    """Update API keys at runtime without restarting the server."""
    if req.groq_key:
        settings.GROQ_API_KEY = req.groq_key.strip()
    if req.gemini_key:
        settings.GEMINI_API_KEY = req.gemini_key.strip()
    if req.mistral_key:
        settings.MISTRAL_API_KEY = req.mistral_key.strip()
    if req.cohere_key:
        settings.COHERE_API_KEY = req.cohere_key.strip()

    # Re-initialize clients
    llm_provider._init_clients()
    return {"status": "updated", "providers": llm_provider.get_status()}
