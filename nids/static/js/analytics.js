/* analytics.js — Threat Analytics page (Chart.js) */

Chart.defaults.color = "#aab4c8";
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.borderColor = "rgba(148,163,184,0.12)";

const PALETTE = {
  signal: "#22e5ff",
  violet: "#8b6bff",
  low: "#34d399",
  medium: "#fbbf24",
  high: "#fb7a3e",
  critical: "#f4415f",
};

let charts = {};

function destroyIfExists(key) {
  if (charts[key]) charts[key].destroy();
}

function buildOverTime(data) {
  destroyIfExists("overTime");
  const ctx = document.getElementById("chartOverTime");
  const gradient = ctx.getContext("2d").createLinearGradient(0, 0, 0, 260);
  gradient.addColorStop(0, "rgba(34,229,255,0.35)");
  gradient.addColorStop(1, "rgba(34,229,255,0.0)");

  charts.overTime = new Chart(ctx, {
    type: "line",
    data: {
      labels: data.map((d) => d.day),
      datasets: [
        {
          label: "Alerts",
          data: data.map((d) => d.count),
          borderColor: PALETTE.signal,
          backgroundColor: gradient,
          fill: true,
          tension: 0.35,
          pointRadius: 3,
          pointBackgroundColor: PALETTE.signal,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true, ticks: { precision: 0 } },
      },
    },
  });
}

function buildSeverity(bySeverity) {
  destroyIfExists("severity");
  const labels = Object.keys(bySeverity);
  const values = Object.values(bySeverity);
  charts.severity = new Chart(document.getElementById("chartSeverity"), {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor: [PALETTE.low, PALETTE.medium, PALETTE.high, PALETTE.critical],
          borderColor: "#0b111f",
          borderWidth: 3,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "62%",
      plugins: { legend: { position: "bottom", labels: { boxWidth: 10, padding: 14 } } },
    },
  });
}

function buildProtocol(byProtocol) {
  destroyIfExists("protocol");
  charts.protocol = new Chart(document.getElementById("chartProtocol"), {
    type: "bar",
    data: {
      labels: byProtocol.map((p) => p.protocol),
      datasets: [
        {
          label: "Alerts",
          data: byProtocol.map((p) => p.count),
          backgroundColor: PALETTE.violet,
          borderRadius: 8,
          maxBarThickness: 46,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true, ticks: { precision: 0 } },
      },
    },
  });
}

function buildTopSources(topSources) {
  destroyIfExists("topSources");
  charts.topSources = new Chart(document.getElementById("chartTopSources"), {
    type: "bar",
    data: {
      labels: topSources.map((s) => s.ip),
      datasets: [
        {
          label: "Alerts",
          data: topSources.map((s) => s.count),
          backgroundColor: PALETTE.signal,
          borderRadius: 8,
        },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { beginAtZero: true, ticks: { precision: 0 } },
        y: { grid: { display: false }, ticks: { font: { family: "JetBrains Mono" } } },
      },
    },
  });
}

function buildStatus(statusDist) {
  destroyIfExists("status");
  charts.status = new Chart(document.getElementById("chartStatus"), {
    type: "pie",
    data: {
      labels: statusDist.map((s) => s.status),
      datasets: [
        {
          data: statusDist.map((s) => s.count),
          backgroundColor: [PALETTE.critical, PALETTE.low, PALETTE.medium],
          borderColor: "#0b111f",
          borderWidth: 3,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "bottom", labels: { boxWidth: 10, padding: 14 } } },
    },
  });
}

async function loadAnalytics() {
  try {
    const res = await fetch("/api/analytics");
    if (!res.ok) throw new Error("bad response");
    const data = await res.json();

    buildOverTime(data.over_time);
    buildSeverity(data.by_severity);
    buildProtocol(data.by_protocol);
    buildTopSources(data.top_sources);
    buildStatus(data.status_distribution);
  } catch (err) {
    console.error("Could not load analytics", err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadAnalytics();
  setInterval(loadAnalytics, 15000);
});
