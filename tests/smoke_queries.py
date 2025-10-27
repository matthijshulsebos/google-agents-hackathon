from app.orchestrator import Orchestrator


def run():
    orch = Orchestrator()
    # Nursing query (formerly finance)
    r1 = orch.answer("test-user", "What is the budget approval policy?", ["nursing"])  # explicit domain
    print("Nursing response:", r1.get("answer")[:120])
    print("Domains:", r1.get("domains"), "Retrieval:", r1.get("retrieval"))

    # Pharmacy query (formerly legal)
    r2 = orch.answer("test-user", "What does the HIPAA consent form require?", ["pharmacy"])  # explicit domain
    print("Pharmacy response:", r2.get("answer")[:120])

    # PO multi-turn (formerly healthcare)
    r3 = orch.answer("test-user", "What is the patient triage protocol?", ["po"])  # turn 1
    print("PO response:", r3.get("answer")[:120])
    r4 = orch.answer("test-user", "And what about medication administration timing?", ["po"])  # turn 2
    print("Follow-up response:", r4.get("answer")[:120])


if __name__ == "__main__":
    run()
