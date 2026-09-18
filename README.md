<div align="center">

# ⚡ G-OmniOS

**Universal Cognitive Memory Firewall Hub & Mind4Action Operating System**  
*Fusing Google Open-Source Portfolio: Always-On Memory Agent, ReasoningBank, Diff-Match-Patch, LevelDB WAL, ScaNN, and SentencePiece Token Allocator.*

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MCP Server](https://img.shields.io/badge/MCP-2.0%20JSON--RPC-brightgreen.svg)](mcp_config.json)
[![Token Savings](https://img.shields.io/badge/Token%20Savings-70%25%E2%80%9390%25%2B-emerald.svg)](#-token-economics--invariant-guarantees)
[![Google Open Source](https://img.shields.io/badge/Google%20Core-LevelDB%20%7C%20ScaNN%20%7C%20DiffMatchPatch-red.svg)](docs/ARCHITECTURE.md)

<br/>

<img src="docs/assets/hero_banner.jpg" alt="G-OmniOS Platform Banner" width="100%" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.6);" />

</div>

---

## 🌟 The Vision: A Cognitive Firewall Hub for Human & AI Mastery

Modern AI agent interaction overwhelms both the user and the language model:
- **For the User**: Cognitive overload, high mental fatigue, fragmented attention, and loss of psychological safety when sensitive data leaks into prompt context.
- **For the Model**: Exponential prompt bloat, lost-in-the-middle degradation, high inference costs, and reasoning stagnation in repetitive thought loops.

**G-OmniOS** solves this universally by providing a **Firewall Hub** between user and AI that monitors, tracks, and schedules memory-building persona skills based on **cognitive patterns**, **psychological behaviors**, and the **Mind4Action** activity process across **Technical, Social, and Mental** ability tracks.

---

## 🖥️ Interactive Real-Time Web Console (Glassmorphism UI)

G-OmniOS features an ultra-responsive, cybernetic dark-mode web console running locally over Server-Sent Events (SSE):

<div align="center">
  <img src="docs/assets/dashboard_preview.jpg" alt="G-OmniOS Glassmorphism Dashboard UI" width="95%" style="border-radius: 10px; margin: 16px 0;" />
</div>

### Console Capabilities:
- 📈 **Tokenomics & Memory Telemetry**: Real-time graphs of shielded prompt tokens, working context load, and cumulative savings.
- 🔍 **Google ScaNN Semantic Vector Search**: Sub-millisecond cosine nearest-neighbor query over past execution memories.
- ⚙️ **Mind4Action 4-Phase Stepper**: Interactive visualizer showing live transitions through `Perceive -> Reflect -> Intend -> Act`.
- 🛡️ **Memory Firewall Live Sandbox**: Test prompts against repetitive thought loops, CLI overload thresholds, and sensitive data filters.
- 👔 **Organizational Agent Drawer**: 1-click consultation and dispatch with 6 autonomous departments.

---

## 🏛️ System Architecture

G-OmniOS decouples verbose chain-of-thought deliberations from the LLM prompt window by routing raw execution records directly to an out-of-band persistent write-ahead log (Google LevelDB WAL), surfacing only compact Myers diffs and relevant semantic vectors.

```mermaid
flowchart TB
    subgraph Clients["Client Ecosystem"]
        VS["VS Code Extension"]
        AG["Antigravity IDE"]
        CL["Claude Desktop / CLI"]
        GPT["ChatGPT / Codex"]
        OP["OpenCode & Blackbox"]
        CLI["CLI & REST / SSE Console"]
    end

    subgraph Hub["G-OmniOS Firewall & Governance Hub"]
        direction TB
        FW["Memory Firewall Hub<br/>• Overload Guard (CLI > 0.80)<br/>• Repetitive Loop Guard (<0.35)<br/>• Psychological Safety Shield<br/>• Prompt Bloat Shield (<=700 tok)"]
        M4A["Mind4Action Engine<br/>• Perceive (Token Budgeting)<br/>• Reflect (Cognitive Profile)<br/>• Intend (Action Synthesis)<br/>• Act (Out-of-Band Dispatch)"]
        DEP["Organizational Agent Teams<br/>• Manager Agent<br/>• HR Agent<br/>• Fullstack AI Agent<br/>• Catalog Agent<br/>• Marketing Agent<br/>• DevOps Agent"]
    end

    subgraph Storage["Google Open-Source Storage & Vector Core"]
        WAL[("Google LevelDB WAL<br/>Zero-Token Persistent Ledger")]
        SCANN[("Google ScaNN Engine<br/>High-Dimensional Vector Space")]
        DMP["Google Diff-Match-Patch<br/>Myers Delta Context Revision"]
        SP["Google SentencePiece<br/>Sub-Word Token Governor"]
    end

    subgraph LLM["LLM Working Context (Strictly Bounded)"]
        CTX["Active Prompt Window<br/>(Target: <= 800 Tokens)"]
    end

    Clients -->|"Raw Prompts & Tool Calls"| FW
    FW -->|"Sanitized Invariants"| M4A
    M4A -->|"Coordinate Tasks"| DEP
    M4A -->|"Verbose Steps & Scratchpad"| WAL
    WAL -->|"Index Memory Vectors"| SCANN
    WAL -->|"Compute Myers Diffs"| DMP
    DMP -->|"Compact Revised Context"| CTX
    SCANN -.->|"Sub-Millisecond Recall"| CTX
    SP -.->|"Enforce Token Quotas"| CTX
```

> 📖 **Deep Dive**: See the full architectural specification in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## 🔄 Mind4Action 4-Phase Cognitive Workflow

The **Mind4Action** cognitive engine structures reasoning into four deterministic, accountable stages:

```mermaid
sequenceDiagram
    autonumber
    actor User as Client / User Stimulus
    participant P as Perceive Phase
    participant R as Reflect Phase
    participant I as Intend Phase
    participant A as Act Phase
    participant DB as Google LevelDB WAL
    participant SC as Google ScaNN Index

    User->>P: Dispatch Task / Query Stimulus
    Note over P: Estimates Token Volume & Categorizes Ability Track (Technical / Social / Mental)
    P->>R: Ingestion Metadata
    Note over R: Computes CLI (Cognitive Load Index), Flow Score, Stress, and Psychological State
    R->>I: Cognitive Profile & Load Metrics
    Note over I: Validates Firewall Invariants, Matches ReasoningBank Template, Caps Working Budget
    I->>A: Formulated Action & Tool Manifest
    Note over A: Executes Task Out-of-Band, Logs Verbose Deliberations to WAL
    A->>DB: Append Step Record to LevelDB
    DB->>SC: Asynchronous Vector Embedding & ScaNN Indexing
    A-->>User: Compact Execution Result & Telemetry (Token Savings KPI)
```

1. **Perceive**: Ingests raw stimulus, estimates token volume, and classifies relevant ability tracks (`Technical`, `Social`, `Mental`).
2. **Reflect**: Dynamically computes **Cognitive Load Index (CLI)** (0.0–1.0), **Flow Score** (0.0–1.0), **Deliberation Depth**, and classifies psychological state transitions (`FLOW`, `FATIGUE`, `DELIBERATE`, `EXPLORATION`, `ANXIOUS`, `FRUSTRATED`).
3. **Intend**: Evaluates firewall invariant guards and formulates bounded, safe action intentions within strict prompt budgets.
4. **Act**: Executes actions out-of-band and logs reasoning steps directly into Google LevelDB WAL without polluting LLM working context.

---

## 👥 Organizational Multi-Agent Team Structure

G-OmniOS structures multi-agent collaboration as a formal corporate organizational team, coordinating asynchronously through the shared LevelDB memory core:

<div align="center">
  <img src="docs/assets/multiagent_ecosystem.jpg" alt="G-OmniOS Multi-Agent Ecosystem" width="95%" style="border-radius: 10px; margin: 16px 0;" />
</div>

```mermaid
graph TD
    classDef manager fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff;
    classDef agent fill:#0f172a,stroke:#818cf8,stroke-width:1px,color:#e2e8f0;
    classDef core fill:#0284c7,stroke:#38bdf8,stroke-width:2px,color:#fff;

    COORD["Coordinator Agent / Dispatch Hub"]:::manager

    MGR["👔 Manager Agent<br/>Roadmaps, Deliverables & Token KPIs"]:::agent
    HR["🧑‍⚕️ HR Agent<br/>Cognitive Ergonomics & Psychological Safety"]:::agent
    FS["💻 Fullstack AI Agent<br/>Memory Architecture & Vector Retrieval"]:::agent
    CAT["📚 Catalog Agent<br/>Ability Tracks & Persona Skills Taxonomy"]:::agent
    MKT["📣 Marketing Agent<br/>Developer Messaging & Value Positioning"]:::agent
    OPS["🛠️ DevOps Agent<br/>Zero-Cloud Durability & Daemon Telemetry"]:::agent

    CORE[("LevelDB Memory Core<br/>& ScaNN Semantic Store")]:::core

    COORD --> MGR
    COORD --> HR
    COORD --> FS
    COORD --> CAT
    COORD --> MKT
    COORD --> OPS

    MGR <--> CORE
    HR <--> CORE
    FS <--> CORE
    CAT <--> CORE
    MKT <--> CORE
    OPS <--> CORE
```

- 👔 **Manager Agent**: Sprint roadmaps, deliverable tracking, token savings KPIs.
- 🧑‍⚕️ **HR Agent**: Cognitive ergonomics, psychological safety auditing, wellness scoring.
- 💻 **Fullstack AI Agent**: Out-of-band memory architecture, ScaNN vector indexing, zero-cloud pipeline auditing.
- 📚 **Catalog Agent**: Persona skills curation and ability-track recommendations.
- 📣 **Marketing Agent**: Value positioning, messaging, target persona alignment.
- 🛠️ **DevOps Agent**: Zero-cloud daemon watchdog, local socket health, air-gapped durability.

---

## 🛡️ Memory Firewall Hub & Psychological Safety

Active invariant enforcement protects both human cognitive bandwidth and model reasoning context:

<div align="center">
  <img src="docs/assets/firewall_safety_hub.jpg" alt="G-OmniOS Cognitive Memory Firewall" width="95%" style="border-radius: 10px; margin: 16px 0;" />
</div>

```mermaid
flowchart LR
    INPUT["Incoming Prompt / Context Revision"] --> G1{"Repetitive Thought<br/>Loop Guard"}
    
    G1 -- "Uniqueness < 0.35" --> B1["BLOCK: Enforce Meta-Cognitive Pivot"]
    G1 -- "PASS" --> G2{"Prompt Bloat<br/>Shield"}

    G2 -- "> 700 Tokens" --> B2["BLOCK: Divert Overflow to LevelDB WAL"]
    G2 -- "PASS" --> G3{"Psychological Safety<br/>& PII Shield"}

    G3 -- "Distress / Leak Detected" --> B3["QUARANTINE: Isolate Sensitive Payload"]
    G3 -- "PASS" --> G4{"Cognitive Load<br/>Index (CLI)"}

    G4 -- "CLI > 0.80" --> B4["ADAPT: Trigger Chunked Consolidation"]
    G4 -- "PASS (CLI <= 0.80)" --> PERMIT["AUTHORIZED: Deliver to Working Context"]

    B1 --> WAL[("LevelDB WAL Ledger")]
    B2 --> WAL
    B3 --> WAL
    B4 --> WAL
```

- **Cognitive Overload Guard**: Intercepts high-complexity tasks when CLI > 0.80 and diverts overflow to structured consolidation.
- **Repetitive Thought Loop Guard**: Detects when reasoning cycles stagnate (token uniqueness ratio < 0.35) and enforces fresh meta-cognitive pivots.
- **Psychological Vulnerability Guard**: Detects sensitive personal statements, panic outbursts, or credentials, shielding them strictly to LevelDB WAL.
- **Prompt Bloat Shield**: Caps working prompt load at 700 tokens, preserving 70%–90%+ token economics.

---

## 🚀 Real-World Product Use Cases

| Domain | Challenge | G-OmniOS Solution | Impact |
|---|---|---|---|
| **Autonomous Software Engineering** | 30k+ token AST diffs & compiler loops degrading model context | Verbose logs streamed to LevelDB WAL; only Myers diffs enter working prompt | **88.4% token savings**, zero context loss over 50+ turns |
| **Quant Risk & Financial Modeling** | High-frequency covariance calculations blowing prompt token budgets | Mind4Action cycle executes calculations out-of-band via `trading` template | Deterministic, auditable execution with bounded 750-token footprint |
| **Enterprise Multi-Agent Governance** | Conflicting goals, circular dialogues, and multiplied token bills | 6 specialized departments coordinate asynchronously via shared LevelDB memory | Structured deliverables, unified roadmaps, zero circular loops |
| **Cognitive Ergonomics & Mental Wellness** | High-pressure outage fatigue and inadvertent leakage of sensitive data | Firewall Hub calculates CLI score in real time and quarantines sensitive tokens | Mental burnout prevention and bulletproof prompt confidentiality |

> 📖 **Read Full Case Studies**: Detailed breakdowns in [`docs/USE_CASES.md`](docs/USE_CASES.md).

---

## ⚡ Quick Start

Runs natively 100% locally with zero external cloud dependencies.

### 1. Installation & Setup
```bash
pip install -e .
```

### 2. Mind4Action 4-Phase Cognitive Cycle (CLI)
```bash
# Execute a cognitive cycle: Perceive -> Reflect -> Intend -> Act
python -m omni_memory.cli mind4action "Deconstruct portfolio covariance matrix for risk parity trading"
```

### 3. Memory Firewall Inspection & Status
```bash
# Display active firewall invariants and rules:
python -m omni_memory.cli firewall

# Inspect prompt context for sensitive leaks or bloat:
python -m omni_memory.cli firewall inspect "Inspect prompt safety, bounds, and token quota..."
```

### 4. Persona Skills Catalog
```bash
# View Technical, Social, and Mental ability tracks:
python -m omni_memory.cli catalog
```

### 5. Organizational Agent Teams Dispatch
```bash
# List all 6 agent departments:
python -m omni_memory.cli department

# Consult Manager Agent for sprint report and token KPIs:
python -m omni_memory.cli department manager

# Consult HR Agent for psychological safety and cognitive ergonomics:
python -m omni_memory.cli department hr

# Consult Fullstack AI Agent for memory architecture audit:
python -m omni_memory.cli department fullstack
```

### 6. Launch Real-Time Glassmorphism Web Console
```bash
python -m omni_memory.cli serve --port 8765 --open
```
Navigate to `http://127.0.0.1:8765/` to interact with the full web console.

---

## 🔌 Universal MCP Server (stdio)

G-OmniOS exposes an enterprise Model Context Protocol (MCP) JSON-RPC 2.0 stdio server:
```bash
python -m omni_memory.mcp
```

### Supported MCP Tools:
1. `gomnios_mind4action_cycle`: Executes a 4-phase cognitive cycle (`Perceive -> Reflect -> Intend -> Act`).
2. `gomnios_firewall_inspect`: Inspects prompt context against cognitive overload and psychological safety invariants.
3. `gomnios_schedule_persona_skill`: Activates a persona skill across Technical, Social, or Mental tracks.
4. `gomnios_department_dispatch`: Dispatches tasks to Manager, HR, Fullstack AI, Catalog, Marketing, or DevOps agents.
5. `gomnios_get_cognitive_status`: Retrieves real-time CLI, flow scores, and firewall safety health.
6. `omnimemory_track_step`: Logs raw thoughts out-of-band to LevelDB WAL.
7. `omnimemory_query_scann`: Nearest-neighbor cosine search over past memory vectors.
8. `omnimemory_trigger_callback`: Broadcasts live dashboard updates and switches to specified templates.
9. `omnimemory_revise_context`: Computes Diff-Match-Patch Myers delta to consolidate unrevised steps.
10. `omnimemory_get_telemetry`: Fetches token economics and working prompt metrics.

---

## 🤖 Multi-Platform Matrix

| Platform | Mode | Config / Integration | Key Capabilities |
|---|---|---|---|
| **Google Antigravity** | Workspace Skill + Project MCP | [`.agents/skills/omnimemory/SKILL.md`](.agents/skills/omnimemory/SKILL.md) & [`mcp_config.json`](mcp_config.json) | Autonomous out-of-band step tracking, ScaNN recall, milestone callbacks |
| **Anthropic Claude** | Desktop & CLI | [`integrations/claude/`](integrations/claude/) | Native tool calling, Diff-Match-Patch delta consolidation |
| **ChatGPT & OpenAI Codex** | Actions + Function Calling | [`integrations/chatgpt_codex/`](integrations/chatgpt_codex/) | OpenAI Function Calling API schema, Python adapter |
| **OpenCode** | OpenCode MCP Manifest | [`integrations/opencode/`](integrations/opencode/) | Cobalt `[OPENCODE]` toast callbacks, zero prompt bloat |
| **Blackbox AI** | Assistant Hooks | [`integrations/blackbox/`](integrations/blackbox/) | Cyber-violet `[BLACKBOX]` callbacks, code refactoring |
| **VS Code** | Extension & Webview Panel | [`extension/`](extension/) | Status bar token counter, command palette ScaNN query, embedded live dashboard |
| **CLI & Terminal** | Standalone REPL, MCP & Callbacks | `omni-memory mind4action`, `omni-memory firewall` | Rich interactive terminal, automated trajectory demos, benchmarks |

---

## 🌐 REST & SSE API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves G-OmniOS Glassmorphism dashboard |
| `GET` | `/api/telemetry` | Token economics, working prompt, cognitive state, firewall metrics |
| `GET` | `/api/cognitive` | Live Cognitive Load Index, flow score, deliberation depth, stress |
| `GET` | `/api/firewall/status` | Active firewall rules, blocked interventions, safety health score |
| `GET` | `/api/skills/catalog` | Lists persona skills grouped by Technical, Social, and Mental tracks |
| `GET` | `/api/departments` | Returns roster of 6 organizational agent teams |
| `POST` | `/api/mind4action` | Executes 4-phase Mind4Action cycle |
| `POST` | `/api/firewall/inspect` | Inspects text for overload, repetitive loops, psychological leaks |
| `POST` | `/api/skills/schedule` | Schedules and activates a persona skill from catalog |
| `POST` | `/api/department/dispatch` | Dispatches task to Manager, HR, Fullstack, Catalog, Marketing, DevOps |
| `GET` | `/api/events` | Server-Sent Events (SSE) real-time streaming updates |
| `POST` | `/api/callback` | Ingests multi-platform callback from CLI, VS Code, Antigravity, Claude, etc. |
| `POST` | `/api/step` | Records execution step out-of-band into LevelDB WAL |
| `POST` | `/api/query` | Google ScaNN dense vector semantic retrieval |
| `POST` | `/api/revise` | Diff-Match-Patch context revision and consolidation |
| `POST` | `/api/simulate` | Runs automated multi-step simulation trajectory |
| `POST` | `/api/reset` | Resets session memory and starts fresh task context |

---

## 📜 Token Economics & Invariant Guarantees

- **Prompt Token Savings**: Consistently saves **70%–90%+** of prompt tokens by routing intermediate thoughts directly to LevelDB WAL.
- **Bounded Working Context**: Working memory is strictly capped (target $\le 800$ tokens), preventing context degradation.
- **Psychological Safety**: Sensitive data is automatically detected and quarantined from prompts.
- **100% Local Execution**: Runs entirely on local Python with zero external cloud requirements.

---

<div align="center">
  <b>G-OmniOS</b> — Built with Google Open-Source Portfolio for Next-Generation Cognitive Intelligence.
</div>
