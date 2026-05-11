# syntax=docker/dockerfile:1.7
#
# Single-image build of the MissionDebug backend + bundled web UI.
# - Stage 1 builds the React/Vite web bundle with pnpm.
# - Stage 2 installs the FastAPI backend and serves the bundle at /.
#
# Override MD_REF at build time to pin to a specific commit, tag, or branch:
#   docker build --build-arg MD_REF=v1.5.0 .
# Default tracks main.

ARG MD_REF=main
ARG MD_REPO=https://github.com/mukul-07/missiondebug.git

# ---------- Stage 1: build the web bundle ----------
FROM node:20-slim AS web-builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@9 --activate

ARG MD_REF
ARG MD_REPO
RUN git clone "${MD_REPO}" /src && cd /src && git checkout "${MD_REF}"

WORKDIR /src/web
RUN pnpm install --frozen-lockfile || pnpm install
RUN pnpm build

# ---------- Stage 2: runtime ----------
FROM python:3.11-slim AS runtime

RUN apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/*

ARG MD_REF
ARG MD_REPO
RUN git clone "${MD_REPO}" /src && cd /src && git checkout "${MD_REF}"

WORKDIR /src/backend
RUN pip install --no-cache-dir .

COPY --from=web-builder /src/web/dist /web

RUN mkdir -p /sessions /fixtures
VOLUME ["/fixtures", "/sessions"]

ENV MD_FIXTURES=1 \
    MD_FIXTURES_DIR=/fixtures \
    MD_SESSIONS_DIR=/sessions \
    MD_WEB_DIR=/web \
    MD_DB=/sessions/missiondebug.sqlite3

EXPOSE 8000

CMD ["sh", "-c", "missiondebug-backend --host 0.0.0.0 --port 8000 --sessions-dir $MD_SESSIONS_DIR --fixtures-dir $MD_FIXTURES_DIR --web-dir $MD_WEB_DIR --db $MD_DB"]
