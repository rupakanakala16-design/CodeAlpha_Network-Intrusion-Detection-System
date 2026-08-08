/* common.js
 * Shared across every page: mobile sidebar toggle, a small helper for
 * severity/status badge classes, and a lightweight "is the backend
 * alive" heartbeat that flips the topbar status pill between
 * "Monitoring Active" (🟢) and "Connection Lost" (🔴).
 */

(function () {
  const sidebar = document.getElementById("sidebar");
  const backdrop = document.getElementById("sidebarBackdrop");
  const toggle = document.getElementById("menuToggle");

  function openSidebar() {
    sidebar.classList.add("open");
    backdrop.classList.add("show");
  }
  function closeSidebar() {
    sidebar.classList.remove("open");
    backdrop.classList.remove("show");
  }
  if (toggle) toggle.addEventListener("click", () => {
    sidebar.classList.contains("open") ? closeSidebar() : openSidebar();
  });
  if (backdrop) backdrop.addEventListener("click", closeSidebar);

  // Close the mobile sidebar automatically after navigating.
  document.querySelectorAll(".nav-link").forEach(el => el.addEventListener("click", closeSidebar));

  // ---- Heartbeat: pings /api/dashboard periodically just to confirm
  // the Flask backend is reachable, independent of page-specific polling.
  const pill = document.getElementById("globalStatusPill");
  const pillText = document.getElementById("globalStatusText");

  async function heartbeat() {
    try {
      const res = await fetch("/api/dashboard");
      if (!res.ok) throw new Error("bad status");
      if (pill) { pill.classList.remove("offline"); }
      if (pillText) pillText.textContent = "Monitoring Active";
    } catch (e) {
      if (pill) { pill.classList.add("offline"); }
      if (pillText) pillText.textContent = "Connection Lost";
    }
  }
  heartbeat();
  setInterval(heartbeat, 8000);

  window.NIDS = window.NIDS || {};

  window.NIDS.severityClass = function (sev) {
    switch ((sev || "").toUpperCase()) {
      case "LOW": return "low";
      case "MEDIUM": return "medium";
      case "HIGH": return "high";
      case "CRITICAL": return "critical";
      default: return "info";
    }
  };

  window.NIDS.statusClass = function (status) {
    return (status || "").toLowerCase().replace(/\s+/g, "-");
  };

  window.NIDS.timeAgo = function (isoLike) {
    try {
      const d = new Date(isoLike.replace(" ", "T"));
      const diff = Math.floor((Date.now() - d.getTime()) / 1000);
      if (diff < 60) return `${diff}s ago`;
      if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
      if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
      return `${Math.floor(diff / 86400)}d ago`;
    } catch (e) {
      return isoLike;
    }
  };

  window.NIDS.escapeHtml = function (str) {
    if (str === null || str === undefined) return "";
    return String(str)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  };
})();
