/* logs.js — System Logs page */

let logSearchDebounce = null;

function logSeverityBadgeClass(sev) {
  switch ((sev || "").toUpperCase()) {
    case "INFO": return "info";
    case "MEDIUM": return "medium";
    case "HIGH": return "high";
    case "CRITICAL": return "critical";
    default: return "info";
  }
}

async function loadLogs() {
  const search = document.getElementById("searchInput").value.trim();
  const severity = document.getElementById("severityFilter").value;
  const params = new URLSearchParams({ search, severity });
  const body = document.getElementById("logsBody");

  try {
    const res = await fetch(`/api/logs?${params.toString()}`);
    if (!res.ok) throw new Error("bad response");
    const rows = await res.json();

    if (!rows.length) {
      body.innerHTML = `<tr><td colspan="5"><div class="empty-state"><i class="fa-solid fa-terminal"></i><p>No log entries yet.</p></div></td></tr>`;
      return;
    }

    body.innerHTML = rows
      .map(
        (l) => `<tr>
          <td class="mono">${l.timestamp}</td>
          <td>${NIDS.escapeHtml(l.event)}</td>
          <td class="mono">${NIDS.escapeHtml(l.source)}</td>
          <td><span class="badge ${logSeverityBadgeClass(l.severity)}">${l.severity}</span></td>
          <td><span class="status-tag resolved">${l.status}</span></td>
        </tr>`
      )
      .join("");
  } catch (err) {
    console.error(err);
    body.innerHTML = `<tr><td colspan="5"><div class="empty-state"><i class="fa-solid fa-plug-circle-xmark"></i><p>Could not reach the backend.</p></div></td></tr>`;
  }
}

async function clearLogs() {
  if (!confirm("Clear all demo log entries? This cannot be undone.")) return;
  try {
    await fetch("/api/logs/clear", { method: "POST" });
    loadLogs();
  } catch (err) {
    console.error(err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadLogs();
  document.getElementById("severityFilter").addEventListener("change", loadLogs);
  document.getElementById("clearLogsBtn").addEventListener("click", clearLogs);
  document.getElementById("searchInput").addEventListener("input", () => {
    clearTimeout(logSearchDebounce);
    logSearchDebounce = setTimeout(loadLogs, 300);
  });
  setInterval(loadLogs, 8000);
});
