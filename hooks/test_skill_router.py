#!/usr/bin/env python3
"""Round-trip tests for the sticky session-state helpers in skill-router.

Why: the helpers (load/save/prune/reinject) are the load-bearing pieces of
the sticky feature — pure functions over JSON files. Easy to exercise
without invoking the full hook end-to-end.
Deps: stdlib only — uses unittest + tempfile, no pytest needed.
Run:  python3 -m unittest hooks/test_skill_router.py -v
"""

from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import time
import unittest
from pathlib import Path


def _load_module():
    """Import skill-router.py despite the hyphen in its filename."""
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location(
        "skill_router", here / "skill-router.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sr = _load_module()


class StickyStateTests(unittest.TestCase):
    """Round-trip tests for save_session_state ↔ load_session_state."""

    def setUp(self) -> None:
        # Redirect SESSION_STATE_DIR to a per-test tempdir so we don't
        # touch ~/.claude/hooks/sessions/ during tests.
        self._tmp = tempfile.TemporaryDirectory()
        self._orig_dir = sr.SESSION_STATE_DIR
        self._orig_ttl = sr.STICKY_TTL_SECS
        sr.SESSION_STATE_DIR = Path(self._tmp.name)
        # Use a generous TTL by default; individual tests override.
        sr.STICKY_TTL_SECS = 900
        # Clear any stray env from prior runs
        os.environ.pop(sr.STICKY_DISABLE_ENV, None)

    def tearDown(self) -> None:
        sr.SESSION_STATE_DIR = self._orig_dir
        sr.STICKY_TTL_SECS = self._orig_ttl
        self._tmp.cleanup()
        os.environ.pop(sr.STICKY_DISABLE_ENV, None)

    # --- Round trip ------------------------------------------------------

    def test_save_then_load_returns_skills(self) -> None:
        sr.save_session_state("sess-1", ["dbt", "data-eng"], "regex-only")
        state = sr.load_session_state("sess-1")
        self.assertIsNotNone(state)
        self.assertEqual(state["last_skills"], ["dbt", "data-eng"])
        self.assertEqual(state["session_id"], "sess-1")
        self.assertEqual(state["last_category"], "regex-only")
        self.assertGreater(state["last_routed_at"], 0)

    def test_load_returns_none_for_missing_session(self) -> None:
        self.assertIsNone(sr.load_session_state("never-existed"))

    def test_load_returns_none_for_corrupt_json(self) -> None:
        sr.SESSION_STATE_DIR.mkdir(parents=True, exist_ok=True)
        (sr.SESSION_STATE_DIR / "broken.json").write_text("{not valid json")
        self.assertIsNone(sr.load_session_state("broken"))

    # --- TTL boundary ----------------------------------------------------

    def test_load_honors_ttl_expiry(self) -> None:
        sr.STICKY_TTL_SECS = 60  # 1 minute
        sr.save_session_state("sess-2", ["dbt"], "regex-only")
        # Backdate the file's ts so it looks 2 minutes old
        path = sr.session_state_path("sess-2")
        data = json.loads(path.read_text())
        data["last_routed_at"] = time.time() - 120
        path.write_text(json.dumps(data))
        self.assertIsNone(sr.load_session_state("sess-2"))

    def test_load_returns_state_just_inside_ttl(self) -> None:
        sr.STICKY_TTL_SECS = 60
        sr.save_session_state("sess-3", ["dbt"], "regex-only")
        path = sr.session_state_path("sess-3")
        data = json.loads(path.read_text())
        # 30 seconds old — comfortably inside TTL
        data["last_routed_at"] = time.time() - 30
        path.write_text(json.dumps(data))
        self.assertIsNotNone(sr.load_session_state("sess-3"))

    # --- No-op guards ----------------------------------------------------

    def test_save_with_empty_skills_is_noop(self) -> None:
        sr.save_session_state("sess-4", [], "both-empty")
        self.assertFalse(sr.session_state_path("sess-4").exists())

    def test_save_with_empty_session_id_is_noop(self) -> None:
        sr.save_session_state("", ["dbt"], "regex-only")
        # No file should exist for the empty session_id
        self.assertFalse(any(sr.SESSION_STATE_DIR.iterdir()))

    # --- Atomic write ----------------------------------------------------

    def test_save_leaves_no_tmp_files(self) -> None:
        for i in range(20):
            sr.save_session_state(f"sess-atomic-{i}", ["dbt"], "regex-only")
        leftovers = [
            f for f in sr.SESSION_STATE_DIR.iterdir() if f.suffix == ".tmp"
        ]
        self.assertEqual(leftovers, [])

    # --- sticky_reinject -------------------------------------------------

    def test_sticky_reinject_filters_unknown_skills(self) -> None:
        sr.save_session_state(
            "sess-5", ["dbt-real", "removed-skill"], "regex-only"
        )
        result = sr.sticky_reinject("sess-5", {"dbt-real", "other"})
        # "removed-skill" was filtered out; "dbt-real" kept
        self.assertEqual(result, ["dbt-real"])

    def test_sticky_reinject_returns_empty_when_disabled(self) -> None:
        sr.save_session_state("sess-6", ["dbt"], "regex-only")
        os.environ[sr.STICKY_DISABLE_ENV] = "1"
        self.assertEqual(sr.sticky_reinject("sess-6", {"dbt"}), [])

    def test_sticky_reinject_returns_empty_for_missing_session_id(self) -> None:
        self.assertEqual(sr.sticky_reinject(None, {"dbt"}), [])
        self.assertEqual(sr.sticky_reinject("", {"dbt"}), [])

    def test_sticky_reinject_returns_empty_when_state_missing(self) -> None:
        self.assertEqual(sr.sticky_reinject("never-saved", {"dbt"}), [])

    def test_sticky_reinject_returns_empty_when_state_expired(self) -> None:
        sr.STICKY_TTL_SECS = 60
        sr.save_session_state("sess-7", ["dbt"], "regex-only")
        path = sr.session_state_path("sess-7")
        data = json.loads(path.read_text())
        data["last_routed_at"] = time.time() - 1000
        path.write_text(json.dumps(data))
        self.assertEqual(sr.sticky_reinject("sess-7", {"dbt"}), [])

    # --- Prune ------------------------------------------------------------

    def test_prune_deletes_old_keeps_fresh(self) -> None:
        sr.STICKY_TTL_SECS = 60  # prune cutoff = 60 * 4 = 240s
        # Create one fresh, one stale
        sr.save_session_state("fresh", ["dbt"], "regex-only")
        sr.save_session_state("stale", ["dbt"], "regex-only")
        stale_path = sr.session_state_path("stale")
        # Backdate mtime to 5 minutes ago (beyond 4×TTL = 4 min cutoff)
        old = time.time() - 300
        os.utime(stale_path, (old, old))

        sr.prune_stale_sessions()

        self.assertTrue(sr.session_state_path("fresh").exists())
        self.assertFalse(stale_path.exists())

    def test_prune_handles_missing_dir(self) -> None:
        # Point at a dir that doesn't exist — should not raise
        sr.SESSION_STATE_DIR = Path(self._tmp.name) / "nonexistent"
        sr.prune_stale_sessions()  # no exception is the assertion


class SkipReasonOrderingTests(unittest.TestCase):
    """The `should_skip` decision matters for log diagnostics — make sure
    ack-words are classified as ack-word, not mis-categorized as too-short
    just because they happen to be short."""

    def setUp(self) -> None:
        os.environ.pop(sr.DISABLE_ENV, None)
        os.environ.pop(sr.RECURSION_GUARD_ENV, None)

    def test_short_ack_classified_as_ack_word(self) -> None:
        # "proceed" is 7 chars (< 12) AND in SKIP_PROMPTS — must report ack-word
        self.assertEqual(sr.should_skip("proceed"), "ack-word")
        self.assertEqual(sr.should_skip("lgtm"), "ack-word")
        self.assertEqual(sr.should_skip("do it"), "ack-word")

    def test_long_ack_still_ack_word(self) -> None:
        self.assertEqual(sr.should_skip("please proceed"), "ack-word")

    def test_short_non_ack_is_too_short(self) -> None:
        self.assertEqual(sr.should_skip("hmm"), "too-short")
        self.assertEqual(sr.should_skip("do that pls"), "too-short")

    def test_long_prompt_no_skip(self) -> None:
        self.assertIsNone(sr.should_skip("add a dbt model with incremental strategy"))

    def test_slash_command_short_circuit(self) -> None:
        self.assertEqual(sr.should_skip("/review"), "slash-command")

    def test_empty_prompt_is_too_short(self) -> None:
        self.assertEqual(sr.should_skip(""), "too-short")
        self.assertEqual(sr.should_skip("   "), "too-short")


class BuildReminderTests(unittest.TestCase):
    """Sanity checks on the reminder text — the assistant relies on these
    cues to decide whether to invoke the skill."""

    def test_router_source_does_not_prefix(self) -> None:
        text = sr.build_reminder(["dbt"], source="router")
        self.assertNotIn("Continuing from earlier", text)
        self.assertIn("dbt", text)

    def test_sticky_source_carries_continuation_prefix(self) -> None:
        text = sr.build_reminder(["dbt"], source="sticky")
        self.assertIn("Continuing from earlier routing", text)
        self.assertIn("follow-up", text)

    def test_single_vs_multi_skill_phrasing_differs(self) -> None:
        single = sr.build_reminder(["dbt"], source="router")
        multi = sr.build_reminder(["dbt", "data-eng"], source="router")
        # Single uses "matched the user's prompt to: X"
        # Multi uses "matched the user's prompt to N skills:"
        self.assertIn("matched the user's prompt to: dbt", single)
        self.assertIn("matched the user's prompt to 2 skills", multi)


if __name__ == "__main__":
    unittest.main()
