from typing import TypedDict, Dict, Any, List, Optional

class BlueprintState(TypedDict, total=False):
    # Inputs
    job_id: str
    raw_idea: str
    user_constraints: Dict[str, Any]
    
    # Progress & Logs
    current_step: str
    logs: List[str]
    active_agent: str
    
    # Agent Artifacts
    red_team_critique: str
    refined_idea: str
    research_data: Dict[str, Any]
    
    # 12 Blueprint Sections
    section_1_vision: str
    section_2_market: str
    section_3_personas: str
    section_4_competitors: str
    section_5_features: str
    section_6_tech_arch: str
    section_7_api_contract: str
    section_8_file_arch: str
    section_9_ui_ux: str
    section_10_security: str
    section_11_execution_phases: str
    section_12_risks: str
    
    # Word Counts & Auditing
    word_counts: Dict[str, int]
    total_words: int
    expansion_attempts: Dict[str, int]
    under_target_sections: List[str]
    
    # Final Output
    final_blueprint: str
    is_complete: bool
    error: Optional[str]

# Strict section minimum word count thresholds
SECTION_THRESHOLDS = {
    "section_1_vision": {"min": 500, "target": 800, "title": "Verified Product Vision"},
    "section_2_market": {"min": 1500, "target": 2000, "title": "Market & Industry Intelligence"},
    "section_3_personas": {"min": 1000, "target": 1500, "title": "Target Audience & Personas"},
    "section_4_competitors": {"min": 1000, "target": 1500, "title": "Competitor Analysis & Differentiation"},
    "section_5_features": {"min": 2000, "target": 3000, "title": "Full Product Feature Specification"},
    "section_6_tech_arch": {"min": 2000, "target": 2500, "title": "Technical Architecture & Schemas"},
    "section_7_api_contract": {"min": 1000, "target": 1500, "title": "Full API Contract"},
    "section_8_file_arch": {"min": 500, "target": 800, "title": "File & Folder Architecture"},
    "section_9_ui_ux": {"min": 1000, "target": 1500, "title": "UI/UX & Design Systems Specification"},
    "section_10_security": {"min": 500, "target": 800, "title": "Security & Performance Requirements"},
    "section_11_execution_phases": {"min": 1000, "target": 1500, "title": "Phased IDE Execution Instructions"},
    "section_12_risks": {"min": 500, "target": 600, "title": "Known Risks, Anti-Patterns & Exclusions"},
}

MINIMUM_TOTAL_WORDS = 15000
