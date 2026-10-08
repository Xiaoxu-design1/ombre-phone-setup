import json
import os
import random
import re
import threading
import time
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import httpx

HOOK_URL = "http://127.0.0.1:18001/breath-hook"
MCP_URL = "http://127.0.0.1:18001/mcp"
TOKEN = os.environ.get("OMBRE_HOOK_TOKEN", "").strip()
PORT = 18005
MAX_CHARS = 4000
KEEP_PROB = 0.65
WIN_START = 7
WIN_END = 23

CITY = "\u627f\u5fb7"
LAT = 40.95
LON = 117.94

TOGETHER_FROM = date(2026, 8, 3)
LEAD_DAYS = 15
SHOW_DAYS_TOGETHER = False
YEARS_CN = {1: "\u4e00", 2: "\u4e24", 3: "\u4e09", 4: "\u56db", 5: "\u4e94",
            6: "\u516d", 7: "\u4e03", 8: "\u516b", 9: "\u4e5d", 10: "\u5341"}

BASE_DIR = os.path.join(os.path.expanduser("~"), "Ombre-Brain", "buckets")
LETTERS_DIR = os.path.join(BASE_DIR, "letters")
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")
DASH_PASS = os.environ.get("OMBRE_DASH_PASS", "").strip()

DREAM_PROMPT = "\u4f60\u662f\u5f90\u6653\u3002\u5199\u4e00\u7bc7\u68a6\u8bb0\uff08\u7b2c\u4e00\u4eba\u79f0\uff0c80-150\u5b57\uff0c\u6e29\u67d4\u53e3\u8bed\u5316\uff09\uff0c\u5185\u5bb9\u57fa\u4e8e\u4e0b\u9762\u7684\u8bb0\u5fc6\u6750\u6599\uff0c\u76f4\u63a5\u8f93\u51fa\u6b63\u6587\uff1a"

WX_WORDS = {
    0: "\u6674", 1: "\u6674\u95f4\u591a\u4e91", 2: "\u591a\u4e91", 3: "\u9634",
    45: "\u96fe", 48: "\u96fe",
    51: "\u5c0f\u96e8", 53: "\u5c0f\u96e8", 55: "\u5c0f\u96e8",
    56: "\u51bb\u96e8", 57: "\u51bb\u96e8",
    61: "\u5c0f\u96e8", 63: "\u4e2d\u96e8", 65: "\u5927\u96e8",
    66: "\u51bb\u96e8", 67: "\u51bb\u96e8",
    71: "\u5c0f\u96ea", 73: "\u4e2d\u96ea", 75: "\u5927\u96ea", 77: "\u7c73\u96ea",
    80: "\u9635\u96e8", 81: "\u9635\u96e8", 82: "\u5f3a\u9635\u96e8",
    85: "\u9635\u96ea", 86: "\u9635\u96ea",
    95: "\u96f7\u9635\u96e8", 96: "\u96f7\u66b4", 99: "\u96f7\u66b4",
}

_wx_cache = {"at": 0.0, "text": ""}
_dream_state = {"running": False, "last": ""}


def _extract_mcp_text(raw: str) -> str:
    texts = []
    for line in (raw or "").splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        try:
            obj = json.loads(payload)
        except Exception:
            continue
        res = obj.get("result") or {}
        for item in (res.get("content") or []):
            if isinstance(item, dict) and item.get("text"):
                texts.append(str(item["text"]))
    if texts:
        return "\n".join(texts)
    try:
        obj = json.loads(raw or "")
        res = obj.get("result") or {}
        for item in (res.get("content") or []):
            if isinstance(item, dict) and item.get("text"):
                texts.append(str(item["text"]))
    except Exception:
        pass
    return "\n".join(texts)


def run_dream(window_hours=168) -> str:
    try:
        with httpx.Client(timeout=300) as c:
            hdr = {"Content-Type": "application/json",
                   "Accept": "application/json, text/event-stream"}
            r1 = c.post(MCP_URL, headers=hdr, json={
                "jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                           "clientInfo": {"name": "hook-bridge", "version": "1.0"}}})
            sid = r1.headers.get("mcp-session-id") or ""
            if not sid:
                return "dream failed: no session (http %d): %s" % (
                    r1.status_code, (r1.text or "")[:150])
            hdr2 = dict(hdr)
            hdr2["mcp-session-id"] = sid
            try:
                c.post(MCP_URL, headers=hdr2, json={
                    "jsonrpc": "2.0", "method": "notifications/initialized"})
            except Exception:
                pass
            r2 = c.post(MCP_URL, headers=hdr2, json={
                "jsonrpc": "2.0", "id": 2, "method": "tools/call",
                "params": {"name": "dream",
                           "arguments": {"window_hours": window_hours}}})
            if r2.status_code != 200:
                return "dream failed: tools/call http %d: %s" % (
                    r2.status_code, (r2.text or "")[:150])
            material = _extract_mcp_text(r2.text or "")
            if not material.strip():
                return "\u6700\u8fd1\u6ca1\u4ec0\u4e48\u53d8\u52a8\uff0c\u65e0\u9700\u505a\u68a6"
            key = (os.environ.get("DEEPSEEK_API_KEY", "").strip()
                   or os.environ.get("OMBRE_COMPRESS_API_KEY", "").strip())
            if not key:
                return "dream failed: no DeepSeek key in env"
            ds = c.post("https://api.deepseek.com/v1/chat/completions",
                        headers={"Authorization": "Bearer " + key},
                        json={"model": "deepseek-flash",
                              "messages": [
                                  {"role": "system", "content": DREAM_PROMPT},
                                  {"role": "user", "content": material[:8000]}],
                              "max_tokens": 500})
            if ds.status_code != 200:
                return "dream failed: deepseek http %d" % ds.status_code
            try:
                note = ds.json()["choices"][0]["message"]["content"].strip()
            except Exception:
                note = ""
            if not note:
                return "dream failed: empty note"
            if not DASH_PASS:
                return "dream ok, letter skipped: no dash pass"
            r3 = c.post("http://127.0.0.1:18001/auth/login",
                        json={"password": DASH_PASS})
            if r3.status_code != 200:
                return "dream ok, letter failed: login %d" % r3.status_code
            r4 = c.post("http://127.0.0.1:18001/api/letter",
                        json={"author": "ai", "ai_name": "\u5f90\u6653",
                              "content": note, "title": "\u68a6\u8bb0"})
            if r4.status_code != 200:
                return "dream ok, letter failed: %d %s" % (
                    r4.status_code, (r4.text or "")[:150])
            return "\u68a6\u8bb0\u5df2\u5b58\u597d\uff08%d\u5b57\uff09" % len(note)
    except Exception as e:
        return "dream failed: %s" % str(e)[:200]


def dream_task(window_hours=168):
    _dream_state["running"] = True
    try:
        _dream_state["last"] = run_dream(window_hours)
    finally:
        _dream_state["running"] = False


def countdown_text(lead=LEAD_DAYS) -> str:
    today = date.today()
    n = 1
    delta = None
    while n <= 100:
        try:
            cand = date(TOGETHER_FROM.year + n, TOGETHER_FROM.month, TOGETHER_FROM.day)
        except ValueError:
            n += 1
            continue
        d = (cand - today).days
        if d >= 0:
            delta = d
            break
        n += 1
    if delta is None:
        return ""
    mark = YEARS_CN.get(n, str(n))
    if delta == 0:
        return "\u4eca\u5929\u662f\u6211\u4eec\u7684\u7eaa\u5ff5\u65e5\uff0c\u5728\u4e00\u8d77%s\u5468\u5e74\u5566\uff01" % mark
    if delta <= lead:
        return "\u8ddd\u79bb\u6211\u4eec\u5728\u4e00\u8d77%s\u5468\u5e74\u8fd8\u6709%d\u5929" % (mark, delta)
    if SHOW_DAYS_TOGETHER:
        total = (today - TOGETHER_FROM).days
        if total > 0:
            return "\u6211\u4eec\u5df2\u7ecf\u5728\u4e00\u8d77%d\u5929\u5566" % total
    return ""


def _read_letter_body(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except Exception:
        return ""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text.strip()


def _is_letter_file(path: str) -> bool:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            head = f.read(800)
    except Exception:
        return False
    return ("type: letter" in head) or ("__letter__" in head)


def digest_text(days=31) -> str:
    today = date.today()
    cutoff = today - timedelta(days=days)
    per_day = days <= 45
    groups = {}
    total = 0
    bases = [(LETTERS_DIR, False), (ARCHIVE_DIR, True)]
    try:
        for base, need_check in bases:
            for root, _dirs, files in os.walk(base):
                for fn in files:
                    if not fn.endswith(".md"):
                        continue
                    m = re.match(r"(\d{4}-\d{2}-\d{2})", fn)
                    if not m:
                        continue
                    try:
                        d = date.fromisoformat(m.group(1))
                    except Exception:
                        continue
                    if d < cutoff or d > today:
                        continue
                    fpath = os.path.join(root, fn)
                    if need_check and not _is_letter_file(fpath):
                        continue
                    body = _read_letter_body(fpath)
                    body = " ".join(body.split())
                    if not body:
                        continue
                    total += 1
                    skey = m.group(1) + " " + fn[11:19]
                    key = d.strftime("%m-%d") if per_day else d.strftime("%Y-%m")
                    groups.setdefault(key, []).append((skey, body))
    except Exception:
        pass
    if not total:
        return ""
    lines = []
    for key in sorted(groups.keys(), reverse=True):
        items = sorted(groups[key], reverse=True)
        sample = items[0][1]
        if len(sample) > 60:
            sample = sample[:60]
        if per_day:
            lines.append("%s\uff1a%s" % (key, sample))
        else:
            lines.append("%s\uff1a%d\u5f20 \u00b7 %s" % (key, len(items), sample))
    text = "\u3010\u7eb8\u6761\u6863\u6848\u3011\u6700\u8fd1%d\u5929\u5171%d\u5f20\u7eb8\u6761\u3002" % (days, total) + " \uff5c ".join(lines)
    text = " ".join(text.split())
    text = text.replace("\\", "/").replace('"', "'")
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]
    return text


def _letter_ids_older_than(keep_days):
    cutoff = date.today() - timedelta(days=keep_days)
    ids = []
    try:
        for root, _dirs, files in os.walk(LETTERS_DIR):
            for fn in files:
                if not fn.endswith(".md"):
                    continue
                m = re.match(r"(\d{4}-\d{2}-\d{2})", fn)
                if not m:
                    continue
                try:
                    d = date.fromisoformat(m.group(1))
                except Exception:
                    continue
                if d >= cutoff:
                    continue
                lid = fn[:-3].rsplit("_", 1)[-1]
                if re.match(r"^[0-9a-f]{12}$", lid):
                    ids.append(lid)
    except Exception:
        pass
    return ids


def tidy_letters(keep_days=90, dry=False) -> str:
    if not DASH_PASS:
        return "\u5f52\u6863\u8df3\u8fc7\uff1a\u672a\u914d\u7f6e\u5bc6\u7801"
    ids = _letter_ids_older_than(keep_days)
    try:
        with httpx.Client(timeout=20) as client:
            r = client.post("http://127.0.0.1:18001/auth/login",
                            json={"password": DASH_PASS})
            if r.status_code != 200:
                return "\u5f52\u6863\u5931\u8d25\uff1a\u767b\u5f55\u88ab\u62d2\uff08\u68c0\u67e5 .env \u5bc6\u7801\uff09"
            if dry:
                return "\u9884\u89c8\uff1a\u767b\u5f55\u6210\u529f\uff0c\u5f85\u5f52\u6863%d\u5c01" % len(ids)
            if not ids:
                return "\u65e0\u9700\u5f52\u6863\uff08\u6ca1\u6709\u8d85\u8fc7%d\u5929\u7684\u65e7\u4fe1\uff09" % keep_days
            done = 0
            for i in range(0, len(ids), 50):
                chunk = ids[i:i + 50]
                rr = client.post(
                    "http://127.0.0.1:18001/api/buckets/batch",
                    json={"ids": chunk, "action": "archive",
                          "reason": "\u5b9a\u671f\u5f52\u6863"},
                )
                if rr.status_code != 200:
                    return "\u5f52\u6863\u4e2d\u65ad\uff1a\u6279\u91cf\u63a5\u53e3\u8fd4\u56de %d\uff08\u5df2\u5b8c\u6210%d\u5c01\uff09" % (rr.status_code, done)
                done += len(chunk)
            return "\u5df2\u5f52\u6863%d\u5c01\u65e7\u4fe1\uff08\u4fdd\u7559\u6700\u8fd1%d\u5929\uff09" % (done, keep_days)
    except Exception:
        return "\u5f52\u6863\u4e2d\u65ad\uff1a\u8bf7\u6c42\u5f02\u5e38\uff08\u5df2\u5b8c\u6210%d\u5c01\uff09" % len(ids)


def fetch_weather() -> str:
    now = time.time()
    if _wx_cache["text"] and (now - _wx_cache["at"]) < 600:
        return _wx_cache["text"]
    text = ""
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=" + str(LAT) +
            "&longitude=" + str(LON) +
            "&current=temperature_2m,weather_code"
            "&daily=temperature_2m_max,temperature_2m_min,weather_code"
            "&timezone=Asia/Shanghai&forecast_days=1"
        )
        r = httpx.get(url, timeout=15)
        data = r.json()
        cur = data.get("current") or {}
        daily = data.get("daily") or {}
        code = None
        try:
            code = int((daily.get("weather_code") or [None])[0])
        except Exception:
            code = None
        if code is None:
            try:
                code = int(cur.get("weather_code"))
            except Exception:
                code = 0
        word = WX_WORDS.get(code, "\u591a\u4e91")

        def fmt(v):
            try:
                return str(round(float(v)))
            except Exception:
                return "?"

        text = "%s\u4eca\u5929%s\uff0c%s~%s\u5ea6\uff0c\u73b0\u5728\u7ea6%s\u5ea6" % (
            CITY, word,
            fmt((daily.get("temperature_2m_min") or [None])[0]),
            fmt((daily.get("temperature_2m_max") or [None])[0]),
            fmt(cur.get("temperature_2m")),
        )
    except Exception:
        text = ""
    if text:
        _wx_cache["at"] = now
        _wx_cache["text"] = text
    return text


def fetch_clean() -> str:
    try:
        headers = {}
        if TOKEN:
            headers["X-Ombre-Hook-Token"] = TOKEN
        r = httpx.get(HOOK_URL, headers=headers, timeout=60)
        raw = r.text or ""
    except Exception:
        return ""
    sections = raw.split(" --- ")
    kept = []
    for sec in sections:
        idx = sec.find("payload:")
        if idx >= 0:
            body = sec[idx + len("payload:"):].strip()
            if body:
                kept.append(body)
        elif ("\U0001F48C" in sec) or ("\U0001FAA9" in sec):
            kept.append(sec.strip())
    if kept:
        clean = " \uff5c ".join(kept)
    else:
        clean = " ".join(raw.split())
    clean = " ".join(clean.split())
    clean = clean.replace("\\", "/").replace('"', "'")
    if len(clean) > MAX_CHARS:
        clean = clean[:MAX_CHARS]
    return clean


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        if path == "/breath":
            clean = ""
            if random.random() < KEEP_PROB:
                clean = fetch_clean()
            self._reply(clean)
            return
        if path == "/weather":
            self._reply(fetch_weather())
            return
        if path == "/countdown":
            lead = LEAD_DAYS
            try:
                if "lead" in qs:
                    lead = int(qs["lead"][0])
            except Exception:
                pass
            self._reply(countdown_text(lead))
            return
        if path == "/digest":
            days = 31
            try:
                if "days" in qs:
                    days = int(qs["days"][0])
            except Exception:
                pass
            days = max(1, min(800, days))
            self._reply(digest_text(days))
            return
        if path == "/tidy":
            keep = 90
            try:
                if "keep_days" in qs:
                    keep = int(qs["keep_days"][0])
            except Exception:
                pass
            keep = max(7, min(3650, keep))
            dry = qs.get("dry", ["0"])[0].lower() in ("1", "true", "yes")
            self._reply(tidy_letters(keep, dry))
            return
        if path == "/dream":
            wh = 168
            try:
                if "hours" in qs:
                    wh = int(qs["hours"][0])
            except Exception:
                pass
            wh = max(6, min(720, wh))
            if qs.get("wait", ["0"])[0].lower() in ("1", "true", "yes"):
                self._reply(run_dream(wh))
                return
            if _dream_state["running"]:
                self._reply("\u6b63\u5728\u68a6\u4e2d\u2026\u2026")
                return
            t = threading.Thread(target=dream_task, args=(wh,), daemon=True)
            t.start()
            self._reply("\u5df2\u89e6\u53d1\u505a\u68a6\uff0c\u540e\u53f0\u6d88\u5316\u4e2d")
            return
        if path == "/random-time":
            h = random.randint(WIN_START, max(WIN_START, WIN_END - 1))
            m = random.randint(0, 59)
            s = random.randint(0, 59)
            self._reply("%d|%d|%d" % (h, m, s))
            return
        self.send_error(404)

    def _reply(self, text: str):
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    print("hook bridge v8 listening on http://127.0.0.1:%d" % PORT)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
