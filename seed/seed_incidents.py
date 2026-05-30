#!/usr/bin/env python3
"""Auto-seed the demo hub with a realistic fleet incident corpus.

Run as a one-shot service by docker-compose so `docker compose up` lands
on a *populated* fleet incident dashboard — MTTR, recurrence rate, top
patterns, "this happened before" with resolutions — instead of an empty
day-one hub. That dashboard is the buyable surface; the demo should show
it working, not just the replay layer.

Pure stdlib (urllib) so it runs in a plain python image with zero pip
installs. Idempotent: ingest + resolution use stable session ids, so a
re-run (docker compose up again) just overwrites the same rows.

Posts directly to the hub's ingest endpoint with explicit summaries —
the same shape the agent's structured summarizer produces — so TF-IDF
similarity clusters the incidents the way a real fleet would.
"""

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

HUB = os.environ.get("HUB", "http://missiondebug:8000").rstrip("/")
TOKEN = (
    os.environ.get("MD_HUB_AUTH_TOKEN")
    or os.environ.get("MD_HUB_AUTH_PASSWORD")
    or ""
)


def _request(path, body=None, method="GET"):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(HUB + path, data=data, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status


def wait_for_hub(timeout=120):
    """Poll /healthz until the backend answers, or give up after `timeout`."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if _request("/healthz") == 200:
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


NOW = time.time()


def ingest(sid, robot, subsystem, days_ago, rule, dur_s, size, topics_h):
    started_s = NOW - days_ago * 86400
    started_ms = int(started_s * 1000)
    dur_ms = dur_s * 1000
    started_str = datetime.fromtimestamp(started_s, tz=timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )
    topics = [t.split(" (")[0] for t in topics_h.split(", ")]
    n = len(topics)
    size_kb = f"{size / 1024:.1f} KB"
    summary = (
        f"Auto-triggered by rule '{rule}' at {started_str} on {robot} "
        f"(subsystem: {subsystem}). Captured {dur_s}.0s across {n} topics: "
        f"{topics_h}. Total payload: {size_kb}."
    )
    body = {
        "session_id": sid,
        "robot_id": robot,
        "started_at": started_ms,
        "ended_at": started_ms + dur_ms,
        "duration_ms": dur_ms,
        "label": f"anomaly:{rule}",
        "topics": topics,
        "mcap_size_bytes": size,
        # No real bytes behind this — the detail page renders its clean
        # "recording unavailable" state, which is itself part of the pitch
        # (incident memory outlives the recording).
        "mcap_url": f"http://agent.invalid/mcap?session={sid}",
        "subsystem": subsystem,
        "summary": summary,
    }
    code = _request("/api/v1/sessions/ingest", body, method="POST")
    print(f"  ingest  {sid:8} {robot:18} {rule:14} -> HTTP {code}", flush=True)


def resolve(sid, status, root_cause="", ticket="", dup=""):
    body = {"status": status, "edited_by": "demo-seed"}
    if root_cause:
        body["root_cause"] = root_cause
    if ticket:
        body["linked_ticket"] = ticket
    if dup:
        body["duplicate_of"] = dup
    code = _request(f"/api/v2/sessions/{sid}/resolution", body, method="PUT")
    print(f"  resolve {sid:8} {status:13} -> HTTP {code}", flush=True)


def heartbeat(robot):
    code = _request(
        "/api/v1/agents/heartbeat",
        {"robot_id": robot, "agent_version": "2.0.0", "buffer_size": 600},
        method="POST",
    )
    print(f"  heartbeat {robot:18} -> HTTP {code}", flush=True)


def main():
    print(f"[demo-seed] waiting for hub at {HUB} ...", flush=True)
    if not wait_for_hub():
        print("[demo-seed] hub never became healthy; giving up.", flush=True)
        return
    print("[demo-seed] hub is up. Seeding incident corpus.", flush=True)

    # Cluster A — battery_low (power). SES-203 is a recurrence of SES-201.
    ingest("SES-201", "warehouse-bot-03", "power", 12, "battery_low", 60, 243712,
           "/battery_state (320 msgs), /cmd_vel (180 msgs), /diagnostics (45 msgs), /odom (600 msgs)")
    ingest("SES-202", "warehouse-bot-07", "power", 9, "battery_low", 60, 251904,
           "/battery_state (318 msgs), /cmd_vel (176 msgs), /diagnostics (44 msgs), /odom (590 msgs)")
    ingest("SES-203", "warehouse-bot-03", "power", 2, "battery_low", 60, 240128,
           "/battery_state (322 msgs), /cmd_vel (181 msgs), /diagnostics (46 msgs), /odom (604 msgs)")

    # Cluster B — topic_dropout (perception).
    ingest("SES-210", "warehouse-bot-05", "perception", 14, "topic_dropout", 60, 512000,
           "/scan (290 msgs), /odom (600 msgs), /tf (1200 msgs), /camera/image_raw (60 msgs)")
    ingest("SES-211", "warehouse-bot-07", "perception", 6, "topic_dropout", 60, 498688,
           "/scan (286 msgs), /odom (598 msgs), /tf (1190 msgs), /camera/image_raw (59 msgs)")

    # Cluster C — stall (navigation).
    ingest("SES-220", "warehouse-bot-01", "navigation", 11, "stall", 60, 198656,
           "/cmd_vel (200 msgs), /odom (600 msgs), /scan (290 msgs), /move_base/status (30 msgs)")
    ingest("SES-221", "warehouse-bot-05", "navigation", 4, "stall", 60, 201728,
           "/cmd_vel (198 msgs), /odom (602 msgs), /scan (288 msgs), /move_base/status (31 msgs)")

    # Cluster D — path_deviation (navigation).
    ingest("SES-230", "warehouse-bot-02", "navigation", 7, "path_deviation", 60, 187392,
           "/cmd_vel (205 msgs), /odom (601 msgs), /plan (40 msgs), /tf (1205 msgs)")

    # A still-open manual capture.
    ingest("SES-240", "warehouse-bot-01", "navigation", 1, "manual", 45, 176128,
           "/cmd_vel (150 msgs), /odom (450 msgs), /scan (220 msgs)")

    resolve("SES-201", "resolved",
            "Battery pack cell 3 degraded; replaced module and recalibrated SoC curve", "JIRA-4471")
    resolve("SES-202", "resolved",
            "Low-charge cutoff misconfigured at 15%; raised fleet default to 25%", "JIRA-4480")
    resolve("SES-203", "duplicate", dup="SES-201")
    resolve("SES-210", "investigating")
    resolve("SES-220", "resolved",
            "Costmap inflation radius too large near racking; tuned per-aisle", "LINEAR-882")
    resolve("SES-230", "wont_fix",
            "Known GPS multipath in aisle 7; operational workaround documented")
    # SES-211, SES-221, SES-240 intentionally left open.

    for robot in ("warehouse-bot-01", "warehouse-bot-02", "warehouse-bot-03",
                  "warehouse-bot-05", "warehouse-bot-07"):
        heartbeat(robot)

    print("[demo-seed] done. Open the Incidents dashboard.", flush=True)


if __name__ == "__main__":
    main()
