"""tools.py - STUDENT IMPLEMENTS.  Source tools for the research agents.   Guide: GUIDE.md, part 1.

Rules for every tool:
  * runs on the HOST (not in the sandbox): API keys must never enter the sandbox;
  * returns a STRING (JSON text of compact records) and NEVER raises:
        "NO RESULTS"  when the source answers with nothing,
        "ERROR: ..."  when the source keeps failing after the retries (the agent then tries another source);
  * the docstring is the tool description the LLM reads: keep it precise (what it does, what it returns, when to use it).
Try your tools without any agent:   python tools.py
"""
import json
import os
import random
import re
import threading
import time
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import httpx
from langchain_core.tools import tool

# ---- constants (given) ----
ARXIV_URL = "https://export.arxiv.org/api/query"  # https only: http answers 301
HF_DAILY_URL = "https://huggingface.co/api/daily_papers"
HF_SEARCH_URL = "https://huggingface.co/api/papers/search"
EXA_URL = "https://mcp.exa.ai/mcp"

RETRYABLE_STATUS = {429, 500, 502, 503, 504}
TIMEOUT = httpx.Timeout(30.0, connect=10.0)
SUMMARY_CHARS = 600          # keep records compact: they go straight into the model context
WEB_SEARCH_CHARS = 8000
WEB_FETCH_CHARS = 12000
ARXIV_MIN_INTERVAL = 3.0     # arXiv API etiquette: at least 3 s between two calls
ATOM = {"a": "http://www.w3.org/2005/Atom"}
BOOLEAN_WORDS = {"AND", "OR", "NOT", "ANDNOT"}


class RetryableError(Exception):
    """Given. Raise it inside a call to ask with_retry to wait and try again (retry_after in seconds, optional)."""

    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


# ---- TODO 1: retry helper ----
def with_retry(fn, *, attempts=5, base=1.0, cap=30.0):
    """Call fn(); when it raises RetryableError, wait and call it again (at most `attempts` calls in total).

    Wait = the server's Retry-After when it sent one, else exponential backoff base * 2**attempt plus random jitter;
    always capped at `cap` seconds. The last failure is re-raised without sleeping. Any other exception is not retried.
    """
    for attempt in range(attempts):
        try:
            return fn()
        except RetryableError as exc:
            if attempt == attempts - 1:
                raise
            if exc.retry_after is not None:
                delay = min(float(exc.retry_after), cap)
            else:
                delay = min(cap, base * 2 ** attempt + random.uniform(0, base))
            time.sleep(max(0.0, delay))
    raise RuntimeError("with_retry: attempts must be >= 1")


def _retry_after(response):
    """Seconds from a Retry-After header (delta-seconds or HTTP date), else None."""
    value = (response.headers.get("Retry-After") or "").strip()
    if not value:
        return None
    if value.isdigit():
        return float(value)
    try:
        return max(0.0, parsedate_to_datetime(value).timestamp() - time.time())
    except (TypeError, ValueError, IndexError):
        return None


def _request(method, url, **kwargs):
    """One HTTP call. Transient failures (429/5xx, network errors) -> RetryableError; other HTTP errors raise."""
    try:
        response = httpx.request(method, url, timeout=TIMEOUT, follow_redirects=True, **kwargs)
    except httpx.TransportError as exc:
        raise RetryableError(f"{type(exc).__name__}: {exc}") from exc
    if response.status_code in RETRYABLE_STATUS:
        raise RetryableError(f"HTTP {response.status_code}", retry_after=_retry_after(response))
    response.raise_for_status()
    return response


def _clean(text):
    return " ".join(str(text or "").split())


def _short(text, limit=SUMMARY_CHARS):
    text = _clean(text)
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def _short_block(text, limit):
    """Truncate multi-line text without collapsing its line structure."""
    return text if len(text) <= limit else text[:limit].rstrip() + "\n...[truncated]"


def _error(exc):
    return f"ERROR: {type(exc).__name__}: {_redact(str(exc))}"


# ---- TODO 2: arXiv ----
_arxiv_lock = threading.Lock()   # researchers run in parallel: serialise arXiv calls to keep the 3 s spacing
_arxiv_last_call = [0.0]


def _arxiv_terms(query):
    """Keep only word/number/hyphen tokens (LLM-written query): quotes, colons and stray boolean words are dropped."""
    terms = re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", str(query or ""))
    return [t for t in terms if t.upper() not in BOOLEAN_WORDS][:8]


def _arxiv_get(params):
    with _arxiv_lock:
        wait = ARXIV_MIN_INTERVAL - (time.monotonic() - _arxiv_last_call[0])
        if wait > 0:
            time.sleep(wait)
        try:
            return _request("GET", ARXIV_URL, params=params)
        finally:
            _arxiv_last_call[0] = time.monotonic()


def _parse_arxiv(xml_text):
    records = []
    for entry in ET.fromstring(xml_text).findall("a:entry", ATOM):
        raw_id = entry.findtext("a:id", default="", namespaces=ATOM)
        if "/abs/" not in raw_id:              # arXiv reports query errors as an entry without /abs/
            continue
        paper_id = re.sub(r"v\d+$", "", raw_id.split("/abs/", 1)[1].strip())
        records.append({
            "id": paper_id,
            "url": f"https://arxiv.org/abs/{paper_id}",
            "published": entry.findtext("a:published", default="", namespaces=ATOM)[:10],
            "title": _clean(entry.findtext("a:title", default="", namespaces=ATOM)),
            "summary": _short(entry.findtext("a:summary", default="", namespaces=ATOM)),
        })
    return records


@tool
def arxiv_search(query: str, max_results: int = 10, sort: str = "date") -> str:
    """Search arXiv papers by a few plain keywords (e.g. "world model survey").
    sort="date" (default): newest submissions first, for the latest preprints.
    sort="relevance": best keyword matches first, to find well-known foundational papers or surveys.
    Returns a JSON list of {id, url, published, title, summary}; url is https://arxiv.org/abs/<id>.
    "NO RESULTS" or "ERROR: ..." otherwise."""
    try:
        terms = _arxiv_terms(query)
        if not terms:
            return "NO RESULTS"
        sort_by = "relevance" if str(sort).strip().lower() == "relevance" else "submittedDate"
        params = {"search_query": " AND ".join(f"all:{t}" for t in terms), "sortBy": sort_by,
                  "sortOrder": "descending", "start": 0, "max_results": max(1, min(int(max_results), 30))}
        response = with_retry(lambda: _arxiv_get(params), attempts=6, base=3.0, cap=60.0)
        records = _parse_arxiv(response.text)
        return json.dumps(records, ensure_ascii=False) if records else "NO RESULTS"
    except Exception as exc:  # noqa: BLE001 - a tool never raises
        return _error(exc)


# ---- TODO 3: Hugging Face ----
def _hf_record(item):
    paper = item.get("paper") or {}
    paper_id = str(paper.get("id") or "").strip()
    if not paper_id:
        return None
    return {
        "id": paper_id,
        "url": f"https://huggingface.co/papers/{paper_id}",
        "published": str(paper.get("publishedAt") or item.get("publishedAt") or "")[:10],
        "title": _clean(paper.get("title") or item.get("title")),
        "summary": _short(paper.get("ai_summary") or paper.get("summary") or item.get("summary")),
        "upvotes": int(paper.get("upvotes") or 0),
        "github": paper.get("githubRepo") or None,
        "stars": int(paper.get("githubStars") or 0) or None,
    }


def _hf_get(url, params):
    data = with_retry(lambda: _request("GET", url, params=params).json(), attempts=5, base=1.0, cap=30.0)
    if not isinstance(data, list):
        raise ValueError(f"unexpected Hugging Face answer: {str(data)[:200]}")
    return [record for record in map(_hf_record, data) if record]


@tool
def hf_daily_papers(limit: int = 30, date: str = "", keyword: str = "") -> str:
    """Hugging Face Daily Papers = what is trending in AI research. Returns a JSON list of
    {id, url, published, title, summary, upvotes, github, stars} sorted by upvotes (at most 20 records).
    `date` is YYYY-MM-DD (empty = latest). `keyword` keeps papers whose title/summary contain ALL its words
    (case-insensitive); there is no topic search on this endpoint (use hf_search_papers for a topic)."""
    try:
        params = {"limit": max(1, min(int(limit), 100))}
        if str(date).strip():
            params["date"] = str(date).strip()
        records = _hf_get(HF_DAILY_URL, params)
        words = str(keyword or "").lower().split()
        if words:
            records = [r for r in records if all(w in f"{r['title']} {r['summary']}".lower() for w in words)]
        records.sort(key=lambda r: r["upvotes"], reverse=True)
        return json.dumps(records[:20], ensure_ascii=False) if records else "NO RESULTS"
    except Exception as exc:  # noqa: BLE001
        return _error(exc)


@tool
def hf_search_papers(query: str, limit: int = 10) -> str:
    """Search Hugging Face papers by topic (semantic search over papers listed on huggingface.co/papers).
    Returns a JSON list of {id, url, published, title, summary, upvotes, github, stars};
    url is https://huggingface.co/papers/<id>. "NO RESULTS" or "ERROR: ..." otherwise."""
    try:
        if not _clean(query):
            return "NO RESULTS"
        records = _hf_get(HF_SEARCH_URL, {"q": _clean(query), "limit": max(1, min(int(limit), 50))})
        return json.dumps(records, ensure_ascii=False) if records else "NO RESULTS"
    except Exception as exc:  # noqa: BLE001
        return _error(exc)


# ---- TODO 4: web search / fetch through the Exa MCP endpoint ----
def _exa_key():
    return (os.getenv("EXA_API_KEY") or "").strip()


def _redact(text):
    """Never leak the Exa key: it travels in the endpoint URL, so it can appear in exception text."""
    text = re.sub(r"(exaApiKey=)[^&\s'\"]+", r"\1***", str(text))
    key = _exa_key()
    return text.replace(key, "***") if key else text


def _sse_messages(response):
    """JSON-RPC messages of an MCP answer: server-sent events ("data: {...}" lines) or plain JSON."""
    if "text/event-stream" in response.headers.get("content-type", ""):
        return [json.loads(line[5:].strip()) for line in response.text.splitlines()
                if line.startswith("data:") and line[5:].strip()]
    return [response.json()]


def _exa_once(name, arguments):
    url = f"{EXA_URL}?exaApiKey={_exa_key()}" if _exa_key() else EXA_URL
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
    response = _request("POST", url, json=payload,
                        headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    for message in _sse_messages(response):
        if message.get("error"):
            raise RuntimeError(f"Exa JSON-RPC error: {message['error'].get('message', message['error'])}")
        result = message.get("result")
        if result is None:
            continue
        text = "\n\n".join(part.get("text", "") for part in result.get("content", []) if part.get("type") == "text")
        # free tier: rate limiting is HTTP 200 + a flag in result._meta (and a text message) -> retry
        if (result.get("_meta") or {}).get("ai.exa/rateLimited") or "hit Exa's free MCP rate limit" in text:
            raise RetryableError("Exa rate limited")
        if result.get("isError"):
            raise RuntimeError(f"Exa tool error: {text[:300]}")
        return text.strip()
    raise RuntimeError("Exa answered without a JSON-RPC result")


def _exa_call(name, arguments):
    return with_retry(lambda: _exa_once(name, arguments), attempts=6, base=5.0, cap=60.0)


@tool
def web_search(query: str, objective: str = "", num_results: int = 5) -> str:
    """Search the web (Exa) for blogs, surveys, project pages and news. `query`: a few keywords; `objective`: one
    sentence describing the ideal page. Returns clean text of the top results, each with Title, URL, Published and
    highlights. "NO RESULTS" or "ERROR: ..." otherwise."""
    try:
        if not _clean(query):
            return "NO RESULTS"
        arguments = {"query": _clean(query),
                     "objective": _clean(objective) or f"Find authoritative, factual pages about: {_clean(query)}",
                     "numResults": max(1, min(int(num_results), 10))}
        text = _exa_call("web_search_exa", arguments)
        return _short_block(text, WEB_SEARCH_CHARS) if text else "NO RESULTS"
    except Exception as exc:  # noqa: BLE001
        return _error(exc)


@tool
def web_fetch(url: str) -> str:
    """Read the full content of one web page (e.g. an arXiv abstract page or a blog post) as markdown, to verify
    details. Long pages are truncated to about 12000 characters. "NO RESULTS" or "ERROR: ..." otherwise."""
    try:
        url = str(url or "").strip()
        if not url.startswith(("http://", "https://")):
            return "ERROR: ValueError: url must start with http:// or https://"
        text = _exa_call("web_fetch_exa", {"urls": [url]})
        return _short_block(text, WEB_FETCH_CHARS) if text else "NO RESULTS"
    except Exception as exc:  # noqa: BLE001
        return _error(exc)


# ---- TODO 5: registry (the researcher subagent gets exactly these) ----
SOURCE_TOOLS = [arxiv_search, hf_daily_papers, hf_search_papers, web_search, web_fetch]


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    for name, fn, args in [
        ("arxiv_search", arxiv_search, {"query": "world model", "max_results": 3}),
        ("hf_daily_papers", hf_daily_papers, {"limit": 20}),
        ("hf_search_papers", hf_search_papers, {"query": "world model", "limit": 3}),
        ("web_search", web_search, {"query": "survey paper on world models", "num_results": 2}),
        ("web_fetch", web_fetch, {"url": "https://arxiv.org/abs/1803.10122"}),
    ]:
        try:
            print(f"== {name}\n{fn.invoke(args)[:400]}\n")
        except NotImplementedError as exc:
            print(f"== {name}: not implemented yet ({exc})\n")
