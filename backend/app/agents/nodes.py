import asyncio
import logging
from typing import Dict, Any, List
from app.services.llm_provider import llm_provider
from app.services.search_service import search_service
from app.core.templates import (
    AGENT_1_RED_TEAM_PROMPT,
    AGENT_2_RESEARCH_PROMPT,
    AGENT_3_ARCHITECT_PROMPT,
    AGENT_4_FEATURE_SPEC_PROMPT,
    AGENT_5_PERSONAS_PROMPT,
    AGENT_6_COMPETITOR_PROMPT,
    AGENT_7_UI_UX_PROMPT,
    AGENT_8_API_CONTRACT_PROMPT,
    AGENT_9_SECURITY_PERFORMANCE_PROMPT,
    AGENT_10_RISKS_EXCLUSIONS_PROMPT,
    AGENT_11_COMPILER_PROMPT,
)
from app.agents.state import BlueprintState, SECTION_THRESHOLDS, MINIMUM_TOTAL_WORDS

logger = logging.getLogger(__name__)

def count_words(text: str) -> int:
    """Helper to accurately count words in a string."""
    return len(text.strip().split()) if text else 0

# --- NODE 1: RED TEAM ADVERSARIAL CRITIC ---
async def red_team_node(state: BlueprintState) -> Dict[str, Any]:
    raw_idea = state.get("raw_idea", "")
    logger.info(f"Running Agent 1 (Red Team) for idea: {raw_idea[:60]}...")
    
    prompt = f"""Raw Product Idea:
\"\"\"{raw_idea}\"\"\"

User Constraints / Preferences:
{state.get('user_constraints', {})}

Execute your 10 brutal questions, dissect fatal flaws, and produce the Refined Survival Concept."""
    
    critique = await llm_provider.generate(
        prompt=prompt,
        system_prompt=AGENT_1_RED_TEAM_PROMPT,
        temperature=0.7
    )
    
    # Extract refined idea from critique if formatted, otherwise provide the critique
    refined = critique
    if "Refined Survival Concept" in critique:
        refined = critique.split("Refined Survival Concept")[-1].strip(": \n")
        
    log_entry = "[Agent 1: Red Team] Successfully grilled raw idea and established refined survival concept."
    return {
        "red_team_critique": critique,
        "refined_idea": refined,
        "active_agent": "Red Team Critic",
        "current_step": "Red-team adversarial analysis complete",
        "logs": state.get("logs", []) + [log_entry]
    }

# --- NODE 2: WEB INTELLIGENCE & MARKET RESEARCH ---
async def research_node(state: BlueprintState) -> Dict[str, Any]:
    refined_idea = state.get("refined_idea") or state.get("raw_idea", "")
    logger.info(f"Running Agent 2 (Web Intelligence) via DuckDuckGo...")
    
    search_data = await search_service.run_structured_protocol(refined_idea[:150])
    
    prompt = f"""Refined Product Concept:
\"\"\"{refined_idea}\"\"\"

Live Internet Search Intelligence:
{search_data}

Synthesize this data into the 5 required research dimensions (Market Sizing, Competitor Landscape, Audience Frustrations, Technical Ecosystem, Legal/Regulatory)."""
    
    market_intel = await llm_provider.generate(
        prompt=prompt,
        system_prompt=AGENT_2_RESEARCH_PROMPT,
        temperature=0.5
    )
    
    log_entry = f"[Agent 2: Researcher] Retrieved live web intelligence across 5 categories ({sum(len(v) for v in search_data.values())} search results)."
    return {
        "research_data": search_data,
        "section_2_market": market_intel,
        "active_agent": "Web Researcher",
        "current_step": "Web and competitor intelligence gathered",
        "logs": state.get("logs", []) + [log_entry]
    }

# --- NODE 3: TECHNICAL FEASIBILITY & SYSTEMS ARCHITECT ---
async def architect_node(state: BlueprintState) -> Dict[str, Any]:
    refined_idea = state.get("refined_idea", "")
    research_summary = state.get("section_2_market", "")[:1000]
    
    prompt = f"""Refined Product Concept:
\"\"\"{refined_idea}\"\"\"

Market & Technical Research Context:
\"\"\"{research_summary}\"\"\"

User Stack Preferences:
{state.get('user_constraints', {})}

Make definitive architectural decisions with explicit justifications for frameworks, DB schema, 3rd party APIs, auth, and hosting."""
    
    arch_output = await llm_provider.generate(
        prompt=prompt,
        system_prompt=AGENT_3_ARCHITECT_PROMPT,
        temperature=0.4
    )
    
    log_entry = "[Agent 3: Systems Architect] Modeled full database schemas, stack versions, and API integrations."
    return {
        "section_6_tech_arch": arch_output,
        "active_agent": "Systems Architect",
        "current_step": "Technical architecture and database schema designed",
        "logs": state.get("logs", []) + [log_entry]
    }

def update_job_progress(job_id: str, active_agent: str = None, current_step: str = None, log: str = None, section: tuple = None):
    """Safely pushes incremental progress to the in-memory job store so SSE streams emit in real-time."""
    if not job_id:
        return
    try:
        from app.api.routes import jobs
        if job_id in jobs:
            if active_agent:
                jobs[job_id]["active_agent"] = active_agent
            if current_step:
                jobs[job_id]["current_step"] = current_step
            if log:
                jobs[job_id]["logs"].append(log)
            if section:
                sec_key, sec_val = section
                jobs[job_id]["sections"][sec_key] = sec_val
    except Exception:
        pass

# --- NODE 4: SECTION DRAFTING SUITE (SECTIONS 1 TO 12) ---
async def section_drafting_node(state: BlueprintState) -> Dict[str, Any]:
    """Drafts remaining specialized sections with concurrency pacing."""
    refined_idea = state.get("refined_idea", "")
    critique = state.get("red_team_critique", "")[:1000]
    tech_arch = state.get("section_6_tech_arch", "")[:1200]
    market = state.get("section_2_market", "")[:1200]

    context = f"""Product Concept: {refined_idea}
Architectural Decisions: {tech_arch}
Market Research: {market}
Red-Team Notes: {critique}"""



    # Section 1: Vision (Groq/Cohere)
    async def draft_vision():
        p = f"{context}\n\nDraft Section 1: Verified Product Vision. Must include exact problem, scope boundaries, anti-scope, one-sentence and paragraph pitch, and success metrics. Target: 800 words."
        return await llm_provider.generate(p, AGENT_1_RED_TEAM_PROMPT, preferred_provider="groq")

    # Section 3: Personas (Groq)
    async def draft_personas():
        p = f"{context}\n\nDraft Section 3: Target Audience & User Personas. Document Primary, Secondary, and Anti-Persona with daily routine, psychology, and WCAG AA accessibility requirements. Target: 1,500 words."
        return await llm_provider.generate(p, AGENT_5_PERSONAS_PROMPT, preferred_provider="groq")

    # Section 4: Competitors (Groq)
    async def draft_competitors():
        p = f"{context}\n\nDraft Section 4: Competitor Analysis & Moat. Detail top 5 direct competitors, 3 indirect, feature comparison matrix, and positioning statement. Target: 1,500 words."
        return await llm_provider.generate(p, AGENT_6_COMPETITOR_PROMPT, preferred_provider="groq")

    # Section 5: Features (Groq)
    async def draft_features():
        p = f"{context}\n\nDraft Section 5: Full Product Feature Specification. For every MVP feature document: user flow, validation rules, error states, empty states, loading states, and success states. Target: 3,000 words."
        return await llm_provider.generate(p, AGENT_4_FEATURE_SPEC_PROMPT, preferred_provider="groq")

    # Section 7: API Contract (Groq)
    async def draft_api():
        p = f"{context}\n\nDraft Section 7: Full REST API Contract. Every endpoint: route, method, request JSON schema, response 200 JSON schema, error 400/401/404/500 schemas, auth, and rate limits. Target: 1,500 words."
        return await llm_provider.generate(p, AGENT_8_API_CONTRACT_PROMPT, preferred_provider="groq")

    # Section 8: File Architecture (Groq)
    async def draft_file_arch():
        p = f"{context}\n\nDraft Section 8: File & Folder Architecture. Complete directory tree, module responsibilities, naming conventions, and every single .env variable with description. Target: 800 words."
        return await llm_provider.generate(p, "You are a Principal Software Architect. Provide the complete project folder structure.", preferred_provider="groq")

    # Section 9: UI/UX (Groq)
    async def draft_ui_ux():
        p = f"{context}\n\nDraft Section 9: UI/UX Specification. Screen-by-screen breakdown, component trees, exact 6-digit hex color palette, typography scale, and responsive breakpoints. Target: 1,500 words."
        return await llm_provider.generate(p, AGENT_7_UI_UX_PROMPT, preferred_provider="groq")

    # Section 10: Security (Groq)
    async def draft_security():
        p = f"{context}\n\nDraft Section 10: Security & Performance Requirements. Auth encryption, sanitization, rate limits, performance benchmarks (LCP < 2.0s, API p95 < 200ms). Target: 800 words."
        return await llm_provider.generate(p, AGENT_9_SECURITY_PERFORMANCE_PROMPT, preferred_provider="groq")

    # Section 11: Execution Phases (Groq)
    async def draft_execution():
        p = f"{context}\n\nDraft Section 11: Phased IDE Execution Instructions. Phase 1 to Phase 8 sequential instructions for the AI IDE with mandatory verification checklists. Target: 1,500 words."
        return await llm_provider.generate(p, "You are an AI IDE Director. Detail Phase 1 to 8 execution instructions with strict verification checklists.", preferred_provider="groq")

    # Section 12: Risks (Groq)
    async def draft_risks():
        p = f"{context}\n\nDraft Section 12: Known Risks & Exclusions. Deceptive complexities, junior developer anti-patterns, and deliberately excluded features with reasons. Target: 600 words."
        return await llm_provider.generate(p, AGENT_10_RISKS_EXCLUSIONS_PROMPT, preferred_provider="groq")

    sections_plan = [
        ("Section 1 (Vision)", "section_1_vision", draft_vision),
        ("Section 3 (Personas)", "section_3_personas", draft_personas),
        ("Section 4 (Competitors)", "section_4_competitors", draft_competitors),
        ("Section 5 (Features)", "section_5_features", draft_features),
        ("Section 7 (API Contract)", "section_7_api_contract", draft_api),
        ("Section 8 (File Architecture)", "section_8_file_arch", draft_file_arch),
        ("Section 9 (UI/UX)", "section_9_ui_ux", draft_ui_ux),
        ("Section 10 (Security)", "section_10_security", draft_security),
        ("Section 11 (Execution Phases)", "section_11_execution_phases", draft_execution),
        ("Section 12 (Risks)", "section_12_risks", draft_risks),
    ]
    job_id = state.get("job_id")
    results = {}
    for title, state_key, fn in sections_plan:
        update_job_progress(job_id, active_agent=title, current_step=f"Drafting {title}...", log=f"Drafting {title}...")
        logger.info(f"===> Started drafting: {title}")
        content = await fn()
        w = count_words(content)
        logger.info(f"<=== Completed drafting: {title} ({w:,} words)")
        results[state_key] = content
        update_job_progress(job_id, section=(state_key, content), log=f"[{title}] Completed ({w:,} words)")
        await asyncio.sleep(0.3)

    log_entry = "[Agents 4-10: Specialized Drafters] All 12 specialized architectural sections drafted successfully."
    response = {
        "active_agent": "Section Drafters",
        "current_step": "All 12 sections drafted, proceeding to word count audit",
        "logs": state.get("logs", []) + [log_entry]
    }
    response.update(results)
    return response

# --- NODE 5: WORD COUNT & QUALITY INSPECTOR ---
async def inspector_node(state: BlueprintState) -> Dict[str, Any]:
    """Audits word counts of each section against minimum thresholds."""
    word_counts = {}
    total_words = 0
    under_target = []
    attempts = state.get("expansion_attempts", {})

    for sec_key, conf in SECTION_THRESHOLDS.items():
        text = state.get(sec_key, "")
        count = count_words(text)
        word_counts[sec_key] = count
        total_words += count

        # If below min and hasn't had an expansion pass
        curr_attempts = attempts.get(sec_key, 0)
        if count < conf["min"] and curr_attempts < 1:
            under_target.append(sec_key)

    log_entry = f"[Agent 11: Inspector] Word count audit complete: {total_words:,} total words across 12 sections. Expanding {len(under_target)} sections."
    return {
        "word_counts": word_counts,
        "total_words": total_words,
        "under_target_sections": under_target,
        "active_agent": "Word Count Inspector",
        "current_step": f"Word count audit: {total_words:,} words across 12 sections",
        "logs": state.get("logs", []) + [log_entry]
    }

# --- NODE 6: SECTION EXPANDER LOOP ---
async def expander_node(state: BlueprintState) -> Dict[str, Any]:
    """Expands under-target sections sequentially with deep concrete technical specifications."""
    job_id = state.get("job_id")
    under_target = state.get("under_target_sections", [])
    attempts = dict(state.get("expansion_attempts", {}))
    updated_sections = {}

    for sec_key in under_target:
        current_text = state.get(sec_key, "")
        conf = SECTION_THRESHOLDS.get(sec_key, {"title": sec_key, "min": 800, "target": 1200})
        current_words = count_words(current_text)
        deficit = max(conf["min"] - current_words, 200)
        attempts[sec_key] = attempts.get(sec_key, 0) + 1

        update_job_progress(job_id, active_agent="Section Expander", current_step=f"Deepening {conf['title']}...", log=f"Deepening {conf['title']} with exhaustive specifications...")

        prompt = f"""Section: {conf['title']}
Context Summary of Current Draft:
\"\"\"{current_text[:1200]}\"\"\"

EXPANSION DIRECTIVE:
Provide exhaustive, highly technical implementation sub-specifications to complement and expand this section.
Focus purely on:
- Complete step-by-step edge cases, failure recovery workflows, and state transitions.
- Concrete TypeScript types, JSON schemas, regex validation patterns, and HTTP status codes.
- Precise implementation constraints, memory budgets, and security verification checklists.
Provide only new, exhaustive technical content without repeating the introduction."""

        logger.info(f"===> Expanding section: {conf['title']} (current: {current_words} words)")
        appendix = await llm_provider.generate(
            prompt=prompt,
            system_prompt="You are a Principal Software Engineer & Systems Architect. Provide exhaustive, concrete technical specifications and zero high-level fluff.",
            preferred_provider="groq",
            temperature=0.6
        )
        combined = f"{current_text}\n\n### Exhaustive Implementation Details & Failure Modes\n\n{appendix}"
        w = count_words(combined)
        logger.info(f"<=== Finished expanding: {conf['title']} ({w:,} words)")
        updated_sections[sec_key] = combined
        update_job_progress(job_id, section=(sec_key, combined), log=f"[{conf['title']}] Expanded to {w:,} words")
        await asyncio.sleep(0.3)

    log_entry = f"[Expander Loop] Expanded {len(under_target)} sections to satisfy word-count thresholds."
    result = {
        "expansion_attempts": attempts,
        "active_agent": "Section Expander",
        "current_step": f"Expanded {len(under_target)} sections",
        "logs": state.get("logs", []) + [log_entry]
    }
    result.update(updated_sections)
    return result

# --- NODE 7: MASTER COMPILER ---
async def compiler_node(state: BlueprintState) -> Dict[str, Any]:
    """Assembles all 12 sections into a unified Master Blueprint document."""
    logger.info("Compiling final Master Blueprint...")
    
    sections = [
        f"# MASTER SYSTEM SPECIFICATION & ONE-SHOT PROMPT FOR AI IDEs\n\n**Generated for:** {state.get('raw_idea')}\n**Target IDEs:** Cursor / Claude Code / Antigravity\n\n---\n",
        f"## SECTION 1 — VERIFIED PRODUCT VISION\n\n{state.get('section_1_vision', '')}\n\n---\n",
        f"## SECTION 2 — MARKET & INDUSTRY INTELLIGENCE\n\n{state.get('section_2_market', '')}\n\n---\n",
        f"## SECTION 3 — TARGET AUDIENCE & USER PERSONAS\n\n{state.get('section_3_personas', '')}\n\n---\n",
        f"## SECTION 4 — COMPETITOR ANALYSIS & DIFFERENTIATION\n\n{state.get('section_4_competitors', '')}\n\n---\n",
        f"## SECTION 5 — FULL PRODUCT FEATURE SPECIFICATION\n\n{state.get('section_5_features', '')}\n\n---\n",
        f"## SECTION 6 — TECHNICAL ARCHITECTURE & DATABASE SCHEMAS\n\n{state.get('section_6_tech_arch', '')}\n\n---\n",
        f"## SECTION 7 — FULL REST API CONTRACT\n\n{state.get('section_7_api_contract', '')}\n\n---\n",
        f"## SECTION 8 — FILE & FOLDER ARCHITECTURE\n\n{state.get('section_8_file_arch', '')}\n\n---\n",
        f"## SECTION 9 — UI/UX & DESIGN SYSTEM SPECIFICATION\n\n{state.get('section_9_ui_ux', '')}\n\n---\n",
        f"## SECTION 10 — SECURITY & PERFORMANCE BENCHMARKS\n\n{state.get('section_10_security', '')}\n\n---\n",
        f"## SECTION 11 — PHASED IDE EXECUTION INSTRUCTIONS\n\n{state.get('section_11_execution_phases', '')}\n\n---\n",
        f"## SECTION 12 — KNOWN RISKS, ANTI-PATTERNS & EXCLUSIONS\n\n{state.get('section_12_risks', '')}\n\n---\n",
    ]
    
    final_blueprint = "".join(sections)
    final_total_words = count_words(final_blueprint)
    
    log_entry = f"[Agent 11: Master Compiler] Compiled complete Master Blueprint. Final total word count: {final_total_words:,} words."
    return {
        "final_blueprint": final_blueprint,
        "total_words": final_total_words,
        "is_complete": True,
        "active_agent": "Master Compiler",
        "current_step": "Master Blueprint compilation complete",
        "logs": state.get("logs", []) + [log_entry]
    }
