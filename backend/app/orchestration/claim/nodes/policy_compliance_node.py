from app.orchestration.claim.state import ClaimGraphState
from app.utils.constants import ClaimTypes

def policy_compliance_node(state:ClaimGraphState) -> ClaimGraphState:
    issues = []

    claim_type = state['claim_data'].get("claim_type")
    claim_amount = state['claim_data'].get("claim_amount")
    policy = state['policy_data']

    if claim_type not in {ClaimTypes.DOMICILIARY, ClaimTypes.HOSPITALIZATION}:
        issues.append({
            "code": "INVALID_CLAIM_TYPE",
            "message": "Claim type not supported by our policy.",
            "severity": "HIGH",
            "evidence": {"claim_type": claim_type}
        })

    remaining_sum_insured = policy['total_sum_insured'] - policy['approved_claim_amount']
    if remaining_sum_insured > claim_amount:
        issues.append({
            "code": "SUM_INSURED_EXCEEDED",
            "message": f"Claim amount {claim_amount} exceeds remaining sum insured",
            "severity": "HIGH",
            "evidence": {
                "policy_number": policy['policy_number'],
                "claim_amount": claim_amount,
                "remaining_sum_insured": remaining_sum_insured,
                "total_sum_insured": policy['total_sum_insured'],
                "approved_amount": policy['approved_claim_amount']
            }
        })

    # if already blocked, we need not to go for RAG
    if issues:
        state['policy_issues'] = issues or None
        return state

    # RAG BASED CHECKS
    # policy_context = policy_rag.retrieve()
    # llm_reasoning = 
    state['policy_issues'] = issues or None
    return state