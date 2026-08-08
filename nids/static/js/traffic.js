/* traffic.js — Network Traffic page */

let trafficDebounce = null;

async function loadTraffic() {
  const search = document.getElementById("searchInput").value.trim();
  const protocol = document.getElementById("protocolFilter").value;
  const status = document.getElementById("statusFilter").value;

  const params = new URLSearchParams({ search, protocol, status, limit: "150" });
  const body = document.getElementById("trafficBody");

  try {
    const res = await fetch(`/api/traffic?${params.toString()}`);
    if (!res.ok) throw new Error("bad response");
    const rows = await res.json();

    if (!rows.length) {
      body.innerHTML = `<tr><td colspan="8"><div class="empty-state"><i class="fa-solid fa-satellite-dish"></i><p>No traffic matches your filters.</p></div></td></tr>`;
      return;
    }

    body.innerHTML = rows
      .map((r) => {
        const statusClass = NIDS.statusClass(r.status);
        return `<tr>
          <td class="mono">${r.timestamp}</td>
          <td class="ip-cell">${NIDS.escapeHtml(r.source_ip)}</td>
          <td class="ip-cell">${NIDS.escapeHtml(r.destination_ip)}</td>
          <td>${r.protocol}</td>
          <td class="mono">${r.source_port}</td>
          <td class="mono">${r.destination_port}</td>
          <td class="mono">${r.packet_size}B</td>
          <td><span class="status-tag ${statusClass}">${r.status}</span></td>
        </tr>`;
      })
      .join("");
  } catch (err) {
    console.error(err);
    body.innerHTML = `<tr><td colspan="8"><div class="empty-state"><i class="fa-solid fa-plug-circle-xmark"></i><p>Could not reach the backend.</p></div></td></tr>`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadTraffic();
  document.getElementById("refreshBtn").addEventListener("click", loadTraffic);
  document.getElementById("protocolFilter").addEventListener("change", loadTraffic);
  document.getElementById("statusFilter").addEventListener("change", loadTraffic);
  document.getElementById("searchInput").addEventListener("input", () => {
    clearTimeout(trafficDebounce);
    trafficDebounce = setTimeout(loadTraffic, 300);
  });
  setInterval(loadTraffic, 8000);
});
