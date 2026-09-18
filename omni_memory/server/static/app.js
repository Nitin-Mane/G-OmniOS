/**
 * G-OmniOS | Cognitive Memory Firewall Hub & Mind4Action Client Logic
 * Real-time event subscription via Server-Sent Events (SSE) + REST updates.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements - Memory & Economics
  const elSavedTokens = document.getElementById("savedTokens");
  const elSavedPct = document.getElementById("savedPct");
  const elSavingsProgress = document.getElementById("savingsProgress");
  const elRawTokens = document.getElementById("rawTokens");
  const elActivePromptTokens = document.getElementById("activePromptTokens");
  const elPromptBudget = document.getElementById("promptBudget");

  const elWorkingTokens = document.getElementById("workingTokens");
  const elEpisodicCount = document.getElementById("episodicCount");
  const elScannCount = document.getElementById("scannCount");

  const elStepStream = document.getElementById("stepStream");
  const elStepCounter = document.getElementById("stepCounter");
  const elCanonicalContextView = document.getElementById("canonicalContextView");
  const elActivePromptView = document.getElementById("activePromptView");
  const elPromptTokenBadge = document.getElementById("promptTokenBadge");
  const elRevisionsList = document.getElementById("revisionsList");

  // Cognitive Strip Elements
  const elCliBar = document.getElementById("cliBar");
  const elCliVal = document.getElementById("cliVal");
  const elFlowBar = document.getElementById("flowBar");
  const elFlowVal = document.getElementById("flowVal");
  const elPsyStateBadge = document.getElementById("psyStateBadge");
  const elCogPatternBadge = document.getElementById("cogPatternBadge");
  const elDelibDepthVal = document.getElementById("delibDepthVal");
  const elActiveSkillBadge = document.getElementById("activeSkillBadge");
  const elSafetyScoreVal = document.getElementById("safetyScoreVal");

  // Callback & Toast Elements
  const elCallbackToast = document.getElementById("callbackToast");
  const elCallbackSourceBadge = document.getElementById("callbackSourceBadge");
  const elCallbackEventTitle = document.getElementById("callbackEventTitle");
  const elCallbackEventDetails = document.getElementById("callbackEventDetails");
  const elBtnCloseCallbackToast = document.getElementById("btnCloseCallbackToast");

  // Template Elements
  const elTemplateTabBar = document.getElementById("templateTabBar");
  const elTemplateTitle = document.getElementById("templateTitle");
  const elTemplateCategory = document.getElementById("templateCategory");
  const elTemplateDesc = document.getElementById("templateDesc");
  const elTemplateBudget = document.getElementById("templateBudget");
  const elTemplateQuery = document.getElementById("templateQuery");
  const elTemplatePromptText = document.getElementById("templatePromptText");
  const btnLoadTemplate = document.getElementById("btnLoadTemplate");
  const btnTestTemplateSearch = document.getElementById("btnTestTemplateSearch");

  // Actions
  const btnSimulate = document.getElementById("btnSimulate");
  const btnQuickM4A = document.getElementById("btnQuickM4A");
  const btnRevise = document.getElementById("btnRevise");
  const btnReset = document.getElementById("btnReset");
  const btnAddStep = document.getElementById("btnAddStep");
  const stepTitleInput = document.getElementById("stepTitleInput");
  const stepPhaseSelect = document.getElementById("stepPhaseSelect");

  const scannQueryInput = document.getElementById("scannQueryInput");
  const btnScannSearch = document.getElementById("btnScannSearch");
  const scannResultsContainer = document.getElementById("scannResults");

  // Mind4Action Elements
  const m4aStimulusInput = document.getElementById("m4aStimulusInput");
  const btnExecuteM4A = document.getElementById("btnExecuteM4A");
  const perceiveMeta = document.getElementById("perceiveMeta");
  const m4aCli = document.getElementById("m4aCli");
  const m4aFlow = document.getElementById("m4aFlow");
  const m4aPsy = document.getElementById("m4aPsy");
  const m4aTargetAction = document.getElementById("m4aTargetAction");
  const m4aFirewallPassed = document.getElementById("m4aFirewallPassed");
  const m4aActStatus = document.getElementById("m4aActStatus");
  const m4aWalKey = document.getElementById("m4aWalKey");
  const m4aTurnsContainer = document.getElementById("m4aTurnsContainer");

  // Firewall Elements
  const firewallTestInput = document.getElementById("firewallTestInput");
  const btnInspectFirewall = document.getElementById("btnInspectFirewall");
  const firewallVerdictResult = document.getElementById("firewallVerdictResult");
  const btnPresetOverload = document.getElementById("btnPresetOverload");
  const btnPresetLeak = document.getElementById("btnPresetLeak");

  // Skills & Departments Elements
  const skillsGridContainer = document.getElementById("skillsGridContainer");
  const departmentsGrid = document.getElementById("departmentsGrid");
  const deptConsultResult = document.getElementById("deptConsultResult");
  const consultDeptBadge = document.getElementById("consultDeptBadge");
  const consultAgentTitle = document.getElementById("consultAgentTitle");
  const consultOutputView = document.getElementById("consultOutputView");
  const btnCloseConsult = document.getElementById("btnCloseConsult");

  let renderedStepIds = new Set();
  let renderedRevisionIds = new Set();
  let availableTemplates = [];
  let currentTemplateId = "raft";
  let cachedSkills = [];
  let currentTrackFilter = "all";
  let toastTimer = null;

  // VS Code Webview messaging integration
  const vscode = typeof acquireVsCodeApi === "function" ? acquireVsCodeApi() : null;

  // Initialize
  initTabs();
  initMind4Action();
  initFirewall();
  initSSE();
  fetchTelemetry();
  loadTemplates();
  loadPersonaSkills();
  loadDepartments();
  checkUrlParameters();

  // Navigation Tabs Switching
  function initTabs() {
    const navTabs = document.querySelectorAll(".nav-tab");
    navTabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        const targetId = tab.getAttribute("data-tab");
        switchTab(targetId);
      });
    });
  }

  function switchTab(targetId) {
    document.querySelectorAll(".nav-tab").forEach((t) => {
      t.classList.toggle("active", t.getAttribute("data-tab") === targetId);
    });
    document.querySelectorAll(".tab-pane").forEach((p) => {
      p.classList.toggle("active", p.id === targetId);
    });
  }

  // SSE event listener
  function initSSE() {
    try {
      const eventSource = new EventSource("/api/events");

      eventSource.addEventListener("initial_state", (e) => {
        const data = JSON.parse(e.data);
        renderTelemetry(data);
      });

      eventSource.addEventListener("step_added", (e) => {
        const data = JSON.parse(e.data);
        if (data.report) renderReport(data.report);
        if (data.step) appendStepCard(data.step);
      });

      eventSource.addEventListener("context_revised", (e) => {
        const data = JSON.parse(e.data);
        if (data.report) renderReport(data.report);
        if (data.revision) appendRevisionCard(data.revision);
        fetchTelemetry();
      });

      eventSource.addEventListener("callback_triggered", (e) => {
        const data = JSON.parse(e.data);
        showCallbackToast(data);
        if (data.template_id) {
          selectTemplate(data.template_id);
        }
        fetchTelemetry();
      });

      eventSource.addEventListener("mind4action_turn", (e) => {
        const turn = JSON.parse(e.data);
        renderMind4ActionTurn(turn);
        fetchTelemetry();
      });

      eventSource.addEventListener("skill_scheduled", (e) => {
        const skill = JSON.parse(e.data);
        elActiveSkillBadge.textContent = skill.title || skill.skill_id;
        showCallbackToast({
          source: "firewall",
          event: "Skill Scheduled",
          template_id: skill.skill_id,
          message: `Scheduled persona skill '${skill.title}' across ${skill.track.toUpperCase()} track.`
        });
      });

      eventSource.addEventListener("department_update", (e) => {
        const update = JSON.parse(e.data);
        showCallbackToast({
          source: update.department || "teams",
          event: "Department Response",
          template_id: update.department,
          message: `Agent team [${(update.department || "").toUpperCase()}] finished task '${update.task}'.`
        });
      });

      eventSource.onerror = () => {
        setTimeout(fetchTelemetry, 3500);
      };
    } catch (err) {
      console.warn("SSE connection error, falling back to polling:", err);
      setInterval(fetchTelemetry, 3500);
    }
  }

  async function fetchTelemetry() {
    try {
      const res = await fetch("/api/telemetry");
      if (res.ok) {
        const data = await res.json();
        renderTelemetry(data);
      }
    } catch (err) {
      console.error("Failed to fetch telemetry:", err);
    }
  }

  function renderTelemetry(data) {
    if (!data) return;

    if (data.report) {
      renderReport(data.report);
    }

    if (data.canonical_context) {
      elCanonicalContextView.textContent = data.canonical_context;
    }

    if (data.prompt_window) {
      elActivePromptView.textContent = data.prompt_window.full_prompt;
      elPromptTokenBadge.textContent = `${data.prompt_window.token_count} Tokens`;
    }

    if (data.scann_index_size !== undefined) {
      elScannCount.textContent = data.scann_index_size;
    }

    if (data.step_count !== undefined) {
      elStepCounter.textContent = `${data.step_count} Steps`;
    }

    if (data.recent_steps && Array.isArray(data.recent_steps)) {
      data.recent_steps.forEach((step) => appendStepCard(step));
    }

    if (data.recent_revisions && Array.isArray(data.recent_revisions)) {
      data.recent_revisions.forEach((rev) => appendRevisionCard(rev));
    }

    renderCognitiveTelemetry(data);
  }

  function renderCognitiveTelemetry(data) {
    const cog = data.cognitive_state;
    if (cog) {
      const cli = Number(cog.cognitive_load_index || 0);
      const flow = Number(cog.flow_score || 0);
      const delib = Number(cog.deliberation_depth || 1);

      elCliVal.textContent = cli.toFixed(2);
      elCliBar.style.width = `${Math.min(100, Math.round(cli * 100))}%`;

      elFlowVal.textContent = flow.toFixed(2);
      elFlowBar.style.width = `${Math.min(100, Math.round(flow * 100))}%`;

      const behavior = (cog.active_behavior || "flow").toLowerCase();
      elPsyStateBadge.textContent = behavior.toUpperCase();
      elPsyStateBadge.className = `badge-psy psy-${behavior}`;

      const pattern = (cog.primary_pattern || "analytical").toLowerCase();
      elCogPatternBadge.textContent = pattern.toUpperCase();

      elDelibDepthVal.textContent = `${delib.toFixed(1)} / 5.0`;
    }

    const fw = data.firewall;
    if (fw) {
      if (fw.active_skill && fw.active_skill.title) {
        elActiveSkillBadge.textContent = fw.active_skill.title;
      }
      if (fw.safety_health_score !== undefined) {
        const pct = Math.round(fw.safety_health_score * 100);
        elSafetyScoreVal.textContent = `${fw.safety_health_score.toFixed(2)} (${pct}%)`;
      }
    }
  }

  function renderReport(report) {
    elSavedTokens.textContent = Number(report.tokens_saved || 0).toLocaleString();
    elSavedPct.textContent = `${report.savings_percentage || 0}%`;
    elSavingsProgress.style.width = `${Math.min(100, report.savings_percentage || 0)}%`;

    elRawTokens.textContent = Number(report.total_raw_tokens_generated || 0).toLocaleString();
    elActivePromptTokens.textContent = report.working_tokens || 0;
    elPromptBudget.textContent = report.working_limit || 800;

    elWorkingTokens.textContent = report.working_tokens || 0;
    elEpisodicCount.textContent = report.episodic_count || 0;
  }

  // Mind4Action Engine Implementation
  function initMind4Action() {
    if (btnExecuteM4A) {
      btnExecuteM4A.addEventListener("click", async () => {
        const stimulus = (m4aStimulusInput.value || "").trim();
        if (!stimulus) return;

        btnExecuteM4A.disabled = true;
        btnExecuteM4A.textContent = "Cycling Mind4Action...";

        try {
          const res = await fetch("/api/mind4action", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ stimulus })
          });
          const turn = await res.json();
          renderMind4ActionTurn(turn);
          fetchTelemetry();
        } catch (err) {
          console.error("Mind4Action cycle failed:", err);
        } finally {
          btnExecuteM4A.disabled = false;
          btnExecuteM4A.textContent = "Execute 4-Phase Cycle";
        }
      });
    }

    if (btnQuickM4A) {
      btnQuickM4A.addEventListener("click", () => {
        switchTab("tab-mind4action");
        if (btnExecuteM4A) btnExecuteM4A.click();
      });
    }

    // Presets click handler
    document.querySelectorAll(".btn-preset").forEach((btn) => {
      btn.addEventListener("click", () => {
        const txt = btn.getAttribute("data-text");
        if (txt) {
          m4aStimulusInput.value = txt;
          if (btnExecuteM4A) btnExecuteM4A.click();
        }
      });
    });
  }

  function renderMind4ActionTurn(turn) {
    if (!turn) return;

    const refl = turn.reflection || {};
    const inten = turn.intention || {};
    const act = turn.action_result || {};

    // 1. Perceive
    const tracks = refl.tracks_perceived || ["technical"];
    perceiveMeta.innerHTML = `
      <div>Tracks: ${tracks.map((t) => `<span class="badge-track track-${t.toLowerCase()}">${escapeHtml(t)}</span>`).join(" ")}</div>
      <div class="text-dim">Stimulus length: ${escapeHtml(turn.stimulus).split(" ").length} words</div>
    `;

    // 2. Reflect
    m4aCli.textContent = Number(refl.cli || 0).toFixed(2);
    m4aFlow.textContent = Number(refl.flow_score || 0).toFixed(2);
    const psy = (refl.psychological_behavior || "flow").toLowerCase();
    m4aPsy.textContent = psy.toUpperCase();
    m4aPsy.className = `badge-psy psy-${psy}`;

    // 3. Intend
    m4aTargetAction.textContent = inten.target_action || "deep_deliberation_wal";
    const fwPassed = inten.firewall_passed !== false;
    m4aFirewallPassed.textContent = fwPassed ? "Passed" : "Blocked/Shielded";
    m4aFirewallPassed.className = `badge-status ${fwPassed ? "online" : "offline"}`;

    // 4. Act
    m4aActStatus.textContent = act.status || "completed";
    m4aWalKey.textContent = act.step_id || "step_wal";

    // Append to turns stream
    if (m4aTurnsContainer) {
      const turnCard = document.createElement("div");
      turnCard.className = "m4a-turn-card glass-card";
      turnCard.innerHTML = `
        <div class="m4a-turn-left">
          <div class="m4a-turn-stimulus">#${escapeHtml(turn.turn_id)} • ${escapeHtml(turn.stimulus)}</div>
          <div class="text-dim" style="font-size: 0.74rem; margin-top: 4px;">
            Intention: <strong>${escapeHtml(inten.target_action || "execute")}</strong> • ${escapeHtml(inten.rationale || "")}
          </div>
        </div>
        <div class="m4a-turn-meta">
          <span>CLI: <strong>${Number(refl.cli || 0).toFixed(2)}</strong></span>
          <span>Flow: <strong class="highlight-green">${Number(refl.flow_score || 0).toFixed(2)}</strong></span>
          <span class="badge-psy psy-${psy}">${psy.toUpperCase()}</span>
        </div>
      `;
      m4aTurnsContainer.prepend(turnCard);
    }
  }

  // Firewall Sandbox
  function initFirewall() {
    if (btnInspectFirewall) {
      btnInspectFirewall.addEventListener("click", async () => {
        const text = (firewallTestInput.value || "").trim();
        if (!text) return;

        btnInspectFirewall.disabled = true;
        btnInspectFirewall.textContent = "Inspecting Invariants...";

        try {
          const res = await fetch("/api/firewall/inspect", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
          });
          const inspection = await res.json();
          renderFirewallVerdict(inspection);
        } catch (err) {
          console.error("Firewall inspection error:", err);
        } finally {
          btnInspectFirewall.disabled = false;
          btnInspectFirewall.textContent = "🛡️ Inspect Prompt Context";
        }
      });
    }

    if (btnPresetOverload) {
      btnPresetOverload.addEventListener("click", () => {
        firewallTestInput.value = "Analyze 10,000 lines of legacy monolithic AST code with extreme urgency and multiple conflicting requirements under high fatigue.";
        btnInspectFirewall.click();
      });
    }

    if (btnPresetLeak) {
      btnPresetLeak.addEventListener("click", () => {
        firewallTestInput.value = "I am having a panic attack and severely depressed, my private password is secret_token_xyz";
        btnInspectFirewall.click();
      });
    }
  }

  function renderFirewallVerdict(res) {
    if (!firewallVerdictResult) return;
    firewallVerdictResult.style.display = "flex";

    const isBlocked = res.blocked || res.verdict === "BLOCKED";
    firewallVerdictResult.className = `firewall-verdict-box ${isBlocked ? "verdict-blocked" : "verdict-allowed"}`;

    firewallVerdictResult.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <strong style="font-size: 0.95rem;">VERDICT: ${isBlocked ? "BLOCKED / SHIELDED OUT-OF-BAND" : "ALLOWED / COMPLIANT"}</strong>
        <span class="badge-status ${isBlocked ? "offline" : "online"}">${res.verdict || (isBlocked ? "BLOCKED" : "ALLOWED")}</span>
      </div>
      <div><strong>Reason / Mitigation:</strong> ${escapeHtml(res.reason || res.suggested_mitigation || "Within safe cognitive limits.")}</div>
      ${res.shielded_tokens ? `<div><strong>Shielded Tokens:</strong> ${res.shielded_tokens} tokens diverted to LevelDB WAL</div>` : ""}
      <div><strong>Clean Context:</strong> <code style="color: #fff; font-family: var(--font-mono); font-size: 0.78rem;">${escapeHtml(res.clean_context || "None")}</code></div>
    `;
  }

  // Persona Skills Catalog
  async function loadPersonaSkills() {
    try {
      const res = await fetch("/api/skills/catalog");
      if (res.ok) {
        cachedSkills = await res.json();
        renderSkillsGrid();
      }
    } catch (err) {
      console.error("Failed to load skills catalog:", err);
    }

    // Filter Buttons
    document.querySelectorAll(".catalog-filter-bar .btn-filter").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".catalog-filter-bar .btn-filter").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        currentTrackFilter = btn.getAttribute("data-track") || "all";
        renderSkillsGrid();
      });
    });
  }

  function renderSkillsGrid() {
    if (!skillsGridContainer) return;

    const filtered = cachedSkills.filter((s) => {
      if (currentTrackFilter === "all") return true;
      return (s.track || "").toLowerCase() === currentTrackFilter.toLowerCase();
    });

    if (!filtered.length) {
      skillsGridContainer.innerHTML = `<div class="empty-state"><p>No skills found for track '${currentTrackFilter}'.</p></div>`;
      return;
    }

    skillsGridContainer.innerHTML = filtered.map((skill) => `
      <div class="skill-card glass-card">
        <div class="skill-card-top">
          <div class="skill-header-row">
            <h4 class="skill-title">${escapeHtml(skill.title || skill.name || skill.skill_id)}</h4>
            <div class="skill-badges">
              <span class="badge-track track-${(skill.track || "technical").toLowerCase()}">${escapeHtml(skill.track || "Tech")}</span>
              <span class="badge-level">${escapeHtml(skill.level || "intermediate")}</span>
            </div>
          </div>
          <p class="skill-desc">${escapeHtml(skill.description || "")}</p>
          <div class="skill-tags-row">
            ${(skill.tags || []).map((t) => `<span class="tag-pill">#${escapeHtml(t)}</span>`).join("")}
          </div>
        </div>
        <div class="skill-card-bottom">
          <span class="skill-budget">⚡ ${skill.prompt_budget || 700} tok budget</span>
          <button class="btn btn-primary btn-sm btn-schedule-skill" data-skill-id="${escapeHtml(skill.skill_id)}">
            Schedule & Activate
          </button>
        </div>
      </div>
    `).join("");

    // Wire schedule buttons
    skillsGridContainer.querySelectorAll(".btn-schedule-skill").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const skillId = btn.getAttribute("data-skill-id");
        btn.disabled = true;
        btn.textContent = "Scheduling...";

        try {
          const res = await fetch("/api/skills/schedule", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ skill_id: skillId })
          });
          const scheduled = await res.json();
          if (scheduled && scheduled.title) {
            elActiveSkillBadge.textContent = scheduled.title;
            showCallbackToast({
              source: "catalog",
              event: "Skill Activated",
              template_id: skillId,
              message: `Scheduled and activated persona skill '${scheduled.title}'.`
            });
            fetchTelemetry();
          }
        } catch (err) {
          console.error("Skill schedule error:", err);
        } finally {
          btn.disabled = false;
          btn.textContent = "Schedule & Activate";
        }
      });
    });
  }

  // Organizational Agent Teams
  async function loadDepartments() {
    try {
      const res = await fetch("/api/departments");
      if (res.ok) {
        const roster = await res.json();
        renderDepartmentsGrid(roster);
      }
    } catch (err) {
      console.error("Failed to load departments:", err);
    }

    if (btnCloseConsult) {
      btnCloseConsult.addEventListener("click", () => {
        if (deptConsultResult) deptConsultResult.style.display = "none";
      });
    }
  }

  function renderDepartmentsGrid(roster) {
    if (!departmentsGrid) return;

    departmentsGrid.innerHTML = roster.map((dept) => `
      <div class="dept-card glass-card">
        <div class="dept-card-top">
          <div class="dept-header-row">
            <h4 class="dept-title">${escapeHtml(dept.title || dept.name)}</h4>
            <span class="badge-track track-${getTrackClass(dept.track)}">${escapeHtml(dept.track || "Universal")}</span>
          </div>
          <div class="dept-role">${escapeHtml(dept.role || "")}</div>
          <p class="dept-focus">${escapeHtml(dept.focus || "")}</p>
        </div>
        <div class="dept-actions">
          <button class="btn btn-secondary btn-sm btn-consult-dept" data-dept-id="${escapeHtml(dept.id)}">
            Consult Agent
          </button>
        </div>
      </div>
    `).join("");

    // Wire consult buttons
    departmentsGrid.querySelectorAll(".btn-consult-dept").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const deptId = btn.getAttribute("data-dept-id");
        btn.disabled = true;
        btn.textContent = "Consulting...";

        try {
          const res = await fetch("/api/department/dispatch", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ department: deptId, task: "status" })
          });
          const result = await res.json();
          renderDepartmentConsultation(deptId, result);
        } catch (err) {
          console.error("Department consult failed:", err);
        } finally {
          btn.disabled = false;
          btn.textContent = "Consult Agent";
        }
      });
    });
  }

  function getTrackClass(trackStr) {
    const s = (trackStr || "").toLowerCase();
    if (s.includes("tech")) return "technical";
    if (s.includes("social") || s.includes("strategy") || s.includes("product")) return "social";
    if (s.includes("mental") || s.includes("safety")) return "mental";
    return "technical";
  }

  function renderDepartmentConsultation(deptId, result) {
    if (!deptConsultResult) return;
    deptConsultResult.style.display = "flex";

    consultDeptBadge.textContent = deptId.toUpperCase();
    consultDeptBadge.className = `badge-track track-${getTrackClass(deptId)}`;
    consultAgentTitle.textContent = `${(result.agent || deptId).toUpperCase()} Response`;

    const displayData = result.result || { ...result };
    delete displayData.agent;
    delete displayData.department;
    delete displayData.status;

    consultOutputView.textContent = JSON.stringify(displayData, null, 2);
    deptConsultResult.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  // Step Streaming
  function appendStepCard(step) {
    if (!step || renderedStepIds.has(step.step_id)) return;
    renderedStepIds.add(step.step_id);

    const emptyState = elStepStream.querySelector(".empty-state");
    if (emptyState) emptyState.remove();

    const card = document.createElement("div");
    card.className = "step-card glass-card";
    card.id = `step-${step.step_id}`;

    const phaseClass = `phase-${(step.phase || "deliberation").toLowerCase()}`;
    const milestoneBadge = step.is_milestone
      ? `<span class="badge-milestone"><span class="milestone-star">★</span> Checkpoint</span>`
      : "";

    card.innerHTML = `
      <div class="step-card-header">
        <div class="step-title-row">
          <span class="step-seq">#${step.sequence_num}</span>
          <span class="step-phase-pill ${phaseClass}">${escapeHtml(step.phase || "DELIBERATION")}</span>
          <h4 class="step-title">${escapeHtml(step.title || "Step")}</h4>
          ${milestoneBadge}
        </div>
        <span class="step-shielded-badge">+${step.token_weight || 0} tokens shielded</span>
      </div>
      <div class="step-body">
        <p class="step-thought">${escapeHtml(step.thought_content || "")}</p>
        ${step.observation ? `<div class="step-obs"><span class="obs-label">Observation:</span> ${escapeHtml(step.observation)}</div>` : ""}
      </div>
    `;

    elStepStream.prepend(card);
  }

  // Revisions Inspector
  function appendRevisionCard(rev) {
    if (!rev || renderedRevisionIds.has(rev.revision_id)) return;
    renderedRevisionIds.add(rev.revision_id);

    const emptyHint = elRevisionsList.querySelector(".empty-hint");
    if (emptyHint) emptyHint.remove();

    const card = document.createElement("div");
    card.className = "revision-card glass-card";
    card.innerHTML = `
      <div class="revision-header">
        <span class="rev-id">Revision #${rev.revision_id ? rev.revision_id.substring(0, 8) : "latest"}</span>
        <span class="badge-compression">${rev.compression_ratio || "1.0"}x Compression</span>
      </div>
      <div class="rev-meta">
        <span>Tokens: <strong>${rev.revised_tokens || 0}</strong></span>
        <span>Steps Distilled: <strong>${rev.steps_included_count || 0}</strong></span>
      </div>
      ${rev.patch_delta ? `<pre class="code-preview diff-preview">${escapeHtml(rev.patch_delta)}</pre>` : ""}
    `;

    elRevisionsList.prepend(card);
  }

  // ScaNN Search
  if (btnScannSearch) {
    btnScannSearch.addEventListener("click", performScannSearch);
  }
  if (scannQueryInput) {
    scannQueryInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") performScannSearch();
    });
  }

  async function performScannSearch() {
    const query = (scannQueryInput.value || "").trim();
    if (!query) return;

    btnScannSearch.disabled = true;
    btnScannSearch.textContent = "Recalling...";

    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: 3 }),
      });

      if (res.ok) {
        const results = await res.json();
        renderScannResults(results);
      }
    } catch (err) {
      console.error(err);
    } finally {
      btnScannSearch.disabled = false;
      btnScannSearch.textContent = "Search";
    }
  }

  function renderScannResults(results) {
    if (!results || results.length === 0) {
      scannResultsContainer.innerHTML = `<div class="empty-hint">No semantic matches found for this query.</div>`;
      return;
    }

    scannResultsContainer.innerHTML = results.map((r) => `
      <div class="scann-result-card glass-card">
        <div class="scann-result-header">
          <span class="scann-score">Cosine Similarity: ${(r.relevance || 0).toFixed(3)}</span>
          <span class="tier-pill tier-${(r.tier || "scratchpad").toLowerCase()}">${escapeHtml(r.tier || "SCRATCHPAD")}</span>
        </div>
        <p class="scann-content">${escapeHtml(r.content || "")}</p>
        <div class="scann-meta">
          <span>Cost: <strong>${r.token_cost || 0} tokens</strong></span>
          <span>Source: LevelDB WAL</span>
        </div>
      </div>
    `).join("");
  }

  // Run Demo Simulation
  if (btnSimulate) {
    btnSimulate.addEventListener("click", async () => {
      btnSimulate.disabled = true;
      btnSimulate.innerHTML = `<span class="btn-icon">⏳</span> Simulating...`;

      try {
        await fetch("/api/simulate", { method: "POST" });
        await fetchTelemetry();
      } catch (err) {
        console.error(err);
      } finally {
        btnSimulate.disabled = false;
        btnSimulate.innerHTML = `<span class="btn-icon">⚡</span> Run Simulation`;
      }
    });
  }

  // Revise Context
  if (btnRevise) {
    btnRevise.addEventListener("click", async () => {
      btnRevise.disabled = true;
      btnRevise.innerHTML = `<span class="btn-icon">⏳</span> Consolidating...`;

      try {
        await fetch("/api/revise", { method: "POST" });
        await fetchTelemetry();
      } catch (err) {
        console.error(err);
      } finally {
        btnRevise.disabled = false;
        btnRevise.innerHTML = `<span class="btn-icon">🔄</span> Revise Context`;
      }
    });
  }

  // Reset Session
  if (btnReset) {
    btnReset.addEventListener("click", async () => {
      const prompt = window.prompt("Enter new task prompt (or leave blank for default):", "Synthesize algorithmic trading strategy with risk parity constraints.");
      if (prompt === null) return;

      try {
        await fetch("/api/reset", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt }),
        });

        renderedStepIds.clear();
        renderedRevisionIds.clear();

        elStepStream.innerHTML = `
          <div class="empty-state">
            <div class="spinner-empty"></div>
            <p>Ready to observe LLM steps. Click <strong>"Run Simulation"</strong> or add a step below.</p>
          </div>
        `;
        elRevisionsList.innerHTML = `<div class="empty-hint">Revisions will appear as the Memory Agent consolidates steps.</div>`;

        await fetchTelemetry();
      } catch (err) {
        console.error(err);
      }
    });
  }

  // Add Step Manually
  if (btnAddStep) {
    btnAddStep.addEventListener("click", async () => {
      const title = (stepTitleInput.value || "").trim();
      const phase = stepPhaseSelect.value;
      if (!title) return;

      btnAddStep.disabled = true;
      try {
        await fetch("/api/step", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title,
            phase,
            thought: `Executing step '${title}' out-of-band to prevent LLM prompt bloat.`,
            observation: "Verified invariants.",
            is_milestone: false,
          }),
        });

        stepTitleInput.value = "";
        await fetchTelemetry();
      } catch (err) {
        console.error(err);
      } finally {
        btnAddStep.disabled = false;
      }
    });
  }

  // Template Gallery
  async function loadTemplates() {
    try {
      const res = await fetch("/api/templates");
      if (res.ok) {
        availableTemplates = await res.json();
        renderTemplateTabs();
        if (availableTemplates.length > 0) {
          selectTemplate(currentTemplateId || availableTemplates[0].id);
        }
      }
    } catch (err) {
      console.error("Failed to load templates:", err);
    }
  }

  function renderTemplateTabs() {
    elTemplateTabBar.innerHTML = availableTemplates.map((t) => `
      <button class="template-tab-btn ${t.id === currentTemplateId ? "active" : ""}" data-id="${t.id}">
        ${escapeHtml(t.title)}
      </button>
    `).join("");

    elTemplateTabBar.querySelectorAll(".template-tab-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.getAttribute("data-id");
        selectTemplate(id);
      });
    });
  }

  function selectTemplate(templateId) {
    currentTemplateId = templateId;
    const tpl = availableTemplates.find((t) => t.id === templateId) || availableTemplates[0];
    if (!tpl) return;

    elTemplateTabBar.querySelectorAll(".template-tab-btn").forEach((b) => {
      b.classList.toggle("active", b.getAttribute("data-id") === tpl.id);
    });

    elTemplateTitle.textContent = tpl.title;
    elTemplateCategory.textContent = tpl.category || "Autonomous Agent";
    elTemplateDesc.textContent = tpl.description || "";
    elTemplateBudget.textContent = `${tpl.prompt_budget || 600} tokens`;
    elTemplateQuery.textContent = tpl.sample_query || "semantic recall query";
    elTemplatePromptText.textContent = tpl.system_prompt || tpl.prompt || "";
  }

  function showCallbackToast(data) {
    if (!elCallbackToast) return;

    if (toastTimer) clearTimeout(toastTimer);

    const source = (data.source || "CLI").toUpperCase();
    elCallbackSourceBadge.textContent = source;
    elCallbackEventTitle.textContent = data.event || data.event_name || "Callback Received";

    const msg = (data.payload && data.payload.message) || data.message || `Synchronized template "${data.template_id || "raft"}"`;
    elCallbackEventDetails.textContent = msg;

    elCallbackToast.style.display = "flex";

    if (vscode) {
      vscode.postMessage({
        type: "callbackReceived",
        source: data.source,
        templateId: data.template_id,
        event: data.event
      });
    }

    toastTimer = setTimeout(() => {
      elCallbackToast.style.display = "none";
    }, 8000);
  }

  function checkUrlParameters() {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const requestedTemplate = urlParams.get("template");
      const requestedSource = urlParams.get("source");
      const requestedEvent = urlParams.get("event") || "Session Started";

      if (requestedTemplate) {
        currentTemplateId = requestedTemplate;
        setTimeout(() => {
          selectTemplate(requestedTemplate);
          showCallbackToast({
            source: requestedSource || "cli",
            event: requestedEvent,
            template_id: requestedTemplate,
            message: `Loaded template "${requestedTemplate}" via callback launcher.`
          });
        }, 300);
      }
    } catch (err) {
      console.warn("URL params check skipped:", err);
    }
  }

  if (elBtnCloseCallbackToast) {
    elBtnCloseCallbackToast.addEventListener("click", () => {
      if (elCallbackToast) elCallbackToast.style.display = "none";
      if (toastTimer) clearTimeout(toastTimer);
    });
  }

  if (btnLoadTemplate) {
    btnLoadTemplate.addEventListener("click", async () => {
      const tpl = availableTemplates.find((t) => t.id === currentTemplateId);
      if (!tpl) return;

      btnLoadTemplate.disabled = true;
      btnLoadTemplate.textContent = "Loading Template...";

      try {
        await fetch("/api/reset", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: tpl.system_prompt || tpl.prompt }),
        });

        renderedStepIds.clear();
        renderedRevisionIds.clear();

        elStepStream.innerHTML = `
          <div class="empty-state">
            <div class="spinner-empty"></div>
            <p>Active agent initialized with <strong>${escapeHtml(tpl.title)}</strong> template. Ready to observe LLM steps.</p>
          </div>
        `;
        elRevisionsList.innerHTML = `<div class="empty-hint">Revisions will appear as the Memory Agent consolidates steps.</div>`;

        await fetchTelemetry();

        showCallbackToast({
          source: "webapp",
          event: "Template Loaded",
          template_id: tpl.id,
          message: `Activated template "${tpl.title}" into agent prompt window.`
        });
      } catch (err) {
        console.error(err);
      } finally {
        btnLoadTemplate.disabled = false;
        btnLoadTemplate.textContent = "Load Into Active Agent";
      }
    });
  }

  if (btnTestTemplateSearch) {
    btnTestTemplateSearch.addEventListener("click", () => {
      const tpl = availableTemplates.find((t) => t.id === currentTemplateId);
      if (!tpl || !tpl.sample_query) return;

      scannQueryInput.value = tpl.sample_query;
      performScannSearch();
      scannQueryInput.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
