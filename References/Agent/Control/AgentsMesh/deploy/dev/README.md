# Dev Environment

One-click local stack: Postgres, Redis, MinIO, Traefik, Gitea, Backend, Runner, Relay, plus a local Next.js frontend with hot reload.

## Quick start

```bash
bazel run //deploy/dev:up                # docker infra + host backend/relay/runner + frontends
bazel run //deploy/dev:backend_only      # CI-style: skip frontends
bazel run //deploy/dev:clean             # stop and wipe volumes
bazel run //deploy/dev:reset_runners     # restart host runner+relay
bazel run //deploy/dev:rebuild_runner    # rebuild runner binary + restart container
```

`./dev.sh [--clean|--reset-runners|...]` still works — same flags, same behavior.

The script auto-generates `.env` with worktree-hashed ports so multiple worktrees can coexist. Actual ports are printed on startup (or read from `deploy/dev/.env`).

Test accounts seeded by `init-seed.sh`:

- **User**: `dev@agentsmesh.local` / `devpass123`
- **Admin**: `admin@agentsmesh.local` / `adminpass123`

## Contributors in mainland China

Docker image pulls through `docker.io` can be slow or unreliable from mainland China. **Configure registry mirrors once on your machine** — the Dockerfiles in this repo intentionally use canonical image names so this works transparently, with automatic fallback to Docker Hub when a mirror is unavailable.

Edit `~/.docker/daemon.json` (Docker Desktop) or `/etc/docker/daemon.json` (Linux), then restart Docker:

```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.m.daocloud.io",
    "https://dockerproxy.com"
  ]
}
```

Do **not** hard-code mirror prefixes into the Dockerfiles — mirror metadata occasionally drifts out of sync with Docker Hub, which breaks builds for *everyone* and can't be fixed without a repo change. The daemon-level config is per-machine, auto-falls-back, and doesn't affect non-China contributors.

## Logs

```bash
tail -f deploy/dev/runtime/backend/backend.log   # ibazel + backend stdout
tail -f deploy/dev/runtime/relay/relay.log
tail -f deploy/dev/runtime/runner/runner.log
tail -f deploy/dev/web.log                       # bazel next_dev (web)
docker compose logs -f postgres                  # docker infra
```

## Common issues

**Port conflicts between worktrees**: ports are derived from the worktree directory name. If you see a port clash, it usually means two worktrees hashed to the same port — rename one or set `PORT_SEED` in `.env`.

**`docker compose build` fails with `failed to resolve source metadata ... not found`**: Your Docker daemon is routing through a broken registry mirror. See the China section above — either fix the mirror list in `daemon.json` or remove it entirely to use Docker Hub directly.

**Runner can't connect to backend**: check `GRPC_PUBLIC_ENDPOINT` in the generated `.env`. For local (non-Docker) runners, this must be reachable from the host — usually `grpcs://localhost:<GRPC_PORT>`.
