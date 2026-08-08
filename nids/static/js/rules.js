/* rules.js — Detection Rules page */

let currentRules = [];

async function loadRules() {
  const body = document.getElementById("rulesBody");
  try {
    const res = await fetch("/api/rules");
    if (!res.ok) throw new Error("bad response");
    currentRules = await res.json();

    if (!currentRules.length) {
      body.innerHTML = `<tr><td colspan="7"><div class="empty-state"><i class="fa-solid fa-list-check"></i><p>No rules configured yet.</p></div></td></tr>`;
      return;
    }

    body.innerHTML = currentRules
      .map((r) => {
        const sevClass = NIDS.severityClass(r.severity);
        const statusLabel = r.enabled ? "Enabled" : "Disabled";
        const statusClass = r.enabled ? "enabled" : "disabled";
        return `<tr>
          <td class="mono">${r.rule_code}</td>
          <td>${NIDS.escapeHtml(r.name)}</td>
          <td style="max-width:280px; white-space:normal; color:var(--text-2); font-size:12px;">${NIDS.escapeHtml(r.description || "")}</td>
          <td>${r.protocol}</td>
          <td><span class="badge ${sevClass}">${r.severity}</span></td>
          <td style="display:flex; align-items:center; gap:8px;">
            <label class="switch">
              <input type="checkbox" class="toggle-enabled" data-id="${r.id}" ${r.enabled ? "checked" : ""}>
              <span class="slider"></span>
            </label>
            <span class="status-tag ${statusClass}">${statusLabel}</span>
          </td>
          <td style="display:flex; gap:6px;">
            <button class="btn btn-ghost btn-sm edit-btn" data-id="${r.id}"><i class="fa-solid fa-pen"></i></button>
            <button class="btn btn-danger btn-sm delete-btn" data-id="${r.id}"><i class="fa-solid fa-trash"></i></button>
          </td>
        </tr>`;
      })
      .join("");

    document.querySelectorAll(".toggle-enabled").forEach((el) =>
      el.addEventListener("change", () => toggleEnabled(parseInt(el.dataset.id, 10), el.checked))
    );
    document.querySelectorAll(".edit-btn").forEach((btn) =>
      btn.addEventListener("click", () => openEditModal(parseInt(btn.dataset.id, 10)))
    );
    document.querySelectorAll(".delete-btn").forEach((btn) =>
      btn.addEventListener("click", () => deleteRule(parseInt(btn.dataset.id, 10)))
    );
  } catch (err) {
    console.error(err);
    body.innerHTML = `<tr><td colspan="7"><div class="empty-state"><i class="fa-solid fa-plug-circle-xmark"></i><p>Could not reach the backend.</p></div></td></tr>`;
  }
}

async function toggleEnabled(id, enabled) {
  try {
    await fetch(`/api/rules/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled }),
    });
    loadRules();
  } catch (err) {
    console.error(err);
  }
}

async function deleteRule(id) {
  if (!confirm("Delete this detection rule? This cannot be undone.")) return;
  try {
    await fetch(`/api/rules/${id}`, { method: "DELETE" });
    loadRules();
  } catch (err) {
    console.error(err);
  }
}

function openAddModal() {
  document.getElementById("ruleModalTitle").textContent = "Add Detection Rule";
  document.getElementById("ruleId").value = "";
  document.getElementById("ruleForm").reset();
  document.getElementById("ruleModal").classList.add("show");
}

function openEditModal(id) {
  const rule = currentRules.find((r) => r.id === id);
  if (!rule) return;
  document.getElementById("ruleModalTitle").textContent = "Edit Detection Rule";
  document.getElementById("ruleId").value = rule.id;
  document.getElementById("ruleName").value = rule.name;
  document.getElementById("ruleDescription").value = rule.description || "";
  document.getElementById("ruleProtocol").value = rule.protocol;
  document.getElementById("ruleSeverity").value = rule.severity;
  document.getElementById("ruleModal").classList.add("show");
}

function closeRuleModal() {
  document.getElementById("ruleModal").classList.remove("show");
}

async function submitRuleForm(e) {
  e.preventDefault();
  const id = document.getElementById("ruleId").value;
  const payload = {
    name: document.getElementById("ruleName").value.trim(),
    description: document.getElementById("ruleDescription").value.trim(),
    protocol: document.getElementById("ruleProtocol").value,
    severity: document.getElementById("ruleSeverity").value,
  };

  try {
    if (id) {
      await fetch(`/api/rules/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } else {
      await fetch("/api/rules", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    }
    closeRuleModal();
    loadRules();
  } catch (err) {
    console.error(err);
    alert("Could not save the rule. Check the console for details.");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadRules();
  document.getElementById("addRuleBtn").addEventListener("click", openAddModal);
  document.getElementById("ruleModalClose").addEventListener("click", closeRuleModal);
  document.getElementById("ruleModalCancel").addEventListener("click", closeRuleModal);
  document.getElementById("ruleForm").addEventListener("submit", submitRuleForm);
  document.getElementById("ruleModal").addEventListener("click", (e) => {
    if (e.target.id === "ruleModal") closeRuleModal();
  });
});
