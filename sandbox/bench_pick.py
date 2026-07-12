#!/usr/bin/env python3
"""
Read-only benchmark for the wicked-jukebox "smart random" pick.

Measures per-pick query time on THIS machine's database so you can see the real
cost on the jukebox hardware (vs a dev box). It is SAFE FOR PRODUCTION: it issues
only SELECTs -- no INSERT/UPDATE/DELETE, no COMMIT.

What it reports, per scenario:
  * first  = first execution after connecting (cache may be cold)
  * median = steady-state (buffer pool warm) over N runs -- what the prefetch
             thread normally sees

Scenarios:
  * current smart-scan for each channel, honoring that channel's mood window
  * current smart-scan with no mood window (the worst / full-table case)
  * candidate-pool prototype at a few pool sizes (the proposed optimization)

Usage
-----
  # simplest: pass the DSN explicitly
  python3 bench_pick.py --dsn "mysql+pymysql://jukebox:PASSWORD@127.0.0.1:3306/jukebox"

  # or via env
  WJ_DSN="mysql+pymysql://..." python3 bench_pick.py

  # or let it try the wicked-jukebox config (run inside the jukebox venv/dir)
  python3 bench_pick.py

  # options
  python3 bench_pick.py --runs 15 --pool 300,800,2000 --max-duration 600

Needs a MySQL driver (pymysql or mysqlclient); the jukebox venv already has one.
Run it with the jukebox's Python so the driver is available, e.g.
  /path/to/jukebox/env/bin/python bench_pick.py --dsn ...
"""

import argparse
import logging
import os
import statistics
import sys
import time
from urllib.parse import unquote, urlparse

# The wicked-jukebox package logs a full traceback on every pick because of a
# pre-existing DynamicPlaylist.apply_to bug (raw-string .where() on SQLAlchemy
# 1.4+). Silence all logging so the benchmark output stays readable.
logging.disable(logging.CRITICAL)

# --- 1) resolve the DSN --------------------------------------------------------


def resolve_dsn(cli_dsn):
    if cli_dsn:
        return cli_dsn
    if os.environ.get("WJ_DSN"):
        return os.environ["WJ_DSN"]
    # try the wicked-jukebox config-resolver (only works with the package on path)
    try:
        from wickedjukebox.config import Config, ConfigKeys  # type: ignore

        dsn = Config().get(ConfigKeys.DSN, "")
        if dsn:
            return dsn
    except Exception:
        pass
    # try the on-disk ini directly
    for path in (
        os.path.expanduser("~/.wicked/wickedjukebox/config.ini"),
        ".wicked/wickedjukebox/config.ini",
        os.path.expanduser("~/.config/wickedjukebox/config.ini"),
    ):
        if os.path.exists(path):
            import configparser

            cp = configparser.ConfigParser()
            cp.read(path)
            if cp.has_option("core", "dsn"):
                return cp.get("core", "dsn")
    sys.exit(
        "Could not resolve a DSN. Pass --dsn "
        "'mysql+pymysql://user:pass@host:port/db' (or set WJ_DSN)."
    )


def connect(dsn):
    """Open a read-only-intent connection from a SQLAlchemy-style DSN."""
    u = urlparse(dsn)
    host = u.hostname or "127.0.0.1"
    port = u.port or 3306
    user = unquote(u.username or "")
    password = unquote(u.password or "")
    db = (u.path or "/").lstrip("/") or "jukebox"
    try:
        import pymysql

        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db,
            charset="utf8mb4",
            autocommit=False,
        )
        return conn, "pymysql"
    except ImportError:
        pass
    import MySQLdb  # type: ignore

    conn = MySQLdb.connect(
        host=host, port=port, user=user, passwd=password, db=db
    )
    return conn, "mysqlclient"


# --- 2) helpers ---------------------------------------------------------------


def scalar(cur, sql, args=None):
    cur.execute(sql, args or ())
    row = cur.fetchone()
    return None if row is None else row[0]


def existing_columns(cur, table):
    cur.execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s",
        (table,),
    )
    return {r[0] for r in cur.fetchall()}


def time_query(cur, sql, args, runs):
    """Return (first_ms, median_ms, min_ms, max_ms, p90_ms). Fully fetches."""
    samples = []
    for i in range(runs + 1):  # 1 warm-up-ish extra; keep the first separately
        t0 = time.perf_counter()
        cur.execute(sql, args)
        cur.fetchall()
        samples.append((time.perf_counter() - t0) * 1000.0)
    first = samples[0]
    warm = sorted(samples[1:]) or [first]
    p90 = warm[min(len(warm) - 1, int(round(0.9 * (len(warm) - 1))))]
    return first, statistics.median(warm), warm[0], warm[-1], p90


def fmt(row_stats):
    f, med, lo, hi, p90 = row_stats
    return (
        f"first={f:8.1f}ms  median={med:8.1f}ms  "
        f"min={lo:8.1f}  p90={p90:8.1f}  max={hi:8.1f}"
    )


# --- 3) build the scoring scan (schema-defensive) -----------------------------

LP_CUTOFF = 7 * 24 * 60 * 60
AGE_CUTOFF = 14 * 24 * 60 * 60


def build_scan(cols, csd_cols, mood, pool_ids):
    """Reconstruct find_song's cost structure: full LEFT JOIN scan + a per-row
    score with recency/age/RAND(), ORDER BY score, LIMIT 10. The exact weights
    do not affect timing; only the scan+filesort do."""
    has_lastplayed = "lastPlayed" in csd_cols
    recency = (
        "- IFNULL(LEAST(%(lpc)s, TIMESTAMPDIFF(SECOND, csd.lastPlayed, NOW())),"
        " %(lpc)s) / %(lpc)s * %(w_lp)s"
        if has_lastplayed
        else "- %(w_lp)s"
    )
    score = (
        f"( {recency} "
        "+ IFNULL(IF(TIMESTAMPDIFF(SECOND, s.added, NOW()) < %(agec)s, "
        "TIMESTAMPDIFF(SECOND, s.added, NOW()) / %(agec)s * %(w_age)s, 0), 0) "
        "+ (RAND() * %(w_rand)s * 2 - %(w_rand)s) ) AS score"
    )
    where = ["s.duration < %(maxd)s"]
    if "broken" in cols:
        where.append("NOT s.broken")
    if "exclude_from_random" in cols:
        where.append("NOT s.exclude_from_random")
    if mood and "mood_score" in cols:
        where.append(
            "(s.mood_score IS NULL OR s.mood_score BETWEEN %(mlo)s AND %(mhi)s)"
        )
    if pool_ids:
        where.append("s.id IN (%s)" % ",".join(str(int(i)) for i in pool_ids))
    sql = (
        f"SELECT s.id, s.localpath, {score} "
        "FROM song s LEFT JOIN channel_song_data csd ON csd.song_id = s.id "
        f"WHERE {' AND '.join(where)} ORDER BY score DESC LIMIT 10"
    )
    return sql


# --- 4) main ------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dsn", default=None)
    ap.add_argument("--runs", type=int, default=12)
    ap.add_argument("--pool", default="300,800,2000")
    ap.add_argument("--max-duration", type=int, default=600)
    args = ap.parse_args()

    dsn = resolve_dsn(args.dsn)
    conn, driver = connect(dsn)
    cur = conn.cursor()

    params = {
        "lpc": LP_CUTOFF,
        "agec": AGE_CUTOFF,
        "w_lp": 10,
        "w_age": 1,
        "w_rand": 1,
        "maxd": args.max_duration,
    }

    try:
        # environment / DB facts -------------------------------------------------
        version = scalar(cur, "SELECT VERSION()")
        bp = scalar(cur, "SELECT @@innodb_buffer_pool_size")
        cols = existing_columns(cur, "song")
        csd_cols = existing_columns(cur, "channel_song_data")
        songs = scalar(cur, "SELECT COUNT(*) FROM song")
        minid = scalar(cur, "SELECT MIN(id) FROM song")
        maxid = scalar(cur, "SELECT MAX(id) FROM song")
        csd = scalar(cur, "SELECT COUNT(*) FROM channel_song_data")
        active = scalar(
            cur,
            "SELECT COUNT(*) FROM users "
            "WHERE unix_timestamp(proof_of_listening)+120 > unix_timestamp(now())",
        )
        if not songs:
            sys.exit("song table is empty -- nothing to benchmark.")
        minid, maxid = int(minid), int(maxid)

        print("=" * 78)
        print(f"driver={driver}  server={version}")
        print(f"innodb_buffer_pool_size = {int(bp)/1024/1024:.0f} MiB")
        print(
            f"songs={songs}  id_range={minid}..{maxid}  "
            f"channel_song_data={csd}  active_users_now={active}"
        )
        print(
            f"runs={args.runs} (median = warm cache)   max_duration={args.max_duration}"
        )
        print("=" * 78)

        # per-channel scans ------------------------------------------------------
        cur.execute("SELECT name, mood_low, mood_high FROM channel ORDER BY id")
        channels = cur.fetchall()
        print(
            "\n### current smart-scan, per channel (honoring its mood window) ###"
        )
        for name, mlo, mhi in channels:
            mood = mlo is not None and mhi is not None
            p = dict(params)
            if mood:
                p["mlo"], p["mhi"] = mlo, mhi
            sql = build_scan(cols, csd_cols, mood, None)
            label = (
                f"channel={name!r} mood={mlo}..{mhi}"
                if mood
                else f"channel={name!r} mood=off"
            )
            print(f"  {label:38s} {fmt(time_query(cur, sql, p, args.runs))}")

        # no-channel full scan (worst case) -------------------------------------
        sql_full = build_scan(cols, csd_cols, False, None)
        print(
            "\n### current smart-scan, no mood window (full-table worst case) ###"
        )
        print(
            f"  {'no channel':38s} {fmt(time_query(cur, sql_full, params, args.runs))}"
        )
        cur.execute("EXPLAIN " + sql_full, params)
        print("  EXPLAIN:")
        for r in cur.fetchall():
            print("   ", r)

        # candidate-pool prototype ----------------------------------------------
        import random

        print(
            "\n### candidate-pool prototype (proposed optimization, no mood) ###"
        )
        for k in [int(x) for x in args.pool.split(",") if x.strip()]:
            pool = [random.randint(minid, maxid) for _ in range(k * 3)]
            sqlp = build_scan(cols, csd_cols, False, pool)
            print(
                f"  pool k={k:<6d}{'':27s}"
                f"{fmt(time_query(cur, sqlp, params, args.runs))}"
            )

        # optional: time the REAL find_song if the package imports cleanly ------
        try:
            from wickedjukebox.model.db.sameta import (
                connect as wj_connect,
                Session,
            )
            from wickedjukebox.core.smartfind import find_song, ScoringConfig

            wj_connect(dsn)
            sc = {
                ScoringConfig.USER_RATING: 4,
                ScoringConfig.LAST_PLAYED: 10,
                ScoringConfig.NEVER_PLAYED: 4,
                ScoringConfig.RANDOMNESS: 1,
                ScoringConfig.MAX_DURATION: args.max_duration,
                ScoringConfig.PROOF_OF_LIFE_TIMEOUT: 120,
            }
            print("\n### faithful cross-check: real find_song() ###")
            for name, mlo, mhi in channels:
                ts = []
                for _ in range(args.runs):
                    s = Session()
                    t0 = time.perf_counter()
                    find_song(s, sc, True, channel_name=name)
                    ts.append((time.perf_counter() - t0) * 1000)
                    s.close()
                ts.sort()
                print(
                    f"  find_song channel={name!r:20s} median={statistics.median(ts):8.1f}ms  min={ts[0]:8.1f}  max={ts[-1]:8.1f}"
                )
        except Exception as exc:  # noqa
            print(
                f"\n(real find_song cross-check skipped: {type(exc).__name__}: {exc})"
            )

        print("\nDone. (read-only; rolling back any implicit transaction)")
    finally:
        try:
            conn.rollback()
        except Exception:
            pass
        conn.close()


if __name__ == "__main__":
    main()
