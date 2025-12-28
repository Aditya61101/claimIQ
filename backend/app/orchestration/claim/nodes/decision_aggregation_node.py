from app.orchestration.claim.state import ClaimGraphState

def decision_aggregation_node(state:ClaimGraphState) -> ClaimGraphState:

    if state.get("consistency_issues"):
        state['recommendation'] = 'REJECT'
        state['reasoning'] = 'Critical inconsistencies across documents'
        state['confidence'] = 0.9
        return state
    
    if state.get("policy_issues"):
        state['recommendation'] = 'REJECT'
        state['reasoning'] = 'Policy compliance violations detected'
        state['confidence'] = 0.85
        return state
    
    if state.get("fraud_signals"):
        state['recommendation'] = 'HUMAN_REVIEW'
        state['reasoning'] = 'Potential fraud indicators detected'
        state['confidence'] = 0.6
        return state
    
    state['recommendation'] = 'APPROVE'
    state['reasoning'] = 'All automated checks passed'
    state['confidence'] = 0.95
    return state