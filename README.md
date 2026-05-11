# MissionDebug demos

> Try [MissionDebug](https://github.com/mukul-07/missiondebug) in 60 seconds. No ROS install, no source checkout.

MissionDebug captures the 60 seconds before a ROS 2 robot failure and lets you scrub it in the browser. This repo runs a self-contained demo of the **replay** side against a pre-recorded session, so you can see the product before installing on a real robot.

## Run it

You need [Docker](https://docs.docker.com/get-docker/) with Compose.

```bash
git clone https://github.com/mukul-07/missiondebug-demos.git
cd missiondebug-demos
docker compose up
```

Open <http://localhost:8000>.

First run builds the image (~2-3 minutes — it clones the main repo, builds the web bundle with pnpm, installs the Python backend). Subsequent runs are instant.

> **Port already in use?** Override the host port with `HOST_PORT=8080 docker compose up`, then open <http://localhost:8080>.

## What you'll see

The session list will already contain a `sample_drive` fixture — click it.

- 30 seconds of synthetic robot drive data
- A stall around `t=8s` (commanded velocity high, odometry near zero)
- A 0.8m path deviation around `t=14s` (orange dot drifts off the green planned path)

Scrub the timeline. Hit space to play. Hit `←` / `→` for 100ms steps. Add an annotation at the playhead. Copy a deep-linked URL (`?t=14.2`) to share a specific frame with a teammate.

## What this demo is, and isn't

**It is** the replay layer of MissionDebug — backend + web UI, against pre-recorded MCAP fixtures.

**It isn't** the capture layer. The agent that subscribes to ROS topics and writes new sessions when detectors fire only runs on a real ROS 2 system. For that, install the `.deb`s on your robot — see [the main repo](https://github.com/mukul-07/missiondebug#install-on-a-real-robot).

## How it fits together

| | What it does | Where it runs |
|---|---|---|
| **Agent** | Subscribes to ROS topics, keeps a 60s rolling buffer, writes MCAP files on detector fire | Real robot only (rclpy) |
| **Backend** | Indexes MCAP files, serves API + UI, handles disk retention | Anywhere (this demo) |
| **Web UI** | Scrubs the MCAP in the browser using Foxglove libraries | Browser, served by backend |

## Adding your own fixture

Drop any MCAP file into `fixtures/` and restart the container. The backend will index it and surface it in the session list.

```bash
cp /path/to/your.mcap fixtures/
docker compose restart
```

## Pinning to a specific version

By default the demo tracks `main` of the upstream repo. To pin to a tag or commit:

```bash
docker compose build --build-arg MD_REF=v1.5.0
docker compose up
```

## Cleanup

```bash
docker compose down              # stop the container
rm -rf sessions/                 # remove indexed data
docker image rm missiondebug-demo  # remove the built image
```

## License

MIT — same as the [main repo](https://github.com/mukul-07/missiondebug).
