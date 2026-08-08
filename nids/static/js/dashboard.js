/* dashboard.js
 * Drives the main Dashboard page: pulls live stats + recent alerts from
 * Flask, animates the counters, renders blips on the 3D radar sweep,
 * and periodically asks the backend to run one "tick" of the simulated
 * traffic generator + detector so the page feels alive.
 */

const sevToBlipClass = (sev) => {
  switch ((sev || "").toUpperCase()) {
    case "LOW": return "low";
    case "MEDIUM": return "med";
    case "HIGH": return "high";
    default: return ""; // critical uses default red
  }
};

function animateCount(el, target) {
  const start = parseInt(el.textContent.replace(/,/g, ""), 10) || 0;
  const duration = 600;
  const startTime = performance.now();
  function step(now) {
    const progress = Math.min(1, (now - startTime) / duration);
    const value = Math.round(start + (target - start) * progress);
    el.textContent = value.toLocaleString();
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function renderRadarBlips(alerts) {
  const container = document.getElementById("radarBlips");
  if (!container) return;
  container.innerHTML = "";

  // place up to 8 blips at deterministic-ish pseudo-random positions
  alerts.slice(0, 8).forEach((alert, i) => {
    const angle = (i * 47 + alert.id * 13) % 360;
    const radiusPct = 20 + ((alert.id * 7) % 30); // 20% - 50% from center
    const rad = (angle * Math.PI) / 180;
    const x = 50 + radiusPct * Math.cos(rad);
    const y = 50 + radiusPct * Math.sin(rad);

    const blip = document.createElement("div");
    blip.className = `radar-blip ${sevToBlipClass(alert.severity)}`;
    blip.style.left = `${x}%`;
    blip.style.top = `${y}%`;
    blip.style.animationDelay = `${(i * 0.3).toFixed(1)}s`;
    blip.title = `${alert.alert_type} — ${alert.source_ip}`;
    container.appendChild(blip);
  });
}

function renderRecentAlerts(alerts) {
  const body = document.getElementById("recentAlertsBody");
  if (!body) return;

  if (!alerts.length) {
    body.innerHTML = `<tr><td colspan="7"><div class="empty-state"><i class="fa-solid fa-shield-halved"></i><p>No alerts yet — the simulated engine hasn't flagged anything.</p></div></td></tr>`;
    return;
  }

  body.innerHTML = alerts
    .map((a) => {
      const sevClass = NIDS.severityClass(a.severity);
      const statusClass = NIDS.statusClass(a.status);
      return `<tr>
        <td class="mono">${NIDS.timeAgo(a.timestamp)}</td>
        <td class="ip-cell">${NIDS.escapeHtml(a.source_ip)}</td>
        <td class="ip-cell">${NIDS.escapeHtml(a.destination_ip)}</td>
        <td>${NIDS.escapeHtml(a.protocol)}</td>
        <td>${NIDS.escapeHtml(a.alert_type)}</td>
        <td><span class="badge ${sevClass}">${a.severity}</span></td>
        <td><span class="status-tag ${statusClass}">${a.status}</span></td>
      </tr>`;
    })
    .join("");
}

async function loadDashboard() {
  try {
    const res = await fetch("/api/dashboard");
    if (!res.ok) throw new Error("Dashboard fetch failed");
    const data = await res.json();

    animateCount(document.getElementById("statPackets"), data.stats.packets_analyzed);
    animateCount(document.getElementById("statThreats"), data.stats.threats_detected);
    animateCount(document.getElementById("statCritical"), data.stats.critical_alerts);
    animateCount(document.getElementById("statRules"), data.stats.active_rules);

    document.getElementById("miniRulesActive").textContent = data.stats.active_rules;
    document.getElementById("serverTime").textContent = data.server_time.split(" ")[1] || data.server_time;

    renderRecentAlerts(data.recent_alerts);
    renderRadarBlips(data.recent_alerts);
  } catch (err) {
    console.error(err);
    const body = document.getElementById("recentAlertsBody");
    if (body) {
      body.innerHTML = `<tr><td colspan="7"><div class="empty-state"><i class="fa-solid fa-plug-circle-xmark"></i><p>Could not reach the backend. Is app.py running?</p></div></td></tr>`;
    }
  }
}

async function tickSimulator() {
  try {
    await fetch("/api/simulate", { method: "POST" });
    document.getElementById("lastTick").textContent = "just now";
  } catch (err) {
    console.error("Simulator tick failed", err);
  }
  loadDashboard();
}

document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();
  // Every 5 seconds: generate new simulated traffic, run detection, refresh UI.
  setInterval(tickSimulator, 5000);
});
