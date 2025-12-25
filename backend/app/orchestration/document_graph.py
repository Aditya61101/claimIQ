from langgraph.graph import StateGraph, END

from app.orchestration.states import DocumentState
from app.orchestration.nodes import document_validation_node, document_verification_node
from app.orchestration.routers import document_router

def build_document_graph():

    graph = StateGraph(DocumentState)

    graph.add_node("validate", document_validation_node)
    graph.add_node("verify", document_verification_node)


    graph.add_conditional_edges("validate", document_router, {
        "verify": "verify",
        "end": END
    })

    graph.add_edge("verify", END)

    graph.set_entry_point("validate")

    return graph.compile()

document_graph = build_document_graph()
