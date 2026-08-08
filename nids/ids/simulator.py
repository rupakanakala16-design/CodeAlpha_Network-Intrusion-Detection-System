"""
ids/simulator.py
------------------
A SAFE, fully simulated network traffic generator.

This module never touches a real network interface and never sends
real packets. It only creates believable-looking demo rows so the
dashboard has fresh data to analyze. It occasionally injects a
"suspicious pattern" (e.g. many connections from one simulated IP in
a short time) purely as synthetic data for the detector to find.

This is intentionally offline / self-contained so the project runs
on any normal computer with no special privileges.
"""

import random
from datetime import datetime

PROTOCOLS = ["TCP", "UDP", "ICMP"]
COMMON_PORTS = [22, 80, 443, 21, 25, 53, 3389, 8080, 8443]

NORMAL_SOURCES = [f"192.168.1.{i}" for i in range(2, 40)] + [f"10.0.0.{i}" for i in range(2, 40)]
NORMAL_DESTS = [f"192.168.1.{i}" for i in range(50, 90)] + ["172.16.0.5", "172.16.0.9", "172.16.0.12"]

# A small pool of simulated "risky" demo source IPs used only to make
# the simulated suspicious patterns believable. These are private /
# non-routable demo addresses, not real attacker infrastructure.
SUSPICIOUS_DEMO_SOURCES = ["192.168.1.99", "10.0.0.66", "192.168.1.13"]


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def generate_normal_packet():
    """Generate one row of ordinary, benign simulated traffic."""
    return {
        "timestamp": _now(),
        "source_ip": random.choice(NORMAL_SOURCES),
        "destination_ip": random.choice(NORMAL_DESTS),
        "protocol": random.choice(PROTOCOLS),
        "source_port": random.randint(1024, 65000),
        "destination_port": random.choice(COMMON_PORTS),
        "packet_size": random.randint(64, 1500),
        "status": "Normal",
    }


def generate_batch(n=5, suspicious_chance=0.18):
    """Generate a batch of simulated packets. With small probability,
    generate a short *simulated* burst of port-scan-like traffic from
    a single demo source so the detector has something to catch.
    """
    batch = []

    if random.random() < suspicious_chance:
        # Simulated port-scan-like burst: same source, many destination ports,
        # in a tight time window. Entirely synthetic.
        src = random.choice(SUSPICIOUS_DEMO_SOURCES)
        dst = random.choice(NORMAL_DESTS)
        burst_size = random.randint(6, 12)
        for _ in range(burst_size):
            batch.append(
                {
                    "timestamp": _now(),
                    "source_ip": src,
                    "destination_ip": dst,
                    "protocol": "TCP",
                    "source_port": random.randint(1024, 65000),
                    "destination_port": random.choice(COMMON_PORTS + [3306, 5432, 6379, 27017]),
                    "packet_size": random.randint(40, 120),
                    "status": "Suspicious",
                }
            )
    else:
        for _ in range(n):
            batch.append(generate_normal_packet())

    return batch
