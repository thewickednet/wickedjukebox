# Scope `DynamicPlaylist.apply_to` to the current channel — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `find_song`'s dynamic-playlist filter must only apply playlists bound to the *current* channel, instead of applying the first active playlist of *any* channel to every channel.

**Background / bug:** `DynamicPlaylist.apply_to` selects `WHERE group_id > 0 ORDER BY group_id` with **no `channel_id` filter**, and `find_song` calls it without passing the channel. In production this applies channel 2's active playlist ("Grillen") to the `wicked` channel (channel 1), restricting it to the wrong artist list. (It was dormant until a raw-string→`text()` fix made `apply_to` actually apply the filter.) Wicked's own playlists are `group_id = 0` (inactive), so the correct behavior is: apply nothing for wicked → pick from the whole DB.

**Fix:** pass the current channel id from `find_song` into `apply_to`, and filter the playlist lookup by `channel_id`. When there's no channel (or no active playlist for it), apply no filter.

**Tech Stack:** Python 3.13, SQLAlchemy < 2.0, MariaDB, pytest.

## Global Constraints

- **SQLAlchemy pinned `< 2.0`.**
- **Scope: channel-scoping only.** Do NOT change the raw-SQL execution mechanism, the artist/album joins, the `text()` parsing, or the exception handling in `apply_to`. Do NOT fix the separate "only ever applies ONE playlist per group" issue (the code's own TODO) — out of scope.
- **Behavior:** `apply_to(query, channel_id)` with `channel_id is None` → return `query` unchanged (no filter). `find_song` with no `channel_name`, or an unknown channel → passes `None`.
- Only these files: `wickedjukebox/model/db/playback.py`, `wickedjukebox/core/smartfind.py`, `test/test_prefetcher.py`.
- Formatting: black 26.5.1 / isort 8.0.1, line-length 80 (repo venv now has these; or `/tmp/wjfmt-new`).

## Environment (already provisioned)

- Venv `~/.virtualenvs/wickedjukebox/bin/{python,pytest}`. Tests run against the config DSN (MariaDB container port 33066); `conftest.py` builds the schema + rolls back per test. `metadata.bind` and `dbsession` share one connection, so a `dynamicPlaylist` row flushed in a test IS visible to `apply_to`'s implicit `.execute()`.
- Baseline: **130 passing**. After the 2 new tests: **132**.

---

## Task 1: Channel-scope `apply_to` and pass the channel from `find_song`

**Files:**
- Modify: `wickedjukebox/model/db/playback.py` (`DynamicPlaylist.apply_to`)
- Modify: `wickedjukebox/core/smartfind.py` (`find_song`, the `apply_to` call, line ~279)
- Test: `test/test_prefetcher.py`

**Interfaces:**
- Changed: `DynamicPlaylist.apply_to(query, channel_id: Optional[int]) -> Query` (was `apply_to(query)`). `find_song` is the only caller.

- [ ] **Step 1: Write the failing tests**

Append to `test/test_prefetcher.py` (it already imports `find_song`, `SCORING_CONFIG`, `Channel`, `Song`). Add a helper and two tests:

```python
def _add_dynamic_playlist(dbsession, channel_id, query, group_id=1):
    from wickedjukebox.model.db.playback import DynamicPlaylist

    dpl = DynamicPlaylist()
    dpl.channel_id = channel_id
    dpl.group_id = group_id
    dpl.probability = 1.0
    dpl.query = query
    dbsession.add(dpl)
    dbsession.flush()
    return dpl


def test_dynamic_playlist_scoped_to_channel(
    dbsession: Session, default_data: Dict[str, Any]
):
    """A playlist bound to one channel must not filter another scope's picks."""
    ch = default_data["default_channel"]
    _add_dynamic_playlist(dbsession, ch.id, 'artist is "zzz_nomatch"')
    # its own channel: the match-nothing playlist applies -> no pick
    assert (
        find_song(dbsession, SCORING_CONFIG, True, channel_name="test-channel")
        is None
    )
    # no channel: the playlist must NOT apply -> a pick is returned
    assert find_song(dbsession, SCORING_CONFIG, True) is not None


def test_dynamic_playlist_applies_for_its_channel(
    dbsession: Session, default_data: Dict[str, Any]
):
    """A matching playlist bound to the channel keeps matching songs eligible."""
    ch = default_data["default_channel"]
    _add_dynamic_playlist(dbsession, ch.id, 'artist is "Tool"')  # default artist
    song = find_song(
        dbsession, SCORING_CONFIG, True, channel_name="test-channel"
    )
    assert song is not None
    assert song.id == default_data["default_song"].id
```

- [ ] **Step 2: Run to verify RED**

Run: `~/.virtualenvs/wickedjukebox/bin/pytest test/test_prefetcher.py -k dynamic_playlist -v`
Expected: `test_dynamic_playlist_scoped_to_channel` FAILS — today `apply_to` ignores the channel, so the `zzz_nomatch` playlist is applied to the no-channel pick too, making `find_song(..., channel_name=None)` return `None` instead of a song. (`test_dynamic_playlist_applies_for_its_channel` may already pass — it's positive coverage.)

- [ ] **Step 3: Channel-scope `apply_to`**

In `wickedjukebox/model/db/playback.py`, change the `DynamicPlaylist.apply_to` signature and add the channel filter. Replace:

```python
    @staticmethod
    def apply_to(query: Query) -> Query:
        """
        Modify *query* by applying additional filters based on a "dynamic
        playlist"
        """
        # TODO An issue with table-aliasing causes cartesian products.
        #      Investigate where this comes from.
        sel = select([DynamicPlaylist.query])
        sel = sel.where(DynamicPlaylist.group_id > 0)
        sel = sel.order_by("group_id")
        res = sel.execute().fetchall()
```

with:

```python
    @staticmethod
    def apply_to(query: Query, channel_id: Optional[int]) -> Query:
        """
        Modify *query* by applying the active dynamic playlist **of the given
        channel** (``group_id > 0``). With no channel (``channel_id is None``)
        or no active playlist for it, *query* is returned unchanged.
        """
        if channel_id is None:
            return query
        # TODO An issue with table-aliasing causes cartesian products.
        #      Investigate where this comes from.
        sel = select([DynamicPlaylist.query])
        sel = sel.where(DynamicPlaylist.channel_id == channel_id)
        sel = sel.where(DynamicPlaylist.group_id > 0)
        sel = sel.order_by("group_id")
        res = sel.execute().fetchall()
```

Leave the rest of the method (the `for dpl in res:` loop, joins, `text(...)` where, exception handlers, `return query`) unchanged.

- [ ] **Step 4: Pass the channel from `find_song`**

In `wickedjukebox/core/smartfind.py`, replace the single call (line ~279):

```python
    query = DynamicPlaylist.apply_to(query)  # type: ignore
```

with (resolve the channel id; `None` when there's no channel name or the channel is unknown):

```python
    dp_channel = (
        Channel.by_name(session, channel_name) if channel_name else None
    )
    query = DynamicPlaylist.apply_to(  # type: ignore
        query, dp_channel.id if dp_channel else None
    )
```

(`Channel` and `DynamicPlaylist` are already imported in `smartfind.py`.)

- [ ] **Step 5: Run the dynamic-playlist tests → GREEN, then the full suite**

```bash
~/.virtualenvs/wickedjukebox/bin/pytest test/test_prefetcher.py -k dynamic_playlist -v
~/.virtualenvs/wickedjukebox/bin/pytest -q 2>&1 | tail -3
```
Expected: both dynamic-playlist tests pass; full suite = **132 passed, 0 failures** (130 + 2).

- [ ] **Step 6: Format and commit**

```bash
/tmp/wjfmt-new/bin/isort --profile black --line-length 80 wickedjukebox/model/db/playback.py wickedjukebox/core/smartfind.py test/test_prefetcher.py
/tmp/wjfmt-new/bin/black --line-length 80 wickedjukebox/model/db/playback.py wickedjukebox/core/smartfind.py test/test_prefetcher.py
git add wickedjukebox/model/db/playback.py wickedjukebox/core/smartfind.py test/test_prefetcher.py
git -c commit.gpgsign=false commit -m "fix(smartfind): scope dynamic playlists to the current channel

DynamicPlaylist.apply_to now filters by channel_id (passed from find_song), so a
playlist active on one channel no longer restricts other channels' picks. A
channel with no active playlist (or no channel) applies no filter -> whole-DB
selection. Fixes wicked being restricted by another channel's playlist.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review (completed by plan author)

**1. Spec coverage:** channel-scoped `apply_to` (Step 3) ✔; channel passed from `find_song`, `None`-safe (Step 4) ✔; no-channel/no-active → no filter (Step 3 early return + tests) ✔; execution mechanism / joins / parsing untouched (Global Constraints) ✔; "one playlist per group" left alone ✔.

**2. Placeholder scan:** none — exact before/after code and commands throughout.

**3. Type/name consistency:** `apply_to(query, channel_id)` signature matches its single caller's updated call; `Channel.by_name` returns a `Channel` (or `None`), `.id` guarded.

## Notes / risks

- `find_song` now does `Channel.by_name` for the playlist scope in addition to the existing `Channel.mood_range` lookup — a second cheap indexed lookup; acceptable for a minimal fix.
- The `zzz_nomatch` RED test proves the playlist is *not* applied cross-scope; the `"Tool"` test proves a matching playlist still filters correctly for its own channel.
- No production data is touched by this change (the stopgap `UPDATE dynamicPlaylist` is separate and not part of this branch).
