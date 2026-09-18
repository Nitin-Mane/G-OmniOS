"""G-OmniOS Python SDK Quickstart Example.

Demonstrates programmatic usage of G-OmniOS as an AI memory and cognitive OS:
1. Initialize the system
2. Execute a 4-phase Mind4Action reasoning cycle (Perceive -> Reflect -> Intend -> Act)
3. Log out-of-band execution steps to Google LevelDB WAL without prompt bloat
4. Query semantic memory via Google ScaNN vector search
5. Inspect and optimize prompt context using the Context Governor
6. Consult specialized agent departments (Manager, Fullstack AI)
7. Generate token savings report
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from omni_memory import GOmniOSSystem, StepPhase


def main():
    print("================================================================")
    print("  G-OmniOS: Python SDK Programmatic Quickstart")
    print("================================================================\n")

    # 1. Initialize G-OmniOS System
    system = GOmniOSSystem()
    print("[1] Initialized G-OmniOS System (LevelDB WAL + ScaNN Vector Space)\n")

    # 2. Execute Mind4Action 4-Phase Cognitive Cycle
    stimulus = "Synthesize an algorithmic trading strategy with risk parity constraints"
    print(f"[2] Running Mind4Action Cognitive Cycle for stimulus:\n    '{stimulus}'")
    turn = system.mind4action_cycle(stimulus)
    refl = turn.get("reflection", {})
    inten = turn.get("intention", {})
    act = turn.get("action_result", {})

    print(f"    • Perceived Tracks: {refl.get('tracks_perceived')}")
    print(f"    • Cognitive Load Index (CLI): {refl.get('cli', 0.0):.2f}")
    print(f"    • Flow Score: {refl.get('flow_score', 0.0):.2f}")
    print(f"    • Target Action: {inten.get('target_action')}")
    print(f"    • Action Status: {act.get('status')} (Logged to WAL)\n")

    # 3. Log Out-of-Band Steps (Zero Prompt Bloat)
    print("[3] Logging Out-of-Band Execution Steps to LevelDB WAL...")
    s1 = system.step(
        phase=StepPhase.DELIBERATION,
        title="Analyze Covariance Matrix",
        thought="Calculating inverse variance weights across 4 asset classes: [0.35, 0.25, 0.20, 0.20].",
        observation="Weights normalized successfully."
    )
    s2 = system.step(
        phase=StepPhase.PLANNING,
        title="Formulate Volatility Trigger Rule",
        thought="If trailing 30d annualized volatility exceeds 18%, apply dynamic scale factor of 0.85.",
        observation="Rule indexed into ScaNN memory space.",
        is_milestone=True
    )
    print(f"    • Step #{s1.sequence_num}: {s1.title} (+{s1.token_weight} tokens saved)")
    print(f"    • Step #{s2.sequence_num}: {s2.title} (Milestone checkpoint)\n")

    # 4. Query Semantic Memory via ScaNN
    query = "volatility trigger rule"
    print(f"[4] Querying Semantic Memory via ScaNN for: '{query}'")
    results = system.scann.search(query, top_k=2)
    for i, res in enumerate(results, 1):
        print(f"    Match #{i}: [Score: {res.score:.4f}] {res.text}")
    print()

    # 5. Inspect and Optimize Prompt Context (Context Governor)
    test_text = "I am designing a distributed consensus state machine with strict quorum replication."
    print(f"[5] Context Governor Inspection on: '{test_text}'")
    gov_report = system.inspect_firewall(test_text)
    print(f"    • Verdict: {gov_report['verdict']}")
    print(f"    • Triggered Rules: {gov_report['triggered_rules']}")
    print(f"    • Suggested Action: {gov_report['suggested_mitigation']}\n")

    # 6. Consult Organizational Agent Departments
    print("[6] Consulting Specialized Agent Department: Manager Agent")
    dept_res = system.dispatch_department("manager", "Generate sprint deliverable status and token KPI report")
    print(f"    • Manager Agent Response: {dept_res.get('status')}")
    print(f"    • Active Sprint: {dept_res.get('active_sprint', {}).get('name')}\n")

    # 7. Token Savings Report
    report = system.allocator.generate_report()
    prompt_info = system.task_agent.get_current_prompt_window()
    print("[7] Token Economics & Savings Report:")
    print(f"    • Total Raw Tokens Generated: {report.total_raw_tokens_generated:,}")
    print(f"    • Active Working Prompt Load: {prompt_info['token_count']} / 800 tokens")
    print(f"    • Prompt Tokens Saved:        {report.tokens_saved:,} ({report.savings_percentage:.1f}%)")
    print(f"    • Out-of-Band Memory Ratio:   {report.compression_ratio:.1f}x\n")

    print("================================================================")
    print("  Quickstart completed successfully! 100% local, zero cloud cost.")
    print("================================================================")


if __name__ == "__main__":
    main()
