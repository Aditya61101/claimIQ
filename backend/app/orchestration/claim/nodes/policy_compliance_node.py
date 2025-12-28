from app.orchestration.claim.state import ClaimGraphState
from app.utils.constants import ClaimTypes

def policy_compliance_node(state:ClaimGraphState) -> ClaimGraphState:
    issues = []

    claim_type = state['claim_data'].get("claim_type")

    if claim_type not in {ClaimTypes.DOMICILIARY, ClaimTypes.HOSPITALIZATION}:
        issues.append({
            "code": "INVALID_CLAIM_TYPE",
            "message": "Claim type not supported by policy",
            "severity": "HIGH",
            "evidence": {"claim_type": claim_type}
        })

        # RAG HOOK
        # policy_context = policy_rag.retrieve()
        # llm_reasoning = 

        state['policy_issues'] = issues or None

        return state