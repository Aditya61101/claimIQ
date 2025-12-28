from langgraph.graph import StateGraph
from .state import ClaimGraphState
from .nodes import *
from .routers import route_after_claim_consistent, route_after_policy

def build_claim_graph():
    graph = StateGraph(ClaimGraphState)

    graph.add_node("claim_consistency", claim_consistency_node)
    graph.add_node("policy", policy_compliance_node)
    graph.add_node("deep_extract", deep_extraction_node)
    graph.add_node("fraud", fraud_detection_node)
    graph.add_node("decision", decision_aggregation_node)

    graph.set_entry_point("claim_consistency")

    graph.add_conditional_edges("claim_consistency", route_after_claim_consistent, {
        "continue": "policy",
        "blocked": "decision"
    })

    graph.add_conditional_edges("policy", route_after_policy, {
        "continue": "deep_extract",
        "blocked": "decision"
    })

    graph.add_edge("deep_extract", "fraud")
    graph.add_edge("fraud", "decision")

    return graph.compile()

claim_graph = build_claim_graph()
