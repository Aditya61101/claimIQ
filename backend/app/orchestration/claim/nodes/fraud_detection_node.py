from app.orchestration.claim.state import ClaimGraphState


def fraud_detection_node(state:ClaimGraphState) -> ClaimGraphState:
    signals = []

    amount = state['claim_data'].get('claim_amount', 0)

    if amount > 10000:
        signals.append({
            "code": "HIGH_CLAIM_AMOUNT",
            "message": "Claim amount unusually high",
            "severity":"LOW",
            "evidence": {"amount": amount},
        })
    state['fraud_signals'] = signals or None

    return state