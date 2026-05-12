# MissionDebug demos

> Try [MissionDebug](https://github.com/mukul-07/missiondebug) in 60 seconds. No ROS install, no source checkout.

MissionDebug captures the 60 seconds before a ROS 2 robot failure and lets you scrub it in the browser. This repo runs a self-contained demo of the **replay** side against a pre-recorded session, so you can see the product before installing on a real robot.

![MissionDebug replay demo](docs/demo.gif)

## Run it

You need [Docker](https://docs.docker.com/get-docker/) with Compose.

```bash
git clone https://github.com/mukul-07/missiondebug-demos.git
cd missiondebug-demos
docker compose up
```

Open <http://localhost:8000>.

First run pulls a pre-built image from [GHCR](https://github.com/mukul-07/missiondebug/pkgs/container/missiondebug) (~30 seconds, multi-arch — works on amd64 and arm64). Subsequent runs are instant.

> If `docker compose` complains about permissions, prefix with `sudo` or add your user to the `docker` group: `sudo usermod -aG docker $USER && newgrp docker`.

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
docker compose down                                         # stop the container
rm -rf sessions/                                            # remove indexed data
docker image rm ghcr.io/mukul-07/missiondebug:latest        # remove the pulled image
```

## Common issues

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
docker ps                        # PORTS column should show 0.0.0.0:8080->8000/tcp
```

**Container exits when you close the terminal.** Run detached so it survives:

```bash
docker compose up -d             # -d = detached
docker compose logs -f           # tail logs in another terminal
```

## License

MIT — same as the [main repo](https://github.com/mukul-07/missiondebug).
