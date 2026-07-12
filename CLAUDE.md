# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Wicked Jukebox is a multi-channel music jukebox backend (v3 rewrite, package version `3.0.0a7`). A "channel" is a long-running process that plays music through a pluggable player backend (currently MPD), picking songs via configurable autoplay/queue strategies and committing playback statistics to a MariaDB/MySQL database. Targets Python 3.13 (`python_requires>=3.13`) and is pinned to **SQLAlchemy < 2.0**.

## Development Setup

The canonical environment is bootstrapped with [fabric](http://www.fabfile.org) (tasks live in `fabfile.py`). It creates a virtualenv at `./env`, so most tools are invoked as `./env/bin/<tool>`.

```bash
fab develop          # full setup: venv, pip install -e .[dev,test], DB container, dev seed, pre-commit, sampledata
fab run-db-container # start ephemeral MariaDB container + rewrite *.ini with the dynamic DB port + alembic upgrade head
fab build_mpd        # build the wickedjukebox/mpd docker image (Dockerfile)
fab run_mpd <mp3_path> [--port=6600]  # run MPD in an ephemeral container for testing
```

`db_container.sh` runs a throwaway MariaDB 10 container (db/user/pass all `jukebox`, root `rootpw`) on a **dynamic host port** — `fab run-db-container` discovers that port and substitutes it into `alembic.ini` and `.wicked/wickedjukebox/config.ini`. Data is **not** persistent. `makemusic.bash` uses ffmpeg to generate `sampledata/` (sine-wave MP3s with metadata) for testing.

## Configuration

Config is loaded via [config-resolver](https://config-resolver.readthedocs.io) under app `wickedjukebox`, group `wicked`, filename `config.ini` — i.e. the active file is typically `.wicked/wickedjukebox/config.ini` (or XDG paths). Copy from `config.ini.dist`. The database DSN lives in `[core] dsn=`. Alembic is configured separately via `alembic.ini` (copy from `alembic.ini.dist`); its `sqlalchemy.url` is read from the same config in `alembic/env.py`.

Component behaviour is selected per channel via ini sections `[channel:<channel-name>:<component>]`, each with a `type` option (see "Architecture"). A `type = null` disables that component.

## Running the Application

Two console entry points are installed (see `setup.py`):

```bash
run-channel -c <channel-name> [-v]   # run a channel's playback loop (-v repeatable for verbosity)
jukebox-admin rescan <path>          # scan a directory tree for .mp3 files and import metadata into the DB
```

## Testing

Tests **require a running MariaDB with migrations applied** — `conftest.py` reads the DSN from the resolved config, runs `alembic upgrade head`, and wraps each test in a transaction that is rolled back (fixtures: `dbsession`, `default_data`).

```bash
fab test                  # spin up DB container, then run pytest with the configured DSN
fab test --cover          # add coverage (term-missing + coverage.xml, branch coverage)
fab test --lf             # only re-run last-failed
fab test --autorun        # re-run on file changes via entr
./env/bin/pytest test/test_components.py::test_name   # run a single test (DB must already be up & migrated)
```

CI (`.github/workflows/ci.yaml`, Python 3.13) runs `pre-commit run --all`, then provisions MariaDB, configures the ini files, runs `alembic upgrade head`, and runs `pytest`.

## Linting & Formatting

`pre-commit` runs **black** and **isort** (both `line-length = 80`, isort uses the black profile) plus check-yaml and trailing-whitespace. `pylint` and `flake8` (max-line-length 80) are also used; VS Code is configured for `typeCheckingMode: strict`. Legacy files matching `wickedjukebox/demon*` are excluded from pre-commit.

## Architecture

### The channel tick loop (`channel.py`)
`Channel.run()` loops calling `tick()` every `tick_interval_s` seconds. Each tick: enqueues a next song if the player is empty (`queue.dequeue()` else `random.pick()`), starts playback if autoplay is on, relays IPC state (current song, progress) and handles SKIP commands, injects a jingle once `songs_since_last_jingle` exceeds the jingle interval, and commits the current song to history (`ChannelStat`) when the player is nearly out of music. The loop swallows exceptions per-tick so a single failure never kills the channel.

### Pluggable components (`component/`)
A `Channel` is composed of five swappable components, each an `ABC` with `Null*` no-op implementations:

| Component | Interface | Implementations (config `type`) |
|-----------|-----------|----------------------------------|
| Player    | `AbstractPlayer` (`player.py`) | `mpd` (`MpdPlayer`), `null` |
| Autoplay  | `AbstractRandom` (`random.py`) | `smart_prefetch`, `allfiles_random`, `null` |
| IPC       | `AbstractIPC` (`ipc.py`)       | `db`, `fs`, `null` |
| Queue     | `AbstractQueue` (`queue.py`)   | `db` (`DatabaseQueue`), `null` |
| Jingle    | `AbstractJingle` (`jingle.py`) | `fs` (`FileBasedJingles`), `null` |

Components are wired together by **`make_component_getter`** in `component/__init__.py`: it maps a config `type` string to a class, instantiates it, then calls `instance.configure(...)` with the keys declared in that class's `CONFIG_KEYS`. `cli/run_channel.py:make_channel` calls the resulting `get_player/get_autoplay/get_ipc/get_queue/get_jingle` factories to build a `Channel`. To add a new implementation: subclass the relevant `Abstract*`, declare `CONFIG_KEYS`, and register it in the `clsmap` of the matching getter.

### Config abstraction (`config.py`)
`ConfigKeys` enumerates every config value and where it lives via `ConfigOption(scope, section, subsection)`. `ConfigScope.CORE` → `[core]`; `ConfigScope.CHANNEL` → `[channel:<channel-name>:<section>]`. Use `Config.get(...)` for single values and `Config.dictify(...)` to pull a whole component section (validates against expected keys, raises `ConfigError` on mismatch).

### Data model & migrations (`model/db/`)
SQLAlchemy declarative models split by domain (`library`, `playback`, `stats`, `auth`, `settings`, `lastfm`, `events`, `logging`, `webui`). The shared `Base`, `Session` (scoped session), and `connect(dsn)` live in `model/db/sameta.py`; entry points call `connect(dsn)` once at startup. `model/db/__init__.py` imports every module so **Alembic autogenerate can see the full schema** — any new model module must be added there. Migrations live in `alembic/versions/`; `alembic/env.py` binds `target_metadata = sameta.Base.metadata`. Models commonly expose `by_name`/`by_filename`/`by_song` classmethod finders.

### Smart song selection (`core/smartfind.py`)
`smart_prefetch` autoplay scores candidate songs in SQL, weighting last-played recency, song age, never-played status, randomness, and aggregated user ratings (love/hate "standings" from users that recently showed "proof of life"). Weights and cutoffs come from the `[channel:*:autoplay]` config (`weight_*`, `max_duration`, `proofoflife_timeout`). `random.py` runs prefetch on a background thread.

### Smart-playlist parser (`smartplaylist/parser.py`)
A `ply` (lex/yacc) grammar that compiles a human-friendly filter string (e.g. `artist contains "tool" and not genre is "pop"`) into a SQLAlchemy query for dynamic playlists.

### Audio scanner (`scanner.py`)
Walks a path for `.mp3` files (`SUPPORTED_FILETYPES`), reads tags via `mutagen` into `Song` rows, and upserts them (`session.merge`). Invoked through `jukebox-admin rescan`.

## Notes

- `sandbox/` contains throwaway GStreamer experiments — not part of the application.
- Full prose docs are in `doc/` (Sphinx) and published at https://thewickednet.github.io/wickedjukebox/.
- `TODO.md` tracks known rough edges (e.g. timezone-aware datetimes, prefetch dedup, file-based IPC for easier testing).
