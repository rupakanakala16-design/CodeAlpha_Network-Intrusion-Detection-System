/* alerts.js — Security Alerts page */

let currentAlerts = [];
let searchDebounce = null;

async function loadAlerts() {
  const search = document.getElementById("searchInput").value.trim();
  const severity = document.getElementById("severityFilter").value;
  const date = document.getElementById("dateFilter").value;
  const params = new URLSearchParams({ search, severity, date });
  const body = document.getElementById("alertsBody");

  try {
    const res = await fetch(`/api/alerts?${params.toString()}`);
    if (!res.ok) throw new Error("bad response");
    currentAlerts = await res.json();

    if (!currentAlerts.length) {
      body.innerHTML = `<tr><td colspan="8"><div class="empty-state"><i class="fa-solid fa-shield-halved"></i><p>No alerts match your filters.</p></div></td></tr>`;
      return;
    }

    body.innerHTML = currentAlerts
      .map((a) => {
        const sevClass = NIDS.severityClass(a.severity);
        const statusClass = NIDS.statusClass(a.status);
        const resolveBtn =
          a.status === "Active"
            ? `<button class="btn btn-ghost btn-sm resolve-btn" data-id="${a.id}"><i class="fa-solid fa-check"></i></button>`
            : `<span style="color:var(--text-2); font-size:11px;">—</span>`;
        return `<tr>
          <td class="mono">${a.timestamp}</td>
          <td class="ip-cell">${NIDS.escapeHtml(a.source_ip)}</td>
          <td class="ip-cell">${NIDS.escapeHtml(a.destination_ip)}</td>
          <td>${a.protocol}</td>
          <td>${NIDS.escapeHtml(a.alert_type)}</td>
          <td><span class="badge ${sevClass}">${a.severity}</span></td>
          <td><span class="status-tag ${statusClass}">${a.status}</span></td>
          <td style="display:flex; gap:6px;">
            <button class="btn btn-ghost btn-sm view-btn" data-id="${a.id}"><i class="fa-solid fa-eye"></i></button>
            ${resolveBtn}
          </td>
        </tr>`;
      })
      .join("");

    document.querySelectorAll(".view-btn").forEach((btn) =>
      btn.addEventListener("click", () => openModal(parseInt(btn.dataset.id, 10)))
    );
    document.querySelectorAll(".resolve-btn").forEach((btn) =>
      btn.addEventListener("click", () => resolveAlert(parseInt(btn.dataset.id, 10)))
    );
  } catch (err) {
    console.error(err);
    body.innerHTML = `<tr><td colspan="8"><div class="empty-state"><i class="fa-solid fa-plug-circle-xmark"></i><p>Could not reach the backend.</p></div></td></tr>`;
  }
}

function openModal(id) {
  const alert = currentAlerts.find((a) => a.id === id);
  if (!alert) return;
  const modal = document.getElementById("alertModal");
  document.getElementById("modalTitle").textContent = alert.alert_type;
  document.getElementById("modalBody").innerHTML = `
    <div style="margin-bottom:8px;"><strong style="color:var(--text-0)">Severity:</strong> <span class="badge ${NIDS.severityClass(alert.severity)}">${alert.severity}</span></div>
    <div style="margin-bottom:8px;"><strong style="color:var(--text-0)">Status:</strong> <span class="status-tag ${NIDS.statusClass(alert.status)}">${alert.status}</span></div>
    <div style="margin-bottom:8px;"><strong style="color:var(--text-0)">Source:</strong> <span class="mono">${NIDS.escapeHtml(alert.source_ip)}</span></div>
    <div style="margin-bottom:8px;"><strong style="color:var(--text-0)">Destination:</strong> <span class="mono">${NIDS.escapeHtml(alert.destination_ip)}</span></div>
    <div style="margin-bottom:8px;"><strong style="color:var(--text-0)">Protocol:</strong> ${alert.protocol}</div>
    <div style="margin-bottom:8px;"><strong style="color:var(--text-0)">Detected:</strong> <span class="mono">${alert.timestamp}</span></div>
    <div><strong style="color:var(--text-0)">Description:</strong><br>${NIDS.escapeHtml(alert.description || "No further detail available for this simulated alert.")}</div>
  `;
  const resolveBtn = document.getElementById("modalResolveBtn");
  resolveBtn.style.display = alert.status === "Active" ? "inline-flex" : "none";
  resolveBtn.onclick = () => resolveAlert(id, true);
  modal.classList.add("show");
}

function closeModal() {
  document.getElementById("alertModal").classList.remove("show");
}

async function resolveAlert(id, fromModal = false) {
  try {
    await fetch(`/api/alerts/${id}/resolve`, { method: "PUT" });
    if (fromModal) closeModal();
    loadAlerts();
  } catch (err) {
    console.error("Could not resolve alert", err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadAlerts();
  document.getElementById("severityFilter").addEventListener("change", loadAlerts);
  document.getElementById("dateFilter").addEventListener("change", loadAlerts);
  document.getElementById("searchInput").addEventListener("input", () => {
    clearTimeout(searchDebounce);
    searchDebounce = setTimeout(loadAlerts, 300);
  });
  document.getElementById("modalClose").addEventListener("click", closeModal);
  document.getElementById("modalCloseBtn").addEventListener("click", closeModal);
  document.getElementById("alertModal").addEventListener("click", (e) => {
    if (e.target.id === "alertModal") closeModal();
  });
  setInterval(loadAlerts, 8000);
});
