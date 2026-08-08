"""
app.py
-------
Main Flask application for the Network Intrusion Detection System
(NIDS) educational dashboard.

Everything here operates on SIMULATED / DEMO data only. No real
network scanning, exploitation, or attacks are performed by this
application. See ids/simulator.py and ids/detector.py for the safe
simulated detection engine.
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import random

from database.db import init_db, get_connection
from ids import simulator, detector

app = Flask(__name__)

# Make sure the database exists (and is seeded) before the first request.
init_db()


# ======================================================================
# PAGE ROUTES  (server-rendered HTML shells; data is loaded via fetch())
# ======================================================================

@app.route("/")
def index():
    return render_template("index.html", active_page="dashboard")


@app.route("/traffic")
def traffic_page():
    return render_template("traffic.html", active_page="traffic")


@app.route("/alerts")
def alerts_page():
    return render_template("alerts.html", active_page="alerts")


@app.route("/rules")
def rules_page():
    return render_template("rules.html", active_page="rules")


@app.route("/analytics")
def analytics_page():
    return render_template("analytics.html", active_page="analytics")


@app.route("/logs")
def logs_page():
    return render_template("logs.html", active_page="logs")


@app.route("/settings")
def settings_page():
    return render_template("settings.html", active_page="settings")


@app.route("/about")
def about_page():
    return render_template("about.html", active_page="about")


# ======================================================================
# API: DASHBOARD
# ======================================================================

@app.route("/api/dashboard")
def api_dashboard():
    conn = get_connection()

    packets_analyzed = conn.execute("SELECT COUNT(*) c FROM traffic").fetchone()["c"]
    threats_detected = conn.execute("SELECT COUNT(*) c FROM alerts").fetchone()["c"]
    critical_alerts = conn.execute(
        "SELECT COUNT(*) c FROM alerts WHERE severity = 'CRITICAL' AND status = 'Active'"
    ).fetchone()["c"]
    active_rules = conn.execute("SELECT COUNT(*) c FROM rules WHERE enabled = 1").fetchone()["c"]

    recent_alerts = conn.execute(
        "SELECT * FROM alerts ORDER BY id DESC LIMIT 8"
    ).fetchall()

    conn.close()

    return jsonify(
        {
            "stats": {
                "packets_analyzed": packets_analyzed,
                "threats_detected": threats_detected,
                "critical_alerts": critical_alerts,
                "active_rules": active_rules,
            },
            "recent_alerts": [dict(a) for a in recent_alerts],
            "system_status": "monitoring",
            "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )


@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    """Run one tick of the simulator + detector. Called by the front-end
    polling loop so the dashboard feels 'live' without a background
    thread. Entirely safe/synthetic — see ids/simulator.py."""
    packets = simulator.generate_batch(n=random.randint(3, 8))
    new_alerts = detector.analyze_and_store(packets)
    return jsonify({"packets_generated": len(packets), "alerts_generated": new_alerts})


# ======================================================================
# API: NETWORK TRAFFIC
# ======================================================================

@app.route("/api/traffic")
def api_traffic():
    protocol = request.args.get("protocol", "all")
    status = request.args.get("status", "all")
    search = request.args.get("search", "").strip()
    limit = int(request.args.get("limit", 100))

    query = "SELECT * FROM traffic WHERE 1=1"
    params = []

    if protocol != "all":
        query += " AND protocol = ?"
        params.append(protocol)
    if status != "all":
        query += " AND status = ?"
        params.append(status)
    if search:
        query += " AND (source_ip LIKE ? OR destination_ip LIKE ?)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows])


# ======================================================================
# API: SECURITY ALERTS
# ======================================================================

@app.route("/api/alerts")
def api_alerts():
    severity = request.args.get("severity", "all")
    date_filter = request.args.get("date", "all")
    search = request.args.get("search", "").strip()

    query = "SELECT * FROM alerts WHERE 1=1"
    params = []

    if severity != "all":
        query += " AND severity = ?"
        params.append(severity)
    if search:
        query += " AND (source_ip LIKE ? OR destination_ip LIKE ? OR alert_type LIKE ?)"
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]
    if date_filter == "today":
        today = datetime.now().strftime("%Y-%m-%d")
        query += " AND timestamp LIKE ?"
        params.append(f"{today}%")

    query += " ORDER BY id DESC"

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows])


@app.route("/api/alerts/<int:alert_id>/resolve", methods=["PUT"])
def api_resolve_alert(alert_id):
    conn = get_connection()
    conn.execute("UPDATE alerts SET status = 'Resolved' WHERE id = ?", (alert_id,))
    conn.execute(
        "INSERT INTO logs (timestamp, event, source, severity, status) VALUES (?,?,?,?,?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Alert #{alert_id} marked as resolved", "ANALYST", "INFO", "Logged"),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ======================================================================
# API: DETECTION RULES
# ======================================================================

@app.route("/api/rules", methods=["GET"])
def api_rules():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rules ORDER BY id ASC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/rules", methods=["POST"])
def api_add_rule():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    description = (data.get("description") or "").strip()
    protocol = data.get("protocol", "TCP")
    severity = data.get("severity", "LOW")

    if not name:
        return jsonify({"error": "Rule name is required"}), 400

    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) c FROM rules").fetchone()["c"]
    rule_code = f"NIDS-{count + 1:03d}"

    conn.execute(
        "INSERT INTO rules (rule_code, name, description, protocol, severity, enabled) VALUES (?,?,?,?,?,1)",
        (rule_code, name, description, protocol, severity),
    )
    conn.execute(
        "INSERT INTO logs (timestamp, event, source, severity, status) VALUES (?,?,?,?,?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"New detection rule created: {rule_code}", "ANALYST", "INFO", "Logged"),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "rule_code": rule_code}), 201


@app.route("/api/rules/<int:rule_id>", methods=["PUT"])
def api_update_rule(rule_id):
    data = request.get_json(force=True)
    conn = get_connection()
    existing = conn.execute("SELECT * FROM rules WHERE id = ?", (rule_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "Rule not found"}), 404

    name = data.get("name", existing["name"])
    description = data.get("description", existing["description"])
    protocol = data.get("protocol", existing["protocol"])
    severity = data.get("severity", existing["severity"])
    enabled = data.get("enabled", existing["enabled"])
    enabled = 1 if str(enabled) in ("1", "true", "True") else 0

    conn.execute(
        "UPDATE rules SET name=?, description=?, protocol=?, severity=?, enabled=? WHERE id=?",
        (name, description, protocol, severity, enabled, rule_id),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/api/rules/<int:rule_id>", methods=["DELETE"])
def api_delete_rule(rule_id):
    conn = get_connection()
    conn.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ======================================================================
# API: THREAT ANALYTICS
# ======================================================================

@app.route("/api/analytics")
def api_analytics():
    conn = get_connection()

    # Threats detected over time (last 7 "days" bucketed by demo timestamp date)
    over_time_rows = conn.execute(
        """SELECT substr(timestamp,1,10) as day, COUNT(*) as c
           FROM alerts GROUP BY day ORDER BY day ASC"""
    ).fetchall()

    by_severity_rows = conn.execute(
        "SELECT severity, COUNT(*) as c FROM alerts GROUP BY severity"
    ).fetchall()

    by_protocol_rows = conn.execute(
        "SELECT protocol, COUNT(*) as c FROM alerts GROUP BY protocol"
    ).fetchall()

    top_sources_rows = conn.execute(
        """SELECT source_ip, COUNT(*) as c FROM alerts
           GROUP BY source_ip ORDER BY c DESC LIMIT 6"""
    ).fetchall()

    status_dist_rows = conn.execute(
        "SELECT status, COUNT(*) as c FROM alerts GROUP BY status"
    ).fetchall()

    conn.close()

    severity_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    by_severity = {row["severity"]: row["c"] for row in by_severity_rows}

    return jsonify(
        {
            "over_time": [{"day": r["day"], "count": r["c"]} for r in over_time_rows],
            "by_severity": {sev: by_severity.get(sev, 0) for sev in severity_order},
            "by_protocol": [{"protocol": r["protocol"], "count": r["c"]} for r in by_protocol_rows],
            "top_sources": [{"ip": r["source_ip"], "count": r["c"]} for r in top_sources_rows],
            "status_distribution": [{"status": r["status"], "count": r["c"]} for r in status_dist_rows],
        }
    )


# ======================================================================
# API: SYSTEM LOGS
# ======================================================================

@app.route("/api/logs")
def api_logs():
    search = request.args.get("search", "").strip()
    severity = request.args.get("severity", "all")

    query = "SELECT * FROM logs WHERE 1=1"
    params = []
    if search:
        query += " AND (event LIKE ? OR source LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if severity != "all":
        query += " AND severity = ?"
        params.append(severity)

    query += " ORDER BY id DESC LIMIT 200"

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/logs/clear", methods=["POST"])
def api_clear_logs():
    conn = get_connection()
    conn.execute("DELETE FROM logs")
    conn.execute(
        "INSERT INTO logs (timestamp, event, source, severity, status) VALUES (?,?,?,?,?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Demo logs cleared by analyst", "ANALYST", "INFO", "Logged"),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ======================================================================
# Error handling
# ======================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
