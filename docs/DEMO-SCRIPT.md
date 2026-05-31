# MissionDebug — demo script

A repeatable 5-minute walkthrough for showing MissionDebug to a prospect.
Lead with the **fleet incident dashboard** (what gets bought), then drill
into one incident to prove the loop. Replay is shown last, as supporting
evidence — not the headline.

## Setup (once, before the call)

```bash
git clone https://github.com/mukul-07/missiondebug-demos.git
cd missiondebug-demos
docker compose up -d            # pulls the image, auto-seeds the incident corpus
```

Open `http://localhost:8000` (or `http://<host>:8080` if `HOST_PORT` is set) →
**Incidents** → switch to **30d**. Confirm the dashboard is populated
(13 captures, ~38% recurrence). If it's empty, the seed job is still
catching up — `docker compose logs seed` shows its progress.

> Reset between demos: `docker compose down && rm -rf sessions/ && docker compose up -d`
> gives you an identical clean dashboard every time.

---

## The walk (≈90 seconds to the hook)

### 1. Open on the dashboard — name the pain
> "Every tool tells you *what* broke. The expensive problem is that fleets
> re-solve the *same* incident over and over because nobody remembers it
> broke this way before."

Point at **Recurrence rate (~38%)**:
> "More than a third of this fleet's incidents last month were repeats of
> something they'd already diagnosed."

### 2. Make the ROI their number
Scroll to **Estimated value — repeat-incident time avoided**. The inputs are
editable — **type the prospect's own numbers**:
- `hrs / investigation` → ask "how long does a typical incident take your team to chase down?" Put their number in.
- `$ / hr` → their loaded engineering cost.

> "At your team's cost, that's $X every month spent re-investigating things
> you'd already solved."

A figure they typed themselves lands harder than one you assert.

### 3. Show the failure modes
**Top recurring patterns** ranks incidents by failure mode (`battery_low`,
`stall`, …) with how many recurred.
> "These are the patterns burning the most time. Let's open one."

### 4. Prove the loop — open a duplicate
Click into a `battery_low` incident (or open **SES-203** directly). On the
detail page, point at **"Has this happened before?"**:
> "The moment this incident fired, the engineer sees it's happened twice
> before — *and the root cause from last time, right here*: 'Battery pack
> cell 3 degraded, replaced module.' No re-investigation. That's the memory."

### 5. Land it
> "MissionDebug is the incident-memory layer for your fleet. The 60-second
> recording is how each capture works — this dashboard is what stops your
> team paying the same debugging cost twice."

---

## Supporting evidence (if they want to see the capture itself)

- Open the **`sample_drive`** fixture (Sessions list) → scrub the timeline,
  hit space to play. Show the camera track and the path-deviation at ~14s.
- Open **`warehouse_robot_30_topics`** → the scalar-chart grid auto-renders a
  chart per numeric topic; filter with the chip box (`imu`, `motor`). This is
  the "it scales to a real 30-70-topic robot" point.
- **"Open in Foxglove"** hands the MCAP to Foxglove Studio for 3D / custom
  layouts — the standards story (MCAP + Foxglove native).

> Note: the seeded incidents are metadata-only, so their detail page shows a
> clean **"recording unavailable"** state. That's intentional and worth
> calling out: *the incident memory outlives the raw clip* — retention tiers
> recordings to cold storage, but the queryable history stays. It's a feature,
> not a gap.

---

## Scope — what to say it is, and isn't

- **Is:** the post-incident replay + incident-memory layer of the robotics ops
  stack, at fleet scale. Self-hostable, MCAP + Foxglove native, air-gap
  friendly (similarity + summaries work fully offline).
- **Isn't:** a live-ops / teleop tool, and not the capture layer in this demo —
  the agent that writes captures runs on a real ROS 2 robot. Point them to the
  main repo's install path for that. Once an agent reports in, *its* captures
  populate this same dashboard.

## One-line positioning

> "MissionDebug is the system that remembers every incident your fleet has
> ever had, so your team stops re-solving the same problems."
