# MissionDebug demos

> Try [MissionDebug](https://github.com/mukul-07/missiondebug) in 60 seconds. No ROS install, no source checkout.

**MissionDebug is the incident memory for your robot fleet.** It captures the 60 seconds around every failure, then makes that history *queryable* — so your team stops re-solving the same incident over and over. This repo runs a self-contained demo, pre-loaded with a realistic fleet incident history, so you can see the dashboard your ops team actually buys — and scrub a real capture in the browser.

![MissionDebug fleet incident dashboard — recurrence rate, MTTR, estimated re-investigation time avoided, top recurring patterns, captures per robot](docs/screenshot-incidents.png)

## Run it

You need [Docker](https://docs.docker.com/get-docker/) with Compose.

```bash
git clone https://github.com/mukul-07/missiondebug-demos.git
cd missiondebug-demos
docker compose up
```

Open <http://localhost:8000>, then click **Incidents** in the top nav.

First run pulls a pre-built image from [GHCR](https://github.com/mukul-07/missiondebug/pkgs/container/missiondebug) (~30 seconds, multi-arch — works on amd64 and arm64). A one-shot `seed` job then populates the hub with a sample fleet incident history (it exits when done; the main service keeps running). Subsequent runs are instant.

> If `docker compose` complains about permissions, prefix with `sudo` or add your user to the `docker` group: `sudo usermod -aG docker $USER && newgrp docker`.

## What you'll see

### 🟢 The fleet incident dashboard — `Incidents` in the top nav

This is the surface a fleet-ops lead buys. The demo seeds 9 incidents across 5 robots so the dashboard renders for real:

- **MTTR** (mean time to resolution) and **resolution rate** across the fleet.
- **Recurrence rate** — how many captures are duplicates of incidents you've already seen. The hook: *"this exact failure already happened twice, and here's the fix."*
- **Top recurring patterns** by failure mode (`battery_low`, `topic_dropout`, `stall`, `path_deviation`), with a per-status breakdown.
- **Captures per day** sparkline and **captures by robot** bars.
- A **window switcher** (7d / 30d / 90d).

Switch to **30d** to see the full seeded history.

### "Has this happened before?" — open any incident

Open **`SES-203`** (a `battery_low` capture on `warehouse-bot-03`). At the top of the detail page:

- A **structured summary** of what was captured (rule, robot, subsystem, topics, payload) — generated deterministically at capture time, no LLM, works fully offline.
- **"Has this happened before?"** surfaces the most similar past incidents — `SES-201` and `SES-202`, both already **resolved**, with their **root causes shown inline** ("Battery pack cell 3 degraded…"). That's the loop that saves your team a re-investigation.
- A **resolution panel** — status (open / investigating / resolved / duplicate / won't-fix), root cause, linked ticket. Edits roll straight into the dashboard's MTTR and recurrence numbers.

> Seeded incidents carry their *metadata* but not the raw recording, so their detail page shows a clean **"recording unavailable"** state — that's intentional: at fleet scale the incident memory outlives the raw clip (retention tiers it to cold storage). To see full replay, open a fixture below.

### 📼 Scrub a real capture — the `sample_drive` and `warehouse_robot_30_topics` fixtures

The demo also ships two real MCAP captures so you can see the replay layer:

**`sample_drive` — the narrative.** 30 seconds of synthetic robot drive data with two staged failures:
- A **stall** around `t=8s` (commanded velocity high, odometry near zero).
- A **0.8m path deviation** around `t=14s`. The camera tracks render a perspective warehouse aisle; the orange dot at the bottom of frame shifts laterally during the drift so the deviation is visible from the camera POV.

**`warehouse_robot_30_topics` — the fleet-scale view.** 30 synthetic topics in the shape of a real fleet robot — diagnostics, control feedback, state machines, multi-field hardware, two `cmd_vel`-shaped control topics. Demonstrates how the UI scales to a real 30-topic robot.

On either fixture you can:
- Scrub the timeline, hit **space** to play, `←` / `→` for 100ms steps, `Shift+←` / `Shift+→` for 1s.
- **Add an annotation at the playhead** and **copy a deep-linked URL** (`?t=14.2`) to share an exact frame.
- Open the **command palette** (`⌘K` / `Ctrl+K`) to jump between sessions / robots / subsystems.
- On the 30-topic session, the **scalar chart grid** auto-renders one chart per numeric topic — filter it with the **chip-based filter** (`?q=imu,motor`).
- Use the **JSON inspector** to scrub the decoded message tree for any topic.
- **`Open in Foxglove`** hands the same MCAP to Foxglove Studio for 3D / custom layouts.

The **`Fleet`** view (top nav) shows agent health — online / stale / silent — across the seeded robots.

## What this demo is, and isn't

**It is** the hub: the fleet incident dashboard, per-incident similarity + resolution, and the replay UI — backend + web, pre-seeded with a sample incident history and two real MCAP captures.

**It isn't** the capture layer. The agent that subscribes to ROS topics and writes a new session when a detector fires only runs on a real ROS 2 system. For that, install the `.deb`s on your robot — see [the main repo](https://github.com/mukul-07/missiondebug#install-on-a-real-robot). Once an agent reports to this hub, *its* captures populate the same dashboard.

## How it fits together

| | What it does | Where it runs |
|---|---|---|
| **Agent** | Subscribes to ROS topics, keeps a 60s rolling buffer, writes MCAP + a structured summary when a detector fires, reports to the hub | Real robot only (rclpy) |
| **Hub (backend)** | Stores incidents, rolls up the fleet dashboard, runs similarity search, serves API + UI | Anywhere (this demo) |
| **Web UI** | The incident dashboard + per-incident replay (Foxglove libraries) | Browser, served by backend |

## Adding your own fixture

Drop any MCAP file into `fixtures/` and restart the container. The backend will index it and surface it in the session list.

```bash
cp /path/to/your.mcap fixtures/
docker compose restart
```

## Demonstrating fleet auth (v2 P4)

By default the demo runs in `single` mode (open routes). To show the fleet-tier auth gate, set a password before starting — the seed job uses the same secret as its Bearer token automatically:

```bash
export MD_MODE=fleet
export MD_HUB_AUTH_PASSWORD=demo
docker compose up -d --force-recreate
```

## Pinning to a specific version

By default the demo tracks `:latest` (tip of `main`). To pin to a release tag or a specific commit, edit `docker-compose.yml`:

```yaml
services:
  missiondebug:
    image: ghcr.io/mukul-07/missiondebug:1.5.0   # release tag
    # or:
    # image: ghcr.io/mukul-07/missiondebug:sha-abc1234   # immutable commit ref
```

Browse available tags: <https://github.com/mukul-07/missiondebug/pkgs/container/missiondebug>.

## Build from source (offline / airgap)

If you can't reach GHCR, build the image yourself from the main repo:

```bash
git clone https://github.com/mukul-07/missiondebug.git
cd missiondebug
docker build -t ghcr.io/mukul-07/missiondebug:latest .
```

Then `cd` back to this demos repo and `docker compose up` — compose will use the locally-built image you just tagged.

## Cleanup

```bash
docker compose down                                         # stop the containers
rm -rf sessions/                                            # remove indexed data
docker image rm ghcr.io/mukul-07/missiondebug:latest        # remove the pulled image
```

To start from a clean hub and re-seed, `rm -rf sessions/` then `docker compose up` again — the seed job re-populates it.

## Common issues

**The Incidents dashboard is empty.** The one-shot `seed` job may still be waiting for the backend, or it errored. Check its log:

```bash
docker compose logs seed
```

It prints one `HTTP 200` line per seeded incident. Re-run it on its own with `docker compose up seed`.

**Port 8000 already in use on the host.** Override via a `.env` file (works under sudo, which strips inline env vars):

```bash
cp .env.example .env             # then uncomment HOST_PORT=8080
docker compose down              # tear down any stale container
docker compose up -d --force-recreate
```

Then open <http://localhost:8080>.

**Reached a Linux VM from a different machine.** `localhost` from the host won't reach the container — you need the VM's IP:

```bash
# inside the VM
hostname -I
# → e.g. 192.168.64.7
```

Open `http://<vm-ip>:8080` from your host browser.

**`docker ps` shows the container running but no port in the PORTS column.** Compose reused a stale container created with old config. Force a rebuild:

```bash
docker compose down
docker compose up -d --force-recreate
```

**Container exits when you close the terminal.** Run detached so it survives:

```bash
docker compose up -d             # -d = detached
docker compose logs -f           # tail logs in another terminal
```

## License

MIT — same as the [main repo](https://github.com/mukul-07/missiondebug).
