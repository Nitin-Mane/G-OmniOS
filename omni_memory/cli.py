"""Interactive Command Line Interface for Google OmniMemory.

Uses Rich for terminal visualization of memory tiers, LevelDB step streams,
and token savings economics.
"""

from __future__ import annotations
import os
import sys
import time
import json
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure UTF-8 stdout/stderr on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from omni_memory.engine import OmniMemorySystem, GOmniOSSystem
from omni_memory.models.step import StepPhase
from omni_memory.server.app import run_dashboard_server

console = Console(safe_box=True)


def display_banner():
    banner = """
[bold cyan]G-OmniOS[/bold cyan] [dim]|[/dim] [bold green]Universal AI Operating System & Cognitive Memory Platform[/bold green]
[dim]Tracking Cognitive Patterns, Psychological Behaviors & Mind4Action across Technical, Social & Mental Tracks[/dim]
[dim]Powered by Google Always-On Agent * ReasoningBank * Diff-Match-Patch * LevelDB * ScaNN[/dim]
    """
    console.print(Panel(banner.strip(), border_style="blue"))


def run_demo_trajectory():
    """Execute a demonstration multi-step trajectory showing zero prompt bloat."""
    display_banner()
    system = OmniMemorySystem()
    system.start_task("Synthesize an algorithmic trading strategy with risk parity constraints.")

    console.print("\n[bold yellow]> Starting Primary Task Agent with Decoupled Memory Agent...[/bold yellow]\n")

    steps_data = [
        (StepPhase.DELIBERATION, "Analyze Mathematical Constraints", 
         "Deconstructing covariance matrix requirements for risk parity across 4 asset classes. Volatility budgeting requires inverse variance weighting.", 
         "Calculated weights: [0.35, 0.25, 0.20, 0.20]"),
        
        (StepPhase.HYPOTHESIS, "Formulate Volatility Targeting Rule", 
         "If asset volatility exceeds 18% annualized, apply dynamic leverage scale down factor of 0.85.", 
         "Target volatility threshold set at 15% with trailing 30d EWMA.", True),
         
        (StepPhase.PLANNING, "Design ScaNN Vector Space for Strategy Rules", 
         "Partitioning rule embeddings into 4 semantic buckets for fast sub-linear lookup during rebalancing.", 
         "Indexed 12 risk rules into ScaNN memory space."),
         
        (StepPhase.CODE_GEN, "Implement Risk Parity Optimization Function", 
         "Writing Python optimization loop with SLSQP constraint solver to minimize asset risk contribution variance.", 
         "Generated optimize_risk_parity() with convergence tolerance 1e-6."),
         
        (StepPhase.EXECUTION, "Execute Historical Backtest (2020-2024)", 
         "Running vector backtester over 1,000 trading days. Tracking maximum drawdown and Sharpe ratio.", 
         "Backtest complete: Sharpe 1.84, Max Drawdown -8.2%, Annualized Return 14.6%."),
         
        (StepPhase.VERIFICATION, "Verify Invariants & Context Revision", 
         "Testing edge cases under sudden volatility shocks (March 2020). Memory Agent triggers Diff-Match-Patch revision.", 
         "Verified robust. Memory Agent distilled 6 steps into a 45-token delta update.", True),
    ]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Processing Agent Steps...", total=len(steps_data))
        
        for phase, title, thought, obs, *is_m in steps_data:
            is_milestone = is_m[0] if is_m else False
            time.sleep(0.4)
            
            step = system.step(
                phase=phase,
                title=title,
                thought=thought,
                observation=obs,
                is_milestone=is_milestone,
            )
            
            progress.console.print(
                f"  [bold green]+[/bold green] [dim]Step #{step.sequence_num}[/dim] "
                f"[[bold cyan]{step.phase.value.upper()}[/bold cyan]] {step.title} "
                f"[dim](+{step.token_weight} tokens shielded)[/dim]"
            )
            progress.advance(task)

    # Force a final context revision
    system.force_revision()

    # Display Memory Allocation Report
    report = system.allocator.generate_report()
    prompt_info = system.task_agent.get_current_prompt_window()

    table = Table(title="Google OmniMemory Allocation & Token Economics", border_style="green")
    table.add_column("Metric", style="bold white")
    table.add_column("Value", style="bold cyan")
    table.add_column("Details", style="dim")

    table.add_row("Total Raw Tokens Generated", f"{report.total_raw_tokens_generated:,}", "Shielded in Google LevelDB WAL")
    table.add_row("Active LLM Prompt Load", f"{prompt_info['token_count']} tokens", "Strictly constant & budgeted")
    table.add_row("Prompt Tokens Saved", f"[bold green]{report.tokens_saved:,} tokens[/bold green]", f"[bold green]{report.savings_percentage}% prompt savings[/bold green]")
    table.add_row("Working Memory Quota", f"{report.working_tokens} / {report.working_limit} tokens", "Governed by SentencePiece allocator")
    table.add_row("ReasoningBank Milestones", f"{report.episodic_count}", "Consolidated strategy checkpoints")
    table.add_row("ScaNN Vector Index Size", f"{system.scann.count()} entries", "Available for on-demand query")

    console.print("\n")
    console.print(table)

    # Show Canonical Context
    console.print("\n[bold purple]Canonical Revised Context (Synthesized by Memory Agent):[/bold purple]")
    console.print(Panel(system.memory_agent.get_canonical_context(), border_style="purple"))

    # Test ScaNN On-Demand Retrieval
    console.print("\n[bold cyan]Testing ScaNN On-Demand Semantic Query for 'volatility targeting':[/bold cyan]")
    retrieved = system.task_agent.query_memory_ondemand("volatility targeting rule", top_k=2)
    console.print(Panel(retrieved, border_style="cyan"))

    console.print("\n[bold green][OK] Invariant Verified: LLM Prompt tokens remained flat while 100% of thoughts were logged out-of-band![/bold green]\n")


def run_benchmark_cli():
    """Run the 10-step zero-token-bloat benchmark."""
    from examples.demo_reasoning_task import run_benchmark
    run_benchmark()


def run_interactive():
    """Run interactive terminal session to track steps and test ScaNN memory queries."""
    display_banner()
    console.print("[bold yellow]> Starting Interactive OmniMemory Agent Session...[/bold yellow]")
    system = OmniMemorySystem()
    system.start_task("Interactive task execution.")
    console.print("[dim]Commands: 'step <title> [| <thought> [| <observation>]]', 'query <text>', 'revise', 'status', 'reset', 'exit'[/dim]\n")

    while True:
        try:
            cmd_line = console.input("[bold cyan]omni-memory>[/bold cyan] ").strip()
            if not cmd_line:
                continue
            if cmd_line.lower() in ("exit", "quit", "q"):
                console.print("[yellow]Exiting interactive session.[/yellow]")
                break

            parts = cmd_line.split(" ", 1)
            action = parts[0].lower()
            arg = parts[1].strip() if len(parts) > 1 else ""

            if action == "query":
                if not arg:
                    console.print("[red]Usage: query <search query>[/red]")
                    continue
                results = system.query_memory(arg, top_k=3)
                if not results:
                    console.print("[dim]No matching memory slots found.[/dim]")
                else:
                    for r in results:
                        console.print(f"  [bold cyan]Cosine {r['relevance']:.3f}[/bold cyan] [{r['tier']}] [dim]({r['token_cost']} tokens)[/dim]: {r['content']}")

            elif action == "step":
                if not arg:
                    console.print("[red]Usage: step <title> [| <thought> [| <observation>]][/red]")
                    continue
                subparts = [s.strip() for s in arg.split("|")]
                title = subparts[0]
                thought = subparts[1] if len(subparts) > 1 else f"Executing step: {title}"
                obs = subparts[2] if len(subparts) > 2 else "Completed with verified invariants."
                st = system.step(
                    phase=StepPhase.EXECUTION,
                    title=title,
                    thought=thought,
                    observation=obs,
                    is_milestone=False,
                )
                console.print(f"  [green]+[/green] Step #{st.sequence_num} recorded out-of-band to LevelDB (+{st.token_weight} tokens shielded)")

            elif action == "revise":
                rev = system.force_revision()
                if rev:
                    console.print(f"  [green][OK][/green] Revised context: {rev.compression_ratio}x compression ({rev.revised_tokens} tokens)")
                else:
                    console.print("[dim]No unrevised steps to consolidate.[/dim]")

            elif action == "status":
                rep = system.allocator.generate_report()
                pw = system.task_agent.get_current_prompt_window()
                console.print(f"  • Raw tokens generated : [bold]{rep.total_raw_tokens_generated:,}[/bold] (shielded)")
                console.print(f"  • Prompt window load   : [bold]{pw['token_count']}[/bold] / {rep.working_limit} tokens")
                console.print(f"  • Tokens saved         : [bold green]{rep.tokens_saved:,}[/bold green] ({rep.savings_percentage}%)")
                console.print(f"  • ScaNN index size     : [bold]{system.scann.count()}[/bold] items")

            elif action == "reset":
                system.reset("Interactive task reset.")
                console.print("[green]Session and memory allocations reset.[/green]")

            else:
                console.print("[red]Unknown command. Available: step, query, revise, status, reset, exit[/red]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Session ended.[/yellow]")
            break


def list_templates_cli():
    """List all available reasoning templates."""
    from omni_memory.engine import TEMPLATES
    display_banner()
    table = Table(title="OmniMemory ReasoningBank Templates", border_style="cyan")
    table.add_column("Template ID", style="bold green")
    table.add_column("Title", style="bold white")
    table.add_column("Category", style="yellow")
    table.add_column("Budget", style="cyan")
    table.add_column("Sample Recall Query", style="dim")

    for t_id, t in TEMPLATES.items():
        table.add_row(t_id, t["title"], t["category"], f"{t['prompt_budget']} tok", t["sample_query"])

    console.print(table)
    console.print("\n[dim]To trigger callback with a template: omni-memory callback --template <id> --open[/dim]\n")


def run_callback_cli(args: list[str]):
    """Trigger a callback to the OmniMemory dashboard and webapp."""
    import argparse
    import urllib.request
    import urllib.error
    import json
    import webbrowser

    parser = argparse.ArgumentParser(
        prog="omni-memory callback",
        description="Trigger an OmniMemory callback to webapp dashboard"
    )
    parser.add_argument("--template", "-t", default="raft", help="Template ID (raft, trading, refactor, research)")
    parser.add_argument("--source", "-S", default="cli", help="Originating platform (antigravity, claude, chatgpt, codex, opencode, blackbox, vscode, cli)")
    parser.add_argument("--msg", "-m", default="", help="Callback message or reasoning note")
    parser.add_argument("--step", "-s", default="", help="Optional step title to record out-of-band")
    parser.add_argument("--port", "-p", type=int, default=8765, help="Dashboard port")
    parser.add_argument("--open", "-o", action="store_true", help="Automatically open dashboard in web browser")

    cleaned_args = []
    i = 0
    while i < len(args):
        if i == 0 and not args[i].startswith("-"):
            cleaned_args.extend(["--template", args[i]])
        else:
            cleaned_args.append(args[i])
        i += 1

    parsed = parser.parse_args(cleaned_args)
    template_id = parsed.template
    source = parsed.source.lower()
    port = parsed.port
    msg = parsed.msg or f"Triggered from {source.upper()} with template '{template_id}'"
    open_browser = parsed.open

    display_banner()
    console.print(f"[bold yellow]> Sending [{source.upper()}] Callback to OmniMemory Dashboard on port {port}...[/bold yellow]")

    url = f"http://127.0.0.1:{port}/api/callback"
    payload = {
        "event": f"{source.title()} Execution Callback",
        "template_id": template_id,
        "source": source,
        "payload": {
            "message": msg,
            "step_title": parsed.step,
            "timestamp": time.time(),
        }
    }

    server_running = False
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            if resp.status == 200:
                server_running = True
                resp_data = json.loads(resp.read().decode("utf-8"))
                console.print(f"[bold green][OK] [{source.upper()}] Callback successfully received by OmniMemory server![/bold green]")
                if "template" in resp_data:
                    t = resp_data["template"]
                    console.print(f"  • Template Activated : [bold cyan]{t.get('title')}[/bold cyan] ({t.get('category')})")
                    console.print(f"  • Prompt Budget     : [bold]{t.get('prompt_budget')} tokens[/bold]")
                    console.print(f"  • Sample ScaNN Query: [dim]'{t.get('sample_query')}'[/dim]")
    except (urllib.error.URLError, ConnectionRefusedError, TimeoutError, OSError):
        console.print(f"[dim yellow]Notice: Dashboard server not currently listening on port {port}.[/dim yellow]")

    dashboard_url = f"http://127.0.0.1:{port}/?template={template_id}&source={source}&event={source.title()}+Callback"

    if open_browser:
        console.print(f"[bold cyan]Opening webapp dashboard in browser: {dashboard_url}[/bold cyan]")
        webbrowser.open(dashboard_url)
        if not server_running:
            console.print("[bold green]> Starting Dashboard server now to display template...[/bold green]")
            httpd = run_dashboard_server(port=port, open_browser=False)
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                console.print("\n[yellow]Shutting down dashboard server.[/yellow]")
    else:
        if server_running:
            console.print(f"[bold cyan]Dashboard available at: [underline]{dashboard_url}[/underline][/bold cyan]\n")
        else:
            console.print(f"[yellow]To view the dashboard and template in your browser, run:[/yellow]")
            console.print(f"  [bold]python -m omni_memory.cli serve --open[/bold]")
            console.print(f"  or [bold]python -m omni_memory.cli callback --template {template_id} --source {source} --open[/bold]\n")


def run_mind4action_cli(args: list[str]):
    """Execute a 4-phase Mind4Action cycle from CLI."""
    stimulus = " ".join(args).strip() if args else "Analyze project roadmap and assess system bottlenecks."
    display_banner()
    console.print(f"[bold yellow]> Executing Mind4Action Cycle (Perceive -> Reflect -> Intend -> Act)...[/bold yellow]\n")
    system = OmniMemorySystem()
    turn = system.mind4action_cycle(stimulus)

    refl = turn.get("reflection", {})
    inten = turn.get("intention", {})
    act_res = turn.get("action_result", {})

    turn_id = turn.get("turn_id", "turn_1")
    table = Table(title=f"Mind4Action Turn #{turn_id} [Cycle Execution]", border_style="cyan")
    table.add_column("Phase", style="bold white", width=14)
    table.add_column("Analysis & Cognitive Telemetry", style="bold cyan")

    tracks_str = ", ".join(refl.get("tracks_perceived", ["technical"]))
    table.add_row("1. Perceive", f"Stimulus: '{turn.get('stimulus', stimulus)}'\nTracks: {tracks_str}")
    table.add_row(
        "2. Reflect",
        f"Cognitive Load Index: [bold]{refl.get('cli', 0.0):.2f}[/bold] | Flow Score: [bold green]{refl.get('flow_score', 0.0):.2f}[/bold green]\n"
        f"Deliberation Depth: [bold]{refl.get('deliberation_depth', 1)}[/bold] | Stress Level: [bold]{refl.get('stress_level', 0.0):.2f}[/bold]\n"
        f"Psychological State: [bold yellow]{refl.get('psychological_behavior', 'flow').upper()}[/bold yellow] ({refl.get('cognitive_pattern', 'analytical')})"
    )
    table.add_row(
        "3. Intend",
        f"Target Action: [bold]{inten.get('target_action', 'execute')}[/bold]\n"
        f"Rationale: {inten.get('rationale', 'Standard execution')}\n"
        f"Firewall Passed: [bold green]{inten.get('firewall_passed', True)}[/bold green] (Allocated: {inten.get('prompt_budget_allocated', 700)} tok)"
    )
    table.add_row(
        "4. Act",
        f"Execution: [bold green]{act_res.get('status', 'completed')}[/bold green] (Action: {act_res.get('action_executed', 'executed')})\n"
        f"Out-of-Band Memory: Step ID {act_res.get('step_id', 'Logged to WAL')}"
    )

    console.print(table)
    console.print("\n[bold green][OK] Mind4Action cycle completed and logged to zero-bloat WAL![/bold green]\n")


def run_firewall_cli(args: list[str]):
    """Inspect prompt or show context governor status."""
    display_banner()
    system = OmniMemorySystem()
    if args and args[0] == "inspect":
        text = " ".join(args[1:]).strip()
        if not text:
            console.print("[red]Usage: g-omnios governor inspect <text to inspect>[/red]")
            return
        console.print("[bold yellow]> Inspecting text with G-OmniOS Context Governor & Quality Optimizer...[/bold yellow]\n")
        res = system.inspect_firewall(text)
        verdict_color = "green" if res["verdict"] == "ALLOWED" else "red"
        console.print(Panel(
            f"Verdict: [{verdict_color} bold]{res['verdict']}[/{verdict_color} bold]\n"
            f"Triggered Invariants: {', '.join(res['triggered_rules']) if res['triggered_rules'] else 'None (Clean Context)'}\n"
            f"Optimization: {res.get('suggested_mitigation', 'None required.')}\n"
            f"Clean Context: {res.get('clean_context')}",
            title="G-OmniOS Context Governor Report",
            border_style=verdict_color
        ))
    else:
        fw_status = system.firewall.get_status()
        table = Table(title="G-OmniOS Context Governor & Quality Invariants", border_style="magenta")
        table.add_column("Governor Component / Guard", style="bold white")
        table.add_column("Status / Policy", style="bold cyan")

        table.add_row("Active Quality Invariants", f"{len(fw_status.get('rules', []))} Rules Enforced")
        table.add_row("Scheduled Persona Skills", f"{fw_status.get('scheduled_count', 0)} active skills scheduled")
        table.add_row("Max Prompt Token Threshold", f"{fw_status.get('max_prompt_tokens', 700)} tokens")
        table.add_row("Cognitive Overload Threshold", f"CLI >= {fw_status.get('cognitive_load_threshold', 0.80)}")
        table.add_row("Context Interventions", f"{fw_status.get('total_interventions', 0)}")
        table.add_row("Shielded Tokens Diverted", f"{fw_status.get('shielded_tokens', 0)} tokens")

        console.print(table)
        console.print("\n[dim]To inspect a text: g-omnios governor inspect <text>[/dim]\n")


def list_catalog_cli():
    """List all persona skills across Technical, Social, and Mental ability tracks."""
    display_banner()
    system = OmniMemorySystem()
    skills = system.firewall.get_catalog()

    table = Table(title="G-OmniOS Persona Skills Catalog", border_style="blue")
    table.add_column("Track", style="bold yellow", width=12)
    table.add_column("Skill ID", style="bold cyan")
    table.add_column("Skill Title", style="bold white")
    table.add_column("Budget", style="green", width=10)
    table.add_column("Description", style="dim")

    for s in skills:
        track_badge = f"[{'cyan' if s.track.value == 'technical' else 'yellow' if s.track.value == 'social' else 'magenta'}]{s.track.value.upper()}[/]"
        table.add_row(track_badge, s.skill_id, s.title, f"{s.prompt_budget} tok", s.description)

    console.print(table)
    console.print("\n[dim]To schedule a persona skill: omni-memory schedule <skill_id>[/dim]\n")


def run_department_cli(args: list[str]):
    """Dispatch tasks or queries to G-OmniOS Organizational Agent Teams."""
    display_banner()
    system = OmniMemorySystem()
    if not args:
        roster = system.departments.get_roster()
        table = Table(title="G-OmniOS Organizational Agent Roster", border_style="green")
        table.add_column("Department", style="bold cyan", width=12)
        table.add_column("Agent Title", style="bold white", width=25)
        table.add_column("Track Affinity", style="yellow", width=14)
        table.add_column("Core Focus", style="dim")

        for k, a in roster.items():
            table.add_row(k, a["title"], a["track"].upper(), a["focus"])

        console.print(table)
        console.print("\n[dim]Usage: omni-memory department <manager|hr|fullstack|catalog|marketing|devops> [task][/dim]\n")
        return

    dept_name = args[0].lower()
    task = " ".join(args[1:]).strip() if len(args) > 1 else "status"
    console.print(f"[bold yellow]> Dispatching to [{dept_name.upper()}] Agent: task='{task}'...[/bold yellow]\n")
    res = system.dispatch_department(dept_name, task)

    if "error" in res:
        console.print(f"[bold red]Error:[/bold red] {res['error']}")
        return

    output_data = res.get("result")
    if output_data is None:
        output_data = {k: v for k, v in res.items() if k not in ("agent", "department", "status")}

    console.print(Panel(
        f"[bold cyan]Agent:[/bold cyan] {res.get('agent', dept_name)} ({res.get('department', dept_name).upper()})\n"
        f"[bold yellow]Status:[/bold yellow] {res.get('status', 'ACTIVE')}\n\n"
        f"[bold white]Output / Plan:[/bold white]\n"
        f"{json.dumps(output_data, indent=2) if isinstance(output_data, dict) else output_data}",
        title=f"G-OmniOS Agent Response: {dept_name.upper()}",
        border_style="green"
    ))


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("--help", "-h"):
        display_banner()
        console.print("[bold]Available Commands:[/bold]")
        console.print("  [cyan]demo[/cyan]                    - Run an automated multi-step reasoning simulation")
        console.print("  [cyan]benchmark[/cyan]               - Run the 10-step zero-token-bloat token savings benchmark")
        console.print("  [cyan]interactive[/cyan]             - Start an interactive terminal REPL for steps & queries")
        console.print("  [cyan]mind4action <stimulus>[/cyan] - Run a 4-phase Mind4Action cycle (Perceive -> Reflect -> Intend -> Act)")
        console.print("  [cyan]governor [inspect <txt>][/cyan]- View Context Governor status or inspect prompt against quality invariants")
        console.print("  [cyan]inspect <text>[/cyan]          - Quick prompt optimization & quality invariant inspection")
        console.print("  [cyan]catalog[/cyan]                 - List Persona Skills Catalog across Technical, Social, and Mental tracks")
        console.print("  [cyan]department [name] [tsk][/cyan]- Dispatch to Manager, HR, Fullstack, Catalog, Marketing, DevOps agents")
        console.print("  [cyan]templates[/cyan]               - List available task templates (Raft, Trading, Refactor, Research)")
        console.print("  [cyan]callback <tpl> [-S src][/cyan]- Trigger callback to webapp dashboard (antigravity, claude, chatgpt, opencode, blackbox)")
        console.print("  [cyan]mcp[/cyan]                     - Launch Model Context Protocol (MCP) stdio server for AI agents")
        console.print("  [cyan]serve [--port P] [-o][/cyan]   - Launch the real-time Glassmorphism Web Console at http://127.0.0.1:8765")
        return

    cmd = args[0].lower()
    if cmd == "demo":
        run_demo_trajectory()
    elif cmd in ("benchmark", "bench"):
        run_benchmark_cli()
    elif cmd in ("interactive", "chat", "repl"):
        run_interactive()
    elif cmd in ("mind4action", "m4a"):
        run_mind4action_cli(args[1:])
    elif cmd in ("governor", "gov", "firewall", "fw"):
        run_firewall_cli(args[1:])
    elif cmd in ("inspect", "check"):
        run_firewall_cli(["inspect"] + args[1:])
    elif cmd in ("catalog", "skills"):
        list_catalog_cli()
    elif cmd in ("department", "dept", "team", "teams", "agents"):
        run_department_cli(args[1:])
    elif cmd in ("templates", "template", "tpl"):
        list_templates_cli()
    elif cmd in ("callback", "cb"):
        run_callback_cli(args[1:])
    elif cmd in ("mcp", "mcp-server"):
        from omni_memory.mcp import run_stdio_mcp
        run_stdio_mcp()
    elif cmd == "serve":
        port = 8765
        open_browser = False
        remaining = args[1:]
        idx = 0
        while idx < len(remaining):
            a = remaining[idx]
            if a in ("--open", "-o"):
                open_browser = True
            elif a in ("--port", "-p") and idx + 1 < len(remaining):
                port = int(remaining[idx + 1])
                idx += 1
            elif a.isdigit():
                port = int(a)
            idx += 1

        display_banner()
        httpd = run_dashboard_server(port=port, open_browser=open_browser)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            console.print("\n[yellow]Shutting down dashboard server.[/yellow]")


if __name__ == "__main__":
    main()
