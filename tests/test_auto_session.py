# tests/test_auto_session.py
import os
import pytest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read(rel):
    return open(os.path.join(PLUGIN_ROOT, rel), encoding="utf-8").read()

def exists(rel):
    return os.path.exists(os.path.join(PLUGIN_ROOT, rel))

# ── Spec test 1 ──────────────────────────────────────────────────────────────
def test_usage_log_exists():
    """memory/usage-log.md seed file is created."""
    assert exists("memory/usage-log.md"), "memory/usage-log.md must exist"

# ── Spec test 2 ──────────────────────────────────────────────────────────────
def test_prodmasterai_step0_describes_append_format():
    """Step 0 in prodmasterai describes the ISO 8601 + processed:false format."""
    content = read("skills/prodmasterai/SKILL.md")
    assert "Step 0" in content
    assert "ISO 8601" in content
    assert "processed: false" in content

# ── Spec test 3 ──────────────────────────────────────────────────────────────
def test_session_start_injects_when_unprocessed():
    """session-start injects 'Auto-session queued' when processed:false entries exist."""
    content = read("hooks/session-start.md")
    assert "Auto-session queued" in content
    assert "processed: false" in content

# ── Spec test 4 ──────────────────────────────────────────────────────────────
def test_session_start_silent_when_no_unprocessed():
    """session-start injects nothing when N=0."""
    content = read("hooks/session-start.md")
    assert "inject nothing" in content or "Else: inject nothing" in content

# ── Spec test 5 ──────────────────────────────────────────────────────────────
def test_session_start_handles_missing_usage_log():
    """session-start sets N=0 and skips injection when usage-log.md does not exist."""
    content = read("hooks/session-start.md")
    assert ("usage-log.md" in content and "does not exist" in content) or \
           ("usage-log.md" in content and "If file does not exist" in content)
    # The N=0 path must lead to no injection — validated by presence of silent skip
    assert "inject nothing" in content or "skip to step" in content

# ── Spec test 6 ──────────────────────────────────────────────────────────────
def test_session_start_last_measure_date_fallback():
    """session-start uses 'never' as LAST_MEASURE_DATE when skill-performance has no real entries."""
    content = read("hooks/session-start.md")
    assert "set LAST_MEASURE_DATE" in content or \
           'LAST_MEASURE_DATE = "never"' in content or \
           ("LAST_MEASURE_DATE" in content and '"never"' in content)

# ── Spec test 7 ──────────────────────────────────────────────────────────────
def test_prodmasterai_step3e_marks_processed_true():
    """Step 3E fires measure and marks all processed:false entries as processed:true."""
    content = read("skills/prodmasterai/SKILL.md")
    assert "Auto-session queued" in content
    assert "processed: true" in content   # write-back instruction must be present

# ── Spec test 8 ──────────────────────────────────────────────────────────────
def test_prodmasterai_step3e_has_precondition_guard():
    """Step 3E does not fire when all entries are already processed:true."""
    content = read("skills/prodmasterai/SKILL.md")
    # Precondition requires at least one processed:false line
    assert "processed: false" in content
    assert "Precondition" in content or "precondition" in content

# ── Spec test 9 ──────────────────────────────────────────────────────────────
def test_measure_auto_session_path():
    """measure has Auto-Session Path: no user prompts, skips learn, runs Step 5."""
    content = read("skills/measure/SKILL.md")
    assert "Auto-Session Path" in content
    assert "source: auto-session" in content
    assert "Skip" in content and "learn" in content   # Step 4 skip instruction
    assert "Step 5" in content                         # Step 5 still runs

# ── Spec test 10 ─────────────────────────────────────────────────────────────
def test_measure_auto_session_sets_inferred():
    """measure auto-session entries include inferred: true."""
    content = read("skills/measure/SKILL.md")
    assert "inferred" in content
    assert "inferred: true" in content or "inferred | true" in content

# ── Spec test 11 ─────────────────────────────────────────────────────────────
def test_measure_minimum_tasks_completed():
    """tasks_completed minimum is 1 for any session."""
    content = read("skills/measure/SKILL.md")
    assert "min 1" in content or "minimum 1" in content or "(min 1)" in content

# ── Spec test 12 ─────────────────────────────────────────────────────────────
def test_report_excludes_inferred_from_averages():
    """report excludes inferred:true entries from averages and shows separate count."""
    content = read("skills/report/SKILL.md")
    assert "inferred: true" in content
    assert "excluded from averages" in content
    assert "Auto-tracked sessions" in content

# ── Spec test 13 ─────────────────────────────────────────────────────────────
def test_session_start_uses_processed_flag_not_date():
    """session-start uses the processed flag as the canonical counter (no date filter)."""
    content = read("hooks/session-start.md")
    # The canonical comment must be present — this is the sole guard mechanism
    assert "canonical" in content or "no date filtering" in content or "processed flag" in content

# ── Spec test 14 ─────────────────────────────────────────────────────────────
def test_report_bootstrap_excludes_inferred():
    """report Fresh-State Bootstrap fires when only inferred:true entries exist."""
    content = read("skills/report/SKILL.md")
    # Bootstrap guard must reference inferred as non-real data — unique to the guard section
    assert "qualifies as real data" in content or "inferred: true` is absent" in content or \
           "real-data entries" in content

# ── Additional structural checks ─────────────────────────────────────────────

def test_usage_log_has_header():
    """usage-log.md seed file has the correct two-line comment header."""
    content = read("memory/usage-log.md")
    assert "# Usage Log" in content
    assert "prodmasterai appends" in content

def test_prodmasterai_reads_usage_log():
    """prodmasterai frontmatter reads: list includes memory/usage-log.md."""
    content = read("skills/prodmasterai/SKILL.md")
    assert "memory/usage-log.md" in content

def test_prodmasterai_priority_includes_e():
    """prodmasterai Rules section priority order includes E."""
    content = read("skills/prodmasterai/SKILL.md")
    assert "A > E > B > C > D" in content

def test_evolve_self_excludes_inferred():
    """evolve-self excludes inferred:true entries and has updated Mode 1 real-data guard."""
    content = read("skills/evolve-self/SKILL.md")
    assert "inferred: true" in content
    # Mode 1 guard must reference the real-data concept, not just example:true
    assert "real-data" in content or "inferred: true` is absent" in content or \
           "inferred: true` are absent" in content
