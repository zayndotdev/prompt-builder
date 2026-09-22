import logging
from langgraph.graph import StateGraph, END
from app.agents.state import BlueprintState
from app.agents.nodes import (
    red_team_node,
    research_node,
    architect_node,
    section_drafting_node,
    inspector_node,
    expander_node,
    compiler_node,
)

logger = logging.getLogger(__name__)

def should_expand(state: BlueprintState) -> str:
    """Conditional router: checks if any section needs expansion."""
    under_target = state.get("under_target_sections", [])
    if under_target:
        logger.info(f"Routing to expander for {len(under_target)} sections...")
        return "expander"
    logger.info("All sections satisfied word-count audit. Routing to compiler...")
    return "compiler"

def build_blueprint_graph():
    """Builds and compiles the cyclic LangGraph multi-agent workflow."""
    workflow = StateGraph(BlueprintState)

    # Add Nodes
    workflow.add_node("red_team", red_team_node)
    workflow.add_node("research", research_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("section_drafting", section_drafting_node)
    workflow.add_node("inspector", inspector_node)
    workflow.add_node("expander", expander_node)
    workflow.add_node("compiler", compiler_node)

    # Set Entry Point
    workflow.set_entry_point("red_team")

    # Linear Edges
    workflow.add_edge("red_team", "research")
    workflow.add_edge("research", "architect")
    workflow.add_edge("architect", "section_drafting")
    workflow.add_edge("section_drafting", "inspector")

    # Conditional Cyclic Edge
    workflow.add_conditional_edges(
        "inspector",
        should_expand,
        {
            "expander": "expander",
            "compiler": "compiler"
        }
    )

    # Loop back from expander to inspector
    workflow.add_edge("expander", "inspector")

    # End
    workflow.add_edge("compiler", END)

    return workflow.compile()

blueprint_graph = build_blueprint_graph()
