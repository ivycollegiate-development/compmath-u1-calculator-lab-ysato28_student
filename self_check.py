#!/usr/bin/env python3
"""Journal CI check — progress meter, never pass/fail.

Reads journal_check.yml at the repo root. If the config file is missing,
unreadable, or does not name a journal date, the check SKIPS with a clear
informational message and exits 0 — an unconfigured repo push must never
show an error to a student.
"""
import os
import re
import subprocess
import sys
import glob

CONFIG = "journal_check.yml"
TEMPLATE = "journal-TEMPLATE.md"
PLACEHOLDER = "[WRITE YOUR ANSWER HERE"

results = []          # (name, passed, detail)


def log(msg: str) -> None:
    print(msg, flush=True)


def git(args):
    return subprocess.run(["git"] + args, capture_output=True, text=True)


def parse_config(text):
    """Tiny parser for the flat YAML we ship. Returns dict or None."""
    cfg = {}
    groups, in_groups, cur = [], False, None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("required_term_groups:"):
            in_groups = True
            continue
        if in_groups:
            if line.startswith("- [") and line.endswith("]"):
                items = [x.strip().strip("'\"") for x in line[3:-1].split(",")]
                groups.append([i for i in items if i])
                continue
            if line.startswith("- ") and cur is not None:
                groups[-1].append(line[2:].strip().strip("'\""))
                continue
            in_groups = False
        m = re.match(r"([a-z_]+):\s*(.*)", line)
        if m:
            cfg[m.group(1)] = m.group(2).strip().strip("'\"")
    if groups:
        cfg["required_term_groups"] = [g for g in groups if g]
    return cfg or None


def load_config():
    if not os.path.exists(CONFIG):
        return None, f"config file '{CONFIG}' not found in this repo"
    try:
        with open(CONFIG, encoding="utf-8") as f:
            cfg = parse_config(f.read())
    except Exception as e:  # unreadable config -> skip, never error
        return None, f"config file '{CONFIG}' could not be read: {e}"
    if not cfg or not cfg.get("journal_date"):
        return None, f"'{CONFIG}' has no journal_date set"
    return cfg, None


def check(name, passed, detail):
    results.append((name, passed, detail))
    mark = "PASS" if passed else "MISS"
    log(f"  [{mark}] {name}")
    log(f"          {detail}")


def main():
    cfg, skip_reason = load_config()
    if cfg is None:
        log("=" * 60)
        log("Journal check SKIPPED — this is not an error.")
        log(f"Reason: {skip_reason}")
        log("No journal checks are configured for this repo, so there is")
        log("nothing to verify. Your push went through fine.")
        log("=" * 60)
        print("0 of 0 checks passing")
        return 0

    date = cfg["journal_date"]
    min_words = int(cfg.get("min_words", "80") or 80)
    groups = cfg.get("required_term_groups", [])
    min_groups = int(cfg.get("min_term_groups", str(max(len(groups), 1))))

    log("=" * 60)
    log(f"Journal check for date {date} — verbose report")
    log("=" * 60)

    # Template present?
    if not os.path.exists(TEMPLATE):
        log(f"  Template '{TEMPLATE}' missing — setup incomplete, skipping.")
        log("  (This is a configuration gap, not your work — nothing to fix.)")
        print("0 of 0 checks passing")
        return 0

    matches = sorted(glob.glob(f"journal-{date}-*.md"))
    log(f"[1] Looking for journal file matching journal-{date}-*.md ...")
    if matches:
        for m in matches:
            log(f"        found: {m}")
    else:
        log("        no file matched that pattern")
    check(
        f"journal-{date}-*.md file exists",
        bool(matches),
        f"expected a file named journal-{date}-<your-userid>.md in the repo root"
        if matches else f"create journal-{date}-$(whoami).md and commit it",
    )
    if not matches:
        for name in ["journal file is committed (no uncommitted changes)",
                     "journal content differs from the template",
                     "template placeholders are replaced",
                     f"at least {min_words} words written",
                     "mentions the tools it should discuss"]:
            check(name, False, "blocked by missing journal file")
        n = len(results)
        log("-" * 60)
        log(f"{sum(1 for _, p, _ in results if p)} of {n} checks passing")
        return 0

    journal = matches[0]

    # Tracked & committed?
    st = git(["status", "--porcelain"])
    dirty = st.stdout.strip()
    tracked = git(["ls-files", journal]).stdout.strip()
    log(f"[2] Is '{journal}' committed? tracked={bool(tracked)}, "
        f"uncommitted_changes={bool(dirty)}")
    check(
        "journal file is committed (no uncommitted changes)",
        bool(tracked) and not dirty,
        ("file is tracked and the tree is clean" if tracked and not dirty
         else (f"uncommitted changes:\n{dirty}" if dirty
               else "file exists but is not committed — git add/commit/push")),
    )

    # Differs from template?
    def norm(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            return re.sub(r"\s+", " ", f.read()).strip()
    same = norm(journal) == norm(TEMPLATE)
    log(f"[3] Content differs from template? {'NO (identical)' if same else 'yes'}")
    check(
        "journal content differs from the template",
        not same,
        ("content matches the template after whitespace — answer the questions"
         if same else "your answers are in place"),
    )

    # Placeholders replaced?
    with open(journal, encoding="utf-8", errors="replace") as f:
        body = f.read()
    n_ph = body.count(PLACEHOLDER)
    log(f"[4] Placeholder lines remaining: {n_ph}")
    check(
        "template placeholders are replaced",
        n_ph == 0,
        ("all placeholder lines replaced with your answers" if n_ph == 0
         else f"{n_ph} line(s) still contain '{PLACEHOLDER}'"),
    )

    # Word count
    words = len(re.findall(r"\S+", body))
    log(f"[5] Word count: {words} (minimum {min_words})")
    check(
        f"at least {min_words} words written",
        words >= min_words,
        f"found {words} words" + ("" if words >= min_words else
                                  f" — write a few more sentences"),
    )

    # Tool mentions
    low = body.lower()
    hits = sum(any(t in low for t in g) for g in groups)
    hit_names = [g[0] for g in groups if any(t in low for t in g)]
    log(f"[6] Tool topics mentioned: {hit_names} "
        f"(need {min_groups} of {len(groups)})")
    check(
        "mentions the tools it should discuss",
        hits >= min_groups,
        (f"found {hits}: {', '.join(hit_names)}" if hits
         else f"none of the target tools found — name which tool "
              f"(try/except, type conversion, input validation) you picked"),
    )

    n = len(results)
    passed = sum(1 for _, p, _ in results if p)
    log("-" * 60)
    log(f"Journal check complete for {journal}")
    print(f"{passed} of {n} checks passing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
