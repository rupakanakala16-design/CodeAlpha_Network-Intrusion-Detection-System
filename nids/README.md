# Network Intrusion Detection System (NIDS) — Educational Dashboard

A full-stack, glassmorphism-styled cybersecurity dashboard that monitors **simulated** network
traffic, applies configurable detection rules, raises security alerts, and visualizes threats —
built for coursework and portfolio demonstration.

> ⚠️ **Educational / safe-use project.** All traffic, IP addresses, and alerts shown are generated
> by a local simulator (`ids/simulator.py`). This application never scans, exploits, or attacks a
> real network. See "How the Simulated IDS Works" below.

---

## Objective

Monitor network traffic and identify suspicious activity using a small rule-based detection
engine, then surface that activity through a live dashboard, alert feed, analytics charts, and
system logs — the same workflow a real Security Operations Center (SOC) tool follows, without any
real scanning or attack traffic.

## Features

- **Live dashboard** with animated stat counters and a 3D CSS radar-sweep visualization
- **Network traffic log** with search, protocol filter, and status filter
- **Security alerts** with severity/date filters, a detail modal, and one-click resolve
- **Detection rules manager** — enable/disable, add, edit, and delete rules (persisted in SQLite)
- **Threat analytics** — 5 Chart.js visualizations (time series, severity, protocol, top sources, status)
- **System logs** with search, severity filter, and a "clear demo logs" action
- **Fully responsive** dark glassmorphism UI with a collapsible mobile sidebar
- **JavaScript polling** (5–15s) keeps every page's data live without a page reload

## Technologies Used

| Layer      | Stack                                                             |
|------------|--------------------------------------------------------------------|
| Frontend   | HTML5, CSS3 (custom glassmorphism design system), JavaScript, Bootstrap 5, Chart.js, Font Awesome |
| Backend    | Python 3, Flask                                                    |
| Database   | SQLite                                                             |
| Detection  | Custom rule-based engine (`ids/detector.py`) + safe simulator (`ids/simulator.py`) |

## Folder Structure

```
network-intrusion-detection/
│
├── app.py                  # Flask app: page routes + JSON API
├── requirements.txt
├── database.db              # created automatically on first run
│
├── templates/
│   ├── base.html            # shared shell: sidebar, topbar
│   ├── index.html           # Dashboard
│   ├── traffic.html         # Network Traffic
│   ├── alerts.html          # Security Alerts
│   ├── rules.html           # Detection Rules
│   ├── analytics.html       # Threat Analytics
│   ├── logs.html            # System Logs
│   ├── settings.html        # Settings
│   └── about.html           # About Project
│
├── static/
│   ├── css/
│   │   └── style.css        # design system (glassmorphism, radar visual, tables, charts)
│   ├── js/
│   │   ├── common.js         # sidebar toggle, heartbeat, shared helpers
│   │   ├── dashboard.js
│   │   ├── traffic.js
│   │   ├── alerts.js
│   │   ├── rules.js
│   │   ├── analytics.js
│   │   └── logs.js
│   └── images/
│
├── database/
│   └── db.py                # schema + demo data seeding
│
├── ids/
│   ├── simulator.py         # SAFE simulated traffic generator
│   └── detector.py          # rule-based detection engine
│
└── README.md
```

## Installation

1. **Create a virtual environment**

   ```bash
   python -m venv venv
   ```

2. **Activate it**

   Windows:
   ```bash
   venv\Scripts\activate
   ```
   macOS / Linux:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## How to Run

```bash
python app.py
```

Then open your browser to:

```
http://127.0.0.1:5000
```

The SQLite database (`database.db`) and all demo data are created automatically the first time
the app starts — there is nothing else to configure.

### Running in VS Code

1. Open the `network-intrusion-detection` folder in VS Code (`File → Open Folder…`).
2. Open a terminal (`` Ctrl+` ``) and run the virtual-environment + install steps above.
3. Select the venv's Python interpreter (`Ctrl+Shift+P` → "Python: Select Interpreter").
4. Run `python app.py` in the terminal, or press `F5` with a basic Flask `launch.json`.
5. Open `http://127.0.0.1:5000` in your browser — the dashboard polls the Flask API automatically.

## How the Simulated IDS Works

1. Every 5 seconds, the **Dashboard** page calls `POST /api/simulate`.
2. `ids/simulator.py` generates a small batch of synthetic packets — almost always ordinary
   TCP/UDP/ICMP "traffic," and occasionally (~18% of ticks) a short **simulated** burst that looks
   like a port scan from one demo source IP.
3. `ids/detector.py` inserts that batch into the `traffic` table, then checks it against the
   currently **enabled** rules:
   - `NIDS-001` — many distinct destination ports from one source in a batch → **Port Scan**
   - `NIDS-002` — a spike in ICMP packets in a batch → **ICMP Anomaly / Suspicious Traffic**
   - `NIDS-003` — a spike in packets flagged `Suspicious` → **Possible Brute Force Pattern**
4. Any match inserts a new row into `alerts` and `logs`, which the frontend picks up on its next
   poll — updating the stat cards, the recent-alerts table, and the radar blips.

### Optional: Connecting a Real Snort/Suricata Sensor

`ids/detector.py` is intentionally structured as a thin analysis layer over a list of packet
dictionaries. To feed it real Suricata `eve.json` events instead of simulated ones, write a small
adapter that reads/tails the EVE JSON log, maps each `alert`/`flow` event into the same
`{timestamp, source_ip, destination_ip, protocol, source_port, destination_port, packet_size,
status}` shape used by `ids/simulator.py`, and pass that list into
`detector.analyze_and_store()`. No other file needs to change. This project ships with the
simulator only, so it runs safely on any machine with no elevated privileges.

## API Endpoints

| Method | Endpoint                     | Description                                  |
|--------|-------------------------------|-----------------------------------------------|
| GET    | `/api/dashboard`              | Stat cards + recent alerts                    |
| POST   | `/api/simulate`                | Run one simulator + detector tick             |
| GET    | `/api/traffic`                 | Traffic log (search/protocol/status filters)  |
| GET    | `/api/alerts`                  | Alerts (search/severity/date filters)         |
| PUT    | `/api/alerts/<id>/resolve`     | Mark an alert as resolved                     |
| GET    | `/api/rules`                   | List detection rules                          |
| POST   | `/api/rules`                   | Create a new detection rule                   |
| PUT    | `/api/rules/<id>`              | Update / enable / disable a rule              |
| DELETE | `/api/rules/<id>`              | Delete a rule                                 |
| GET    | `/api/analytics`               | Aggregated data for the 5 analytics charts    |
| GET    | `/api/logs`                    | System logs (search/severity filters)         |
| POST   | `/api/logs/clear`              | Clear all demo log entries                    |

All endpoints return JSON.

## Screenshots

_Add screenshots of the Dashboard, Alerts, Rules, and Analytics pages here after your first run._

## Future Improvements

- WebSocket-based push updates instead of polling
- User authentication + role-based access (analyst vs. admin)
- Exportable PDF/CSV incident reports
- Configurable simulator intensity (traffic volume, suspicious-burst frequency)
- Real Suricata `eve.json` tailer adapter shipped as an optional module

## Educational / Safe-Use Note

This project is intended for learning how intrusion detection dashboards are built. It uses a
local, offline traffic simulator by default and does not perform any real network scanning,
exploitation, or attacks. Do not point the optional integration layer at traffic you do not have
explicit authorization to monitor.
