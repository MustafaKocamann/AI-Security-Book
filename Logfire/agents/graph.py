from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .nodes import planner, explainer, analyst, creator, web_searcher, formatter

def _route_intent(state: AgentState) -> str:
    intent = state.get("intent", "explain")
    if intent in ("explain", "analyze", "create", "search"):
        return intent
    return "explain"

def build_graph():
    """
    Constructs and compiles the Multi-Agent Router LangGraph workflow.
    """
    g = StateGraph(AgentState)

    # Register workflow nodes
    g.add_node("planner",      planner)
    g.add_node("explainer",    explainer)
    g.add_node("analyst",      analyst)
    g.add_node("creator",      creator)
    g.add_node("web_searcher", web_searcher)
    g.add_node("formatter",    formatter)

    # Entry point -> Planner classifies intent
    g.add_edge(START, "planner")

    # Conditional routing to the appropriate specialist
    g.add_conditional_edges(
        "planner",
        _route_intent,
        {
            "explain": "explainer",
            "analyze": "analyst",
            "create":  "creator",
            "search":  "web_searcher",
        },
    )

    # All specialist nodes converge into the Formatter
    for specialist in ("explainer", "analyst", "creator", "web_searcher"):
        g.add_edge(specialist, "formatter")

    # Formatter outputs final result to END
    g.add_edge("formatter", END)

    return g.compile()
