# Docker Commands Reference — For This App

This guide covers **only the Docker / Docker Compose commands needed to build
and run the `webserver` app** (a Flask todo-list API with a static frontend,
backed by SQLite). Every command below is shown first, followed by a
**flag-by-flag explanation**.

> **Tooling in use:** Docker Engine 29.x + Docker Compose v5.x (`docker compose`).
> The app listens on port `5000` and persists data to `./database.db` on the host.

---

## Quick Start (recommended — Docker Compose)

```bash
# 1. Build the image (first run only, or whenever deps change)
docker compose build

# 2. Start the app in the background
docker compose up -d

# 3. (Optional) watch the log output live
docker compose logs -f

# 4. (Optional) open a shell inside the running container
docker compose exec web sh

# 5. When done, stop & remove the container (keeps your database)
docker compose down
```

Open your browser at **http://localhost:5000** — the frontend loads and the
`/api/todos` endpoints respond.

---

## Option A — Run with Docker Compose

The project ships a `docker-compose.yml` that defines a single service called
`web`. Compose handles building, networking, and port mapping automatically.

### `docker compose build`

Builds the Docker image for the `web` service using the `Dockerfile`.

| Token          | Meaning |
|----------------|---------|
| `docker compose` | Compose CLI plugin (note: **no hyphen** in modern Docker). |
| `build`        | Build images for the services defined in `docker-compose.yml`. |
| *(no args)*    | Builds **all** services. You can scope it: `docker compose build web`. |

> **Flags you may add:**<br>
> `--build-arg KEY=VAL` — pass build args to the Dockerfile.<br>
> `--no-cache` — ignore the build cache and rebuild every layer from scratch.<br>
> `--no-rm` — keep intermediate builder containers (default: remove them).<br>
> `--pull` — always attempt to pull a newer base image (`python:3.12-slim`).

### `docker compose up -d`

Builds (if needed) **and starts** the containers.

| Token          | Meaning |
|----------------|---------|
| `up`           | Create and start all (or specified) service containers. |
| `-d`           | **Detach** — run containers in the background and return to your shell. Without `-d`, logs stream in the foreground. |

> **Flags you may add:**<br>
> `--build` — build images before starting (useful to force a fresh build).<br>
> `--force-recreate` — recreate containers even if the image hasn't changed.<br>
> `--remove-orphans` — remove containers for services no longer in the compose file.

### `docker compose logs -f`

Shows container log output.

| Token   | Meaning |
|---------|---------|
| `logs`  | Print the stdout/stderr logs of the service containers. |
| `-f`    | **Follow** — keep streaming new log lines (like `tail -f`). |
| `web` *(optional)* | Restrict output to the `web` service only. |

> **Flags you may add:**<br>
> `--tail N` — show only the last N lines of logs.

### `docker compose exec web sh`

Open an interactive shell inside the running `web` container.

| Token       | Meaning |
|-------------|---------|
| `exec`      | Run a command in an **already-running** container. |
| `web`       | The **service name** (defined in `docker-compose.yml`). |
| `sh`        | The command to run — here, a non-interactive shell. Because `python:3.12-slim` (Debian) includes `sh` but not `bash`, use `sh`. |

> **Flags you may add:**<br>
> `-it` — combine **interactive** (`-i`) + **tty** (`-t`) for a usable terminal. With Compose the `-i` is implicit; add `-T` to disable pseudo-tty allocation.

### `docker compose down`

Stops and removes the containers **and** the Compose-managed network.

| Token  | Meaning |
|--------|---------|
| `down` | Stop running containers and remove them, plus the app network. |

> **Flags you may add:**<br>
> `-v` — also remove **named volumes**. *(Note: this app uses a bind mount — `./database.db` — which lives on the host, so Compose will **not** delete `database.db` itself; you'd remove it manually with `rm`.)*<br>
> `--rmi all` — also remove the built images.<br>
> `-t N` — set the stop timeout in seconds (default 10).

### `docker compose run --rm web sh`

Run a **one-off** command in a **new** container.

| Token     | Meaning |
|-----------|---------|
| `run`     | Create and start a one-off container (separate lifecycle from `up`). |
| `--rm`    | Automatically remove the container when the command exits. |
| `web`     | The service to use as the base (its image + config). |
| `sh`      | The command to run inside that one-off container. |

---

## Option B — Run with plain `docker`

You can also build and run the app without Compose. This is useful for quick
local testing or when you want full control over flags.

### `docker build -t webserver .`

Build the image from the `Dockerfile` in the current directory.

| Token         | Meaning |
|---------------|---------|
| `docker build` | Build an image from a Dockerfile. |
| `-t webserver` | **Tag** (name) the resulting image `webserver` (defaults to `latest`). Use `webserver:latest` or add `:1.0`. |
| `.`           | The **build context** — the current directory. Docker sends everything in this dir (except `.dockerignore` entries) as the build context. |

> **Flags you may add:**<br>
> `--no-cache` — rebuild every layer; ignore previously cached layers.

### `docker run -d --rm -p 5000:5000 --name webserver webserver`

Create and start a container from the image.

| Token                | Meaning |
|----------------------|---------|
| `docker run`         | Create **and start** a container from an image (combines `create` + `start`). |
| `-d`                 | **Detach** — run in the background; print the container ID and return. |
| `--rm`               | **Auto-remove** the container when it stops (handy for ephemeral test runs). |
| `-p 5000:5000`       | **Publish** port — map host port `5000` → container port `5000`. The app's `app.run(port=5000)` binds inside the container, so the right side must be `5000`. The left side can differ (e.g. `-p 8080:5000`) to avoid host conflicts. |
| `--name webserver`   | Give the container a friendly, memorable name. Without it Docker picks a random one. |
| `webserver`          | The **image** to run (as tagged by `docker build -t webserver`). |

> **Flags you may add:**<br>
> `-e PORT=5000` — set an environment variable (`app.py` reads `os.environ.get('PORT', 5000)`).<br>
> `-v $(pwd)/database.db:/app/database.db` — **bind mount** the host DB — equivalent to the Compose volume (so data survives container removal).<br>
> `--network host` — use the host's network stack directly (Linux only; no port mapping needed, but less isolated).

### `docker ps` / `docker ps -a`

List containers.

| Token   | Meaning |
|---------|---------|
| `ps`    | List **running** containers. |
| `-a`    | **All** containers — include stopped ones. |

### `docker stop <name>` / `docker start <name>`

Stop / start an existing (possibly stopped) container.

| Token   | Meaning |
|---------|---------|
| `stop`  | Gracefully stop a running container (sends `SIGTERM`, then `SIGKILL` after a timeout). |
| `start` | Start a previously created + stopped container. |
| `<name>`| The container name or ID (e.g. `webserver`). |

### `docker rm <name>`

Remove a **stopped** container.

| Token     | Meaning |
|-----------|---------|
| `rm`      | Remove one or more stopped containers. |
| `-f` *(optional)* | **Force** — remove even if currently running (stops it first). |
| `<name>`  | The container name or ID. |

> Because `--rm` was used with `run`, the container is removed automatically on
> exit — you rarely need `rm` by hand in that case.

### `docker logs <name>` / `docker logs -f <name>`

Show container logs.

| Token       | Meaning |
|-------------|---------|
| `logs`      | Print the captured stdout/stderr of the container. |
| `-f`        | **Follow** — stream new log lines as they're produced. |
| `--tail N`  | *(optional)* show only the last N lines. |
| `<name>`    | The container name or ID. |

### `docker exec -it <name> sh`

Run a command in a **running** container.

| Token       | Meaning |
|-------------|---------|
| `exec`      | Execute a command **inside an already-running container**. |
| `-i`        | **Interactive** — keep STDIN open so you can type input. |
| `-t`        | **TTY** — allocate a pseudo-terminal (gives you a proper shell prompt). `-it` together → interactive shell. |
| `<name>`    | The running container name or ID (e.g. `webserver`). |
| `sh`        | The command to run (`sh` is present on `python:3.12-slim`; use `bash` only on images that include it). |

---

## What This App's Docker Files Do

### `Dockerfile` — the build recipe

```dockerfile
FROM python:3.12-slim            # base image: Python 3.12 on a minimal Debian
WORKDIR /app                    # create + cd into /app inside the container
COPY requirements.txt .         # copy ONLY requirements first (for layer caching)
RUN pip install --no-cache-dir -r requirements.txt   # install deps w/o caching pip downloads
COPY app.py .                   # copy the Flask app
COPY static/ static/            # copy the frontend assets
CMD python app.py               # default command: start the Flask server
```

### `docker-compose.yml` — the service definition

```yaml
services:
  web:
    build: .                       # build image from ./Dockerfile
    ports:
      - "5000:5000"                # host:5000 -> container:5000
    volumes:
      - ./database.db:/app/database.db  # bind-mount host DB into the container
    restart: unless-stopped        # auto-restart the container if it exits/crashes
```

### `.dockerignore` — keeps the build lean

Excludes `__pycache__`, `*.pyc`, `*.pyo`, `*.db`, `.git`, `.gitignore`,
`.DS_Store`, and `docker-compose.yml` from the **build context** — so those
files are never sent to the daemon or copied into the image. This makes builds
faster and the image smaller.

---

## Typical Workflow

```bash
# First run: build + start
docker compose up -d --build

# Make a code change to app.py or static/ ... then restart the service
docker compose up -d --build        # rebuild & restart with latest code

# Inspect / debug
docker compose exec web sh          # shell into the container
docker compose logs -f              # watch logs live

# Tear down (containers + network; database.db on host is preserved)
docker compose down

# To also remove the local SQLite DB file:
rm -f database.db

# To fully wipe everything (images + containers + volumes):
docker compose down --rmi all -v
```

---

## Common Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| `port is already allocated` | Something else uses host port 5000. | Use `-p 8080:5000` (Compose: override `ports`) or free the port. |
| Changes to `app.py` not reflected | You ran without `--build`. | Rebuild: `docker compose up -d --build`. |
| `database.db` not persisting | The bind mount path is wrong / host file deleted. | Keep `./database.db` next to `docker-compose.yml`. |
| Database not created on first start | Container never ran `app.py`. | Run once: `docker compose up` then `docker compose exec web python app.py` (init happens in `__main__`). |
