from .state import ClaimGraphState

def route_after_claim_consistent(state:ClaimGraphState):
    issues = state.get("consistency_issues")

    has_blocking = any(i["severity"]=="HIGH" for i in issues)

    return "blocked" if has_blocking else "continue"

def route_after_policy(state:ClaimGraphState):
    issues = state.get("policy_issues")

    has_blocking = any(i["severity"]=="HIGH" for i in issues)

    return "blocked" if has_blocking else "continue"