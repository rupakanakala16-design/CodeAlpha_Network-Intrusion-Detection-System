"""
ids/detector.py
-----------------
A simple, rule-based detection engine. It looks at recently generated
SIMULATED traffic and, when it matches a pattern described by an
enabled rule, writes a new alert + log entry to the database.

This mirrors (in a beginner-friendly way) how a real NIDS such as
Snort/Suricata inspects packets against signatures — but it only ever
operates on locally generated demo data.

Optional real-IDS integration:
See `ids/README_INTEGRATION.md` (documented in the project README) for
how you could point this layer at a real Snort/Suricata EVE JSON log
instead of the simulator, without changing anything else downstream.
"""

from collections import defaultdict
from datetime import datetime

from database.db import get_connection


def _log(conn, event, source, severity, status="Logged"):
    conn.execute(
        "INSERT INTO logs (timestamp, event, source, severity, status) VALUES (?,?,?,?,?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), event, source, severity, status),
    )


def _rule_enabled(conn, rule_code):
    row = conn.execute("SELECT enabled FROM rules WHERE rule_code = ?", (rule_code,)).fetchone()
    return bool(row and row["enabled"])


def analyze_and_store(packets):
    """Insert a batch of simulated packets into `traffic`, then run
    lightweight detection logic over that batch to decide whether any
    alerts should be raised. Returns the number of alerts generated.
    """
    if not packets:
        return 0

    conn = get_connection()
    cur = conn.cursor()

    for p in packets:
        cur.execute(
            """INSERT INTO traffic
               (timestamp, source_ip, destination_ip, protocol, source_port, destination_port, packet_size, status)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                p["timestamp"],
                p["source_ip"],
                p["destination_ip"],
                p["protocol"],
                p["source_port"],
                p["destination_port"],
                p["packet_size"],
                p["status"],
            ),
        )

    alerts_generated = 0

    # ---- Rule: Port Scan Detection (NIDS-001) -----------------------
    # IF many connection attempts occur from the same simulated source
    # within this batch -> generate "Possible Port Scan" alert.
    if _rule_enabled(conn, "NIDS-001"):
        counts = defaultdict(list)
        for p in packets:
            if p["protocol"] == "TCP":
                counts[p["source_ip"]].append(p)
        for src, plist in counts.items():
            distinct_ports = {p["destination_port"] for p in plist}
            if len(plist) >= 5 and len(distinct_ports) >= 4:
                dst = plist[0]["destination_ip"]
                cur.execute(
                    """INSERT INTO alerts
                       (timestamp, source_ip, destination_ip, protocol, alert_type, severity, status, description)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        src,
                        dst,
                        "TCP",
                        "Port Scan",
                        "HIGH",
                        "Active",
                        f"Simulated source contacted {len(distinct_ports)} distinct ports in a short window "
                        f"({len(plist)} packets). Matches rule NIDS-001.",
                    ),
                )
                _log(conn, f"Port scan pattern identified from {src}", "NIDS", "HIGH")
                alerts_generated += 1

    # ---- Rule: ICMP Anomaly (NIDS-002) -------------------------------
    if _rule_enabled(conn, "NIDS-002"):
        icmp_packets = [p for p in packets if p["protocol"] == "ICMP"]
        if len(icmp_packets) >= 6:
            src = icmp_packets[0]["source_ip"]
            dst = icmp_packets[0]["destination_ip"]
            cur.execute(
                """INSERT INTO alerts
                   (timestamp, source_ip, destination_ip, protocol, alert_type, severity, status, description)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    src,
                    dst,
                    "ICMP",
                    "Suspicious Traffic",
                    "MEDIUM",
                    "Active",
                    f"Elevated simulated ICMP frequency detected ({len(icmp_packets)} packets). Matches rule NIDS-002.",
                ),
            )
            _log(conn, "Unusual ICMP traffic pattern detected", "NIDS", "MEDIUM")
            alerts_generated += 1

    # ---- Rule: Repeated Connection Attempts (NIDS-003) ---------------
    if _rule_enabled(conn, "NIDS-003"):
        suspicious_status = [p for p in packets if p["status"] == "Suspicious"]
        if len(suspicious_status) >= 6:
            src = suspicious_status[0]["source_ip"]
            dst = suspicious_status[0]["destination_ip"]
            cur.execute(
                """INSERT INTO alerts
                   (timestamp, source_ip, destination_ip, protocol, alert_type, severity, status, description)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    src,
                    dst,
                    "TCP",
                    "Possible Brute Force Pattern",
                    "CRITICAL",
                    "Active",
                    "Repeated simulated connection attempts detected in a short window. Matches rule NIDS-003.",
                ),
            )
            _log(conn, f"Repeated connection attempts flagged from {src}", "NIDS", "CRITICAL")
            alerts_generated += 1

    if alerts_generated == 0:
        _log(conn, f"Analyzed {len(packets)} simulated packets — no threats found", "IDS", "INFO")

    conn.commit()
    conn.close()
    return alerts_generated
