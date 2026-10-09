"""research.py - STUDENT IMPLEMENTS.  The main script.   Guide: GUIDE.md, part 3.

Usage:  python research.py "survey about world model"
Result: reports/<slug>.md   reports/<slug>.sources.json   reports/<slug>.meta.json
"""
import datetime
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path

import check_citations
from agents import (FINALIZER_PATH, NOTES_DIR, RECURSION_LIMIT, REPORT_PATH, SOURCES_PATH, VALIDATOR_PATH, WORKDIR,
                    build_lead_agent)
from model import make_model
from sandbox import download, open_sandbox, upload

ROOT = Path(__file__).parent
REPORTS = ROOT / "reports"
VALIDATOR_SOURCE = ROOT / "check_citations.py"
FINALIZER_SOURCE = ROOT / "finalize_citations.py"   # provided: uploaded next to your validator


def slugify(topic):
    """Turn a topic into a safe file name: lower case, runs of non-word characters become one "-", max 60 chars,
    never empty (fall back to "topic"). The topic is user input: "../../x" must not escape reports/."""
    slug = re.sub(r"[^a-z0-9]+", "-", str(topic or "").lower()).strip("-")[:60].strip("-")
    return slug or "topic"


def build_prompt(topic):
    """The user message sent to the lead agent."""
    today = datetime.date.today().isoformat()
    return (f"Topic: {topic}\n"
            f"Today is {today}; 'recent' means the last two years.\n"
            f"Produce the cited survey report for this topic by following your steps 1-8: plan, delegate the "
            f"sub-questions to researchers in parallel (notes in {NOTES_DIR}/), check the notes, merge {SOURCES_PATH} "
            f"(at least 3 source families), write the body of {REPORT_PATH}, run the finalizer, run the validator "
            f"until it prints OK, and spot-check claims with the citation-checker.")


def summarize(messages, elapsed, model_name):
    """Return {"model", "elapsed_s", "subagent_calls", "tool_calls": {name: count}, "tokens": {"input", "output"}}.

    Lead messages only: subagent tokens are not included, so `tokens` undercounts the real cost.
    """
    calls, tokens = Counter(), {"input": 0, "output": 0}
    for message in messages:
        for call in getattr(message, "tool_calls", None) or []:
            calls[call["name"]] += 1
        usage = getattr(message, "usage_metadata", None) or {}
        tokens["input"] += int(usage.get("input_tokens") or 0)
        tokens["output"] += int(usage.get("output_tokens") or 0)
    return {"model": model_name, "elapsed_s": round(elapsed, 1), "subagent_calls": calls.get("task", 0),
            "tool_calls": dict(sorted(calls.items())), "tokens": tokens}


def save_outputs(backend, topic, messages, elapsed, model_name, reports_dir=REPORTS):
    """Download the report from the sandbox and write the three files into reports_dir. Return the report path.

    A failed run (missing/empty report, missing or invalid sources.json, a report the validator rejects) raises
    RuntimeError and writes NOTHING.
    """
    files = download(backend, [REPORT_PATH, SOURCES_PATH])
    report, raw_sources = files.get(REPORT_PATH), files.get(SOURCES_PATH)
    if not report or not report.strip():
        raise RuntimeError(f"the agent produced no report at {REPORT_PATH}")
    if not raw_sources:
        raise RuntimeError(f"the agent produced no {SOURCES_PATH}")
    try:
        sources = json.loads(raw_sources.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise RuntimeError(f"{SOURCES_PATH} is not valid JSON: {exc}") from exc
    if not isinstance(sources, list) or not sources or not all(isinstance(s, dict) for s in sources):
        raise RuntimeError(f"{SOURCES_PATH} must be a non-empty JSON list of objects")
    # the agent may stop (call limit, or it gives up) before the in-sandbox validator printed OK: that is a failed run
    problems = check_citations.check(report.decode("utf-8", errors="replace"), sources)
    if problems:
        raise RuntimeError("the report does not pass check_citations.py: " + "; ".join(problems[:5]))

    meta = {"topic": topic, **summarize(messages, elapsed, model_name), "n_sources": len(sources),
            "source_families": sorted({str(s.get("source")) for s in sources if s.get("source")})}
    slug = slugify(topic)
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / f"{slug}.sources.json").write_bytes(raw_sources)     # byte-for-byte what the sandbox validated
    (reports_dir / f"{slug}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                                                   encoding="utf-8")
    report_path = reports_dir / f"{slug}.md"
    report_path.write_bytes(report)
    return report_path


def model_label(model):
    return str(getattr(model, "model_name", None) or getattr(model, "model", None) or os.getenv("LAB_MODEL") or "?")


def main(topic):
    """Return the process exit code (0 ok, 1 failed run, 2 no topic)."""
    topic = " ".join(str(topic or "").split())
    if not topic:
        print('usage: python research.py "<topic>"', file=sys.stderr)
        return 2
    model = make_model()
    start = time.monotonic()
    try:
        with open_sandbox() as backend:   # the sandbox is always stopped and removed, even on errors
            backend.execute(f"mkdir -p {NOTES_DIR} {WORKDIR}/report")
            upload(backend, {VALIDATOR_PATH: VALIDATOR_SOURCE.read_bytes(),
                             FINALIZER_PATH: FINALIZER_SOURCE.read_bytes()})
            agent = build_lead_agent(backend, model)
            result = agent.invoke({"messages": [{"role": "user", "content": build_prompt(topic)}]},
                                  config={"recursion_limit": RECURSION_LIMIT})
            path = save_outputs(backend, topic, result["messages"], time.monotonic() - start, model_label(model))
    except Exception as exc:  # noqa: BLE001 - a failed run exits 1 and leaves no report behind
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"report saved: {path} ({round(time.monotonic() - start, 1)} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(" ".join(sys.argv[1:])))
