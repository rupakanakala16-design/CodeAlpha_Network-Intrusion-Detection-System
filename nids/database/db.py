"""
database/db.py
----------------
All SQLite database logic lives here: connecting, creating tables,
and seeding the database with demo data the very first time the
app is started.

Everything in this project is SIMULATED / DEMO data for an
educational cybersecurity dashboard. No real network scanning or
attacking happens anywhere in this codebase.
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

# The SQLite file lives at the project root.
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database.db")


def get_connection():
    """Return a new SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enforce foreign keys / better concurrency behaviour
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they do not exist yet, then seed demo data
    the first time the database is created."""
    is_new = not os.path.exists(DB_PATH)

    conn = get_connection()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS traffic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            destination_ip TEXT NOT NULL,
            protocol TEXT NOT NULL,
            source_port INTEGER,
            destination_port INTEGER,
            packet_size INTEGER,
            status TEXT NOT NULL DEFAULT 'Normal'
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            destination_ip TEXT NOT NULL,
            protocol TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active',
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            protocol TEXT NOT NULL,
            severity TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event TEXT NOT NULL,
            source TEXT NOT NULL,
            severity TEXT NOT NULL DEFAULT 'INFO',
            status TEXT NOT NULL DEFAULT 'Logged'
        );
        """
    )
    conn.commit()

    if is_new:
        _seed_demo_data(conn)

    conn.close()


def _seed_demo_data(conn):
    """Populate the database with clearly-labelled simulated demo data
    so the dashboard is populated the moment the app starts."""
    cur = conn.cursor()
    now = datetime.now()

    # ---- Detection rules -------------------------------------------------
    rules = [
        ("NIDS-001", "Port Scan Detection", "Detect unusual repeated connection patterns from a single source", "TCP", "HIGH", 1),
        ("NIDS-002", "ICMP Anomaly", "Detect unusual ICMP traffic patterns / ping floods", "ICMP", "MEDIUM", 1),
        ("NIDS-003", "Repeated Connection Attempts", "Detect repeated failed connection attempts (possible brute force)", "TCP", "HIGH", 1),
        ("NIDS-004", "Unusual Protocol Activity", "Flag traffic on rarely-used protocols/ports", "UDP", "MEDIUM", 1),
        ("NIDS-005", "Large Packet Anomaly", "Detect abnormally large packet sizes", "TCP", "LOW", 1),
        ("NIDS-006", "Suspicious Source Reputation", "Flag traffic from simulated known-bad demo IP ranges", "TCP", "CRITICAL", 1),
        ("NIDS-007", "DNS Tunneling Pattern", "Detect abnormal DNS query frequency", "UDP", "MEDIUM", 1),
        ("NIDS-008", "SYN Flood Pattern", "Detect high-rate simulated SYN packets", "TCP", "CRITICAL", 1),
    ]
    cur.executemany(
        "INSERT INTO rules (rule_code, name, description, protocol, severity, enabled) VALUES (?,?,?,?,?,?)",
        rules,
    )

    # ---- Simulated traffic --------------------------------------------
    protocols = ["TCP", "UDP", "ICMP"]
    statuses = ["Normal", "Normal", "Normal", "Suspicious", "Blocked"]
    demo_sources = [f"192.168.1.{i}" for i in range(2, 30)] + [f"10.0.0.{i}" for i in range(2, 30)]
    demo_destinations = [f"192.168.1.{i}" for i in range(50, 90)] + ["172.16.0.5", "172.16.0.9"]

    traffic_rows = []
    for i in range(60):
        ts = (now - timedelta(minutes=random.randint(0, 240))).strftime("%Y-%m-%d %H:%M:%S")
        traffic_rows.append(
            (
                ts,
                random.choice(demo_sources),
                random.choice(demo_destinations),
                random.choice(protocols),
                random.randint(1024, 65000),
                random.choice([22, 80, 443, 21, 53, 3389, 8080]),
                random.randint(64, 1500),
                random.choice(statuses),
            )
        )
    cur.executemany(
        """INSERT INTO traffic
           (timestamp, source_ip, destination_ip, protocol, source_port, destination_port, packet_size, status)
           VALUES (?,?,?,?,?,?,?,?)""",
        traffic_rows,
    )

    # ---- Demo alerts -----------------------------------------------------
    alert_defs = [
        ("192.168.1.10", "192.168.1.20", "TCP", "Port Scan", "HIGH", "Active", "Multiple sequential port connection attempts detected from a single simulated source."),
        ("10.0.0.15", "10.0.0.20", "ICMP", "Suspicious Traffic", "MEDIUM", "Active", "Elevated ICMP echo request frequency detected."),
        ("192.168.1.14", "192.168.1.55", "TCP", "Repeated Connection Attempts", "HIGH", "Active", "Repeated failed authentication attempts against a simulated service."),
        ("10.0.0.22", "172.16.0.5", "UDP", "Unusual Protocol Activity", "MEDIUM", "Resolved", "Traffic observed on an uncommon UDP port range."),
        ("192.168.1.8", "192.168.1.60", "TCP", "Possible Brute Force Pattern", "CRITICAL", "Active", "High-frequency login attempts detected in simulated traffic."),
        ("10.0.0.5", "172.16.0.9", "TCP", "Port Scan", "HIGH", "Resolved", "Sequential port sweep pattern detected and mitigated."),
        ("192.168.1.19", "192.168.1.77", "ICMP", "Suspicious Traffic", "LOW", "Active", "Minor anomaly in ICMP packet timing."),
        ("10.0.0.11", "10.0.0.30", "TCP", "Possible Brute Force Pattern", "CRITICAL", "Active", "Simulated credential stuffing pattern identified."),
    ]
    alert_rows = []
    for i, (src, dst, proto, atype, sev, status, desc) in enumerate(alert_defs):
        ts = (now - timedelta(minutes=random.randint(0, 180))).strftime("%Y-%m-%d %H:%M:%S")
        alert_rows.append((ts, src, dst, proto, atype, sev, status, desc))
    cur.executemany(
        """INSERT INTO alerts
           (timestamp, source_ip, destination_ip, protocol, alert_type, severity, status, description)
           VALUES (?,?,?,?,?,?,?,?)""",
        alert_rows,
    )

    # ---- Demo logs -------------------------------------------------------
    log_defs = [
        ("Network monitoring started", "SYSTEM", "INFO", "Logged"),
        ("Detection engine initialized with 8 active rules", "IDS", "INFO", "Logged"),
        ("Suspicious traffic detected", "NIDS", "HIGH", "Logged"),
        ("Port scan pattern identified", "NIDS", "HIGH", "Logged"),
        ("Alert NIDS-001 triggered", "IDS", "MEDIUM", "Logged"),
        ("Database connection established", "SYSTEM", "INFO", "Logged"),
        ("Simulated traffic generator running", "SIMULATOR", "INFO", "Logged"),
        ("Critical alert escalated", "NIDS", "CRITICAL", "Logged"),
    ]
    log_rows = []
    for event, source, sev, status in log_defs:
        ts = (now - timedelta(minutes=random.randint(0, 200))).strftime("%Y-%m-%d %H:%M:%S")
        log_rows.append((ts, event, source, sev, status))
    cur.executemany(
        "INSERT INTO logs (timestamp, event, source, severity, status) VALUES (?,?,?,?,?)",
        log_rows,
    )

    conn.commit()
