# Airflow Practice

A small sandbox for learning **Apache Airflow** and practicing how to write DAGs.
It runs Airflow with Docker Compose (the official Airflow compose file), and also includes a `uv` Python environment so your editor can autocomplete and type-check DAG code.

---

## Project structure

```
airflow_practice/
├── dags/                     # DAG files. Airflow loads everything in this folder.
│   └── 1_first_dag.py        # First practice DAG (3 tasks in a chain)
├── config/                   # Optional custom airflow.cfg for the containers (empty)
├── plugins/                  # Custom Airflow plugins (empty)
├── logs/                     # Scheduler / task logs written by Airflow (generated)
├── docker-compose.yaml       # Official Airflow stack: Postgres, Redis, webserver, scheduler, worker, triggerer
├── .env                      # Local environment variables for docker compose (AIRFLOW_UID)
├── pyproject.toml / uv.lock  # Local Python env (apache-airflow) for IDE support
├── .python-version           # Python 3.12
└── main.py                   # Placeholder created by `uv init` (not used by Airflow)
```

## DAGs

### `first_dag` ([dags/1_first_dag.py](dags/1_first_dag.py))

A beginner DAG built with the TaskFlow API (`@dag` / `@task` decorators).
It has three tasks that run one after another:

```
first_task  >>  second_task  >>  third_task
```

Each task prints a message. Read the output in the task logs in the Airflow UI.

> Tip: add new practice DAGs to `dags/` with a numbered prefix (`2_...py`, `3_...py`) and give each a unique `dag_id`.

---

## How to run it (Docker, recommended)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with Docker Compose v2
- At least 4 GB of RAM for Docker (8 GB is better)

### Steps

1. **Clone the repo and enter the folder**

   ```bash
   git clone <your-repo-url> airflow_practice
   cd airflow_practice
   ```

2. **Create the folders Airflow mounts.** Git does not track empty folders, so you may need to create them:

   ```bash
   mkdir -p dags logs plugins config
   ```

3. **Create the `.env` file.** This file is not committed (see below).

   - Linux / WSL / macOS:
     ```bash
     echo "AIRFLOW_UID=$(id -u)" > .env
     ```
   - Windows (PowerShell):
     ```powershell
     "AIRFLOW_UID=50000" | Out-File -Encoding ascii .env
     ```

4. **Initialize the database and create the admin user.** Run this once:

   ```bash
   docker compose up airflow-init
   ```

   Wait until it prints that it exited with code `0`.

5. **Start Airflow**

   ```bash
   docker compose up -d
   ```

   Check that all containers are `healthy`:

   ```bash
   docker compose ps
   ```

6. **Open the UI** at <http://localhost:8080>

   - Username: `airflow`
   - Password: `airflow`

   (These are the defaults from `docker-compose.yaml`. You can override them with `_AIRFLOW_WWW_USER_USERNAME` / `_AIRFLOW_WWW_USER_PASSWORD` in `.env`.)

7. **Run the DAG**

   - Find `first_dag` in the DAG list. New DAGs start **paused** (`DAGS_ARE_PAUSED_AT_CREATION=true`), so switch the toggle on.
   - Click ▶ **Trigger DAG**.
   - Open the run, click a task, then open **Logs** to see the printed message.

   Or use the CLI:

   ```bash
   docker compose exec airflow-scheduler airflow dags list
   docker compose exec airflow-scheduler airflow dags test first_dag
   ```

8. **Stop Airflow**

   ```bash
   docker compose down          # stop the containers
   docker compose down -v       # stop and also delete the database volume (full reset)
   ```

### Optional: Flower (Celery monitoring)

```bash
docker compose --profile flower up -d
```

Then open <http://localhost:5555>.

---

## Local Python environment (IDE support)

`pyproject.toml` installs `apache-airflow` locally with [uv](https://docs.astral.sh/uv/). This lets VS Code resolve `from airflow.decorators import dag, task` and gives you autocomplete.

```bash
uv sync                      # creates .venv and installs dependencies
```

Then select `.venv` as the Python interpreter in your editor.

> **Version note:** the local env installs **Airflow 3.x** (`apache-airflow>=3.1.7`), but the Docker image is **Airflow 2.10.4** (`apache/airflow:2.10.4`). The DAG in this repo works on both. If you use features that only exist in Airflow 3 (for example `from airflow.sdk import dag, task`), update the image tag in `docker-compose.yaml` (or set `AIRFLOW_IMAGE_NAME` in `.env`) and switch to the Airflow 3 compose file.

### Running Airflow without Docker (optional)

Airflow does not run natively on Windows. Use **WSL2**, Linux, or macOS:

```bash
export AIRFLOW_HOME=$(pwd)
uv run airflow standalone
```

`airflow standalone` creates `airflow.cfg`, `airflow.db`, and `simple_auth_manager_passwords.json.generated` (holds the admin password) in `AIRFLOW_HOME`. These files are machine-specific and secret, so **do not commit them**.

---

## What must NOT be pushed to GitHub

| File / folder | Why |
|---|---|
| `.env` | Local environment settings. Commit a `.env.example` instead if you want to document the variables. |
| `airflow.cfg` (root) | Generated by a local Airflow run. It contains **`fernet_key`, webserver `secret_key`, and `jwt_secret`**, plus absolute paths from your machine. |
| `simple_auth_manager_passwords.json.generated` | Contains the **admin login password** for local Airflow 3. |
| `airflow.db`, `*.db` | Local SQLite metadata database. |
| `logs/` | Runtime logs. They are large and change constantly. |
| `.venv/` | Local virtual environment. Recreate it with `uv sync`. |
| `__pycache__/`, `*.pyc` | Python bytecode cache. |
| `C:UsersAsusDocumentsairflow_practice/` | Empty folder created by mistake from a badly escaped Windows path. Delete it. |
| `airflow-webserver.pid`, `standalone_admin_password.txt`, `webserver_config.py` | Files local Airflow may create. |

Add this to `.gitignore` (on top of the existing Python rules):

```gitignore
# Secrets / local config
.env
airflow.cfg
simple_auth_manager_passwords.json.generated
standalone_admin_password.txt
webserver_config.py

# Airflow runtime files
logs/
*.db
*.pid

# Accidental Windows-path folder
C:*/
```

**Safe to commit:** `dags/`, `plugins/`, `config/` (unless you put secrets there), `docker-compose.yaml`, `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `README.md`.

> The credentials in `docker-compose.yaml` (`airflow/airflow` for Postgres and the UI) are the public defaults from the official Airflow file. They are fine for local practice, but **never use them on a server that others can reach**.

If any secret file has already been committed, removing it in a later commit is not enough. Remove it from the index (`git rm --cached <file>`) and **create new keys** (`fernet_key`, `secret_key`, `jwt_secret`) before you push.

---

## Useful commands

```bash
docker compose logs -f airflow-scheduler                   # follow scheduler logs
docker compose exec airflow-scheduler airflow dags list-import-errors   # find broken DAG files
docker compose exec airflow-scheduler airflow tasks test first_dag first_task 2024-01-01
docker compose restart                                     # restart all services
```

## References

- [Airflow docs](https://airflow.apache.org/docs/apache-airflow/stable/index.html)
- [Running Airflow in Docker](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)
- [TaskFlow API tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html)
