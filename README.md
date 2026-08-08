# 🛡️ Network Intrusion Detection System (NIDS)

A web-based **Network Intrusion Detection System (NIDS)** developed as a cybersecurity project for monitoring network traffic, detecting suspicious activity, generating security alerts, and visualizing threats through a modern dashboard.

---

## 📌 Project Overview

The Network Intrusion Detection System monitors network traffic and analyzes it using predefined detection rules.

When suspicious activity is detected, the system generates a security alert containing information such as:

- Source IP address
- Destination IP address
- Network protocol
- Alert type
- Severity
- Timestamp
- Alert status

The project includes a **Flask web dashboard** that allows users to monitor traffic, view alerts, analyze threats, manage detection rules, and view system logs.

> **Note:** This project uses simulated/demo network traffic for safe educational purposes. It is not intended for unauthorized network scanning, exploitation, or attacks.

---

## 🎯 Objectives

- Monitor network traffic
- Detect suspicious network behavior
- Generate security alerts
- Classify threats based on severity
- Store security events
- Display alerts through a web dashboard
- Visualize threat statistics
- Provide a safe simulated IDS environment

---

## ✨ Features

### 📊 Dashboard
- System monitoring status
- Packets analyzed
- Threats detected
- Critical alerts
- Active detection rules
- Recent security alerts

### 🌐 Network Traffic Monitoring
- Source IP
- Destination IP
- Protocol
- Ports
- Packet size
- Traffic status
- Search and filtering

### 🚨 Security Alerts
- Alert type
- Severity level
- Timestamp
- Source and destination information
- Alert resolution status
- Alert filtering

### ⚙️ Detection Rules
- View detection rules
- Enable/disable rules
- Add rules
- Edit rules
- Delete rules

### 📈 Threat Analytics
Interactive charts for:

- Threats over time
- Threats by severity
- Threats by protocol
- Source IP activity
- Alert status

### 📋 System Logs
Records important events such as:

- Monitoring started
- Suspicious traffic detected
- Alerts generated
- System events

---

## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap 5
- Chart.js
- Font Awesome

### Backend
- Python
- Flask

### Database
- SQLite

### Security / Detection
- Rule-based detection
- Simulated network traffic
- IDS detection engine
- Snort/Suricata integration-ready architecture

---

## 📁 Project Structure

```text
nids/
│
├── app.py
├── README.md
├── requirements.txt
│
├── database/
│   ├── __init__.py
│   └── db.py
│
├── ids/
│   ├── __init__.py
│   ├── detector.py
│   └── simulator.py
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   ├── js/
│   │   ├── alerts.js
│   │   ├── analytics.js
│   │   ├── common.js
│   │   ├── dashboard.js
│   │   ├── logs.js
│   │   ├── rules.js
│   │   └── traffic.js
│   │
│   └── images/
│
└── templates/
    ├── base.html
    ├── index.html
    ├── about.html
    ├── alerts.html
    ├── analytics.html
    ├── logs.html
    ├── rules.html
    ├── settings.html
    └── traffic.html
