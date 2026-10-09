"""check_citations.py - STUDENT IMPLEMENTS `check`.   Runs INSIDE the sandbox (standard library only).

research.py uploads this file to the sandbox and the lead agent runs it with the `execute` tool:
    python3 /tmp/work/research/check_citations.py [report.md] [sources.json]
It must exit 0 and print "OK: ..." when the report is consistent, else print each problem and exit 1.
"""
import json
import re
import sys

REPORT = "/tmp/work/report/report.md"
SOURCES = "/tmp/work/research/sources.json"

_REF_HEADING = re.compile(r"(?m)^##[ \t]+References[ \t]*$")
_CODE = re.compile(r"```.*?```|`[^`\n]*`", re.DOTALL)        # citations inside code are not citations
_CITATION = re.compile(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\](?!\()")  # [3] [1, 2] [1-3]; not a Markdown link [3](url)
_REF_LINE = re.compile(r"^\s*\[(\d+)\]")
_URL = re.compile(r"https?://[^\s<>]+")
_HEADING = re.compile(r"(?m)^##[ \t]+(.+?)[ \t]*$")
FAMILY_URL = {"arxiv": "https://arxiv.org/abs/", "hf-daily": "https://huggingface.co/papers/",
              "hf-search": "https://huggingface.co/papers/", "web": None}


def structure_problems(body):
    """REPORT_TEMPLATE structure: TL;DR, Background, 3-6 theme sections, Trends and open problems (in this order)."""
    names = [h.strip().lower() for h in _HEADING.findall(body)]
    problems = [f"missing section '## {title}'" for title in ("TL;DR", "Background", "Trends and open problems")
                if title.lower() not in names]
    problems += [f"section '## {name}' appears more than once" for name in sorted({n for n in names
                                                                                     if names.count(n) > 1})]
    if not problems:
        themes = names[names.index("background") + 1:names.index("trends and open problems")]
        if not 3 <= len(themes) <= 6:
            problems.append(f"{len(themes)} theme sections between '## Background' and '## Trends and open problems' "
                            "(need 3 to 6)")
        problems += [f"theme '## {name}' must be about a topic theme: trends and open problems belong in "
                     "'## Trends and open problems' only" for name in themes
                     if "open problem" in name or "trend" in name]
    return problems


def _numbers(group):
    """'1, 2' -> [1, 2];  '1-3' -> [1, 2, 3]."""
    numbers = []
    for part in re.split(r"\s*,\s*", group):
        span = re.fullmatch(r"(\d+)\s*[–-]\s*(\d+)", part)
        if span:
            a, b = int(span.group(1)), int(span.group(2))
            numbers.extend(range(a, b + 1) if 0 <= b - a <= 200 else [a, b])
        else:
            numbers.append(int(part))
    return numbers


def cited_numbers(body):
    """Every source number cited in the report body (grouped forms expanded, code and links ignored)."""
    text = _CODE.sub(" ", body)
    return {n for match in _CITATION.finditer(text) for n in _numbers(match.group(1))}


def check(report_text, sources):
    """Return a list of problem strings (empty list = OK).

    Besides the rules below (GUIDE part 4), it also checks that each source's url matches its family
    (RUBRIC 2.2: arxiv -> https://arxiv.org/abs/..., hf-* -> https://huggingface.co/papers/...) and the
    REPORT_TEMPLATE section structure, so the agent fixes both inside the sandbox before the report is downloaded.

    PSEUDO-CODE:
      problems = []
      if sources is empty: return ["no sources in sources.json"]
      for each source entry:
          n must be an int                       -> problem if not
          url must start with http:// or https://-> problem if not
          the same url must not appear twice     -> problem if duplicated
      split report_text at the heading "## References":
          body = text before it; if the heading is missing -> problem
      cited = set of numbers found as [n] in the BODY only (not in the reference list; use a regex)
      every number in `cited` must exist in sources -> problem "[n] cited but missing from sources.json"
      every source number must be in `cited`        -> problem "source [n] never cited"
      the lines of the References section that start with "[n]" (regex) are the reference lines:
          every source needs exactly ONE reference line (none missing, no number twice, no number that is not a source)
          each reference line holds exactly ONE http(s) URL and it must equal that source's url
          (a line bundling several sources under one number is a problem)
      return problems
    """
    if not isinstance(sources, list) or not sources:
        return ["no sources in sources.json"]
    problems, by_n, seen_urls = [], {}, {}
    for i, entry in enumerate(sources):
        if not isinstance(entry, dict):
            problems.append(f"sources.json entry #{i + 1} is not an object")
            continue
        n, url = entry.get("n"), entry.get("url")
        if not isinstance(n, int) or isinstance(n, bool):
            problems.append(f"sources.json entry #{i + 1}: n={n!r} is not an integer")
            continue
        if n in by_n:
            problems.append(f"source number [{n}] appears twice in sources.json")
        by_n[n] = entry
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            problems.append(f"source [{n}]: url {url!r} does not start with http:// or https://")
        elif url in seen_urls:
            problems.append(f"source [{n}]: url {url} duplicates source [{seen_urls[url]}]")
        else:
            seen_urls[url] = n
        family = entry.get("source")
        if family not in FAMILY_URL:
            problems.append(f"source [{n}]: source {family!r} is not one of {sorted(FAMILY_URL)}")
        elif FAMILY_URL[family] and isinstance(url, str) and not url.startswith(FAMILY_URL[family]):
            problems.append(f"source [{n}]: source '{family}' needs a url starting with {FAMILY_URL[family]} "
                            f"(got {url}); use the canonical url or set source to 'web'")

    headings = list(_REF_HEADING.finditer(report_text))
    if not headings:
        return problems + ["the report has no '## References' heading"]
    body, references = report_text[:headings[-1].start()], report_text[headings[-1].end():]
    problems += structure_problems(body)

    cited = cited_numbers(body)
    problems += [f"[{n}] cited but missing from sources.json" for n in sorted(cited - set(by_n))]
    problems += [f"source [{n}] never cited in the report body" for n in sorted(set(by_n) - cited)]

    ref_lines = {}
    for line in references.splitlines():
        match = _REF_LINE.match(line)
        if match:
            ref_lines.setdefault(int(match.group(1)), []).append(line)
    for n in sorted(ref_lines):
        lines = ref_lines[n]
        if n not in by_n:
            problems.append(f"References line [{n}] is not a source in sources.json")
            continue
        if len(lines) > 1:
            problems.append(f"References has {len(lines)} lines numbered [{n}] (need exactly one)")
        urls = _URL.findall(lines[0])
        if len(urls) != 1:
            problems.append(f"References line [{n}] holds {len(urls)} URLs (need exactly one; never bundle sources)")
        elif urls[0].rstrip(".,;") != by_n[n].get("url"):
            problems.append(f"References line [{n}] URL {urls[0]} differs from sources.json url {by_n[n].get('url')}")
    problems += [f"source [{n}] has no line in References" for n in sorted(set(by_n) - set(ref_lines))]
    return problems


def main(argv):
    report_path = argv[1] if len(argv) > 1 else REPORT
    sources_path = argv[2] if len(argv) > 2 else SOURCES
    try:
        with open(report_path, encoding="utf-8") as f:
            report = f.read()
        with open(sources_path, encoding="utf-8") as f:
            sources = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"cannot read inputs: {exc}")
        return 1
    problems = check(report, sources)
    if problems:
        print("\n".join(problems))
        return 1
    print(f"OK: {len(sources)} sources, all citations resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
