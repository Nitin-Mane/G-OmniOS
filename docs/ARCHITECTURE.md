# G-OmniOS Architecture & System Specification

This document details the architectural principles, subsystems, invariant pipelines, and data flows powering **G-OmniOS**.

---

## 🏛️ System Overview

G-OmniOS serves as an out-of-band **Cognitive Operating System** and **Memory Firewall Hub** positioned between client interfaces (IDE extensions, agent frameworks, CLI) and underlying Large Language Models (LLMs).

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

---

## 🔄 Mind4Action 4-Phase Cognitive Cycle

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

---

## 👥 Organizational Agent Hierarchy & Governance

G-OmniOS deploys six specialized organizational agent teams communicating asynchronously through a shared memory core:

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

---

## 🛡️ Memory Firewall Invariant Flow

The Memory Firewall Hub evaluates every prompt, step, and context update against strict invariants before allowing token allocation into LLM working memory:

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

---

## 📊 Token Economics & Context Invariant

In standard unbuffered LLM agent architectures, intermediate chain-of-thought, compiler errors, raw database responses, and API logs accumulate linearly:

$$\text{Tokens}_{\text{Standard}}(N) = \text{BasePrompt} + \sum_{i=1}^{N} \text{StepTokens}_i$$

Under **G-OmniOS**, intermediate steps are routed directly to the LevelDB WAL, leaving the working context bounded:

$$\text{Tokens}_{\text{G-OmniOS}}(N) = \text{BasePrompt} + \Delta_{\text{MyersRevision}} + \text{TopK}_{\text{ScaNN}} \le \text{Budget}_{\text{Max}} \quad (\approx 800\text{ tokens})$$

This delivers consistent **70%–90%+ token cost reductions** and completely prevents long-horizon context degradation.
