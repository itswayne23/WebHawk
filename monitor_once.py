import json, os, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import requests

BASE = Path(__file__).resolve().parent
SITES = BASE / "config" / "sites.json"
STATE = BASE / "state" / "status.json"
IST = ZoneInfo("Asia/Kolkata")
TOKEN, CHAT = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
LIMIT = int(os.getenv("FAILURES_BEFORE_ALERT", "3"))

def now():
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")

def send(text):
    if not TOKEN or not CHAT:
        raise RuntimeError("Telegram secrets are missing")
    r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      json={"chat_id": CHAT, "text": text}, timeout=20)
    r.raise_for_status()
    if not r.json().get("ok"):
        raise RuntimeError("Telegram API rejected message")

def main():
    urls = json.loads(SITES.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8"))
    records = state.setdefault("sites", {})
    lines, counts = [], {"ONLINE":0,"SLOW":0,"DOWN":0,"CHECKING":0}
    for url in urls:
        old = records.get(url, {})
        old_status, failures = old.get("status","UNKNOWN"), int(old.get("failures",0))
        started, code, error = time.perf_counter(), None, None
        try:
            res = requests.get(url, timeout=15, allow_redirects=True,
                               headers={"User-Agent":"WEBWATCH/1.0"})
            code = res.status_code
            ms = round((time.perf_counter()-started)*1000)
            status = ("SLOW" if ms >= 5000 else "ONLINE") if 200 <= code < 400 else "DOWN"
            if status == "DOWN": error = f"HTTP {code}"
        except requests.RequestException as exc:
            ms, status, error = round((time.perf_counter()-started)*1000), "DOWN", str(exc)[:250]
        incident = old.get("incident_started")
        if status == "DOWN":
            failures += 1
            if failures < LIMIT:
                status = "CHECKING"
            elif old_status != "DOWN":
                incident = now()
                send(f"🚨 WEBWATCH OUTAGE\nWebsite: {url}\nDetected: {incident}\nFailures: {failures}\nDetail: {error}")
        else:
            failures = 0
            if old_status == "DOWN":
                send(f"✅ WEBWATCH RECOVERY\nWebsite: {url}\nStatus: {status}\nRecovered: {now()}\nResponse: {ms} ms")
            incident = None
        records[url] = {"status":status,"failures":failures,"http_status":code,
                        "response_ms":ms,"last_checked":now(),"incident_started":incident}
        counts[status] = counts.get(status,0)+1
        lines.append(f"{status} | {url} | HTTP {code or '-'} | {ms} ms")
        print(lines[-1])
    STATE.write_text(json.dumps(state,indent=2),encoding="utf-8")
    print("Cycle complete:",len(urls),"URLs",counts)
    if os.getenv("SEND_HOURLY_REPORT","false").lower()=="true":
        report="📊 WEBWATCH HOURLY REPORT\n"+f"Time: {now()}\nTotal: {len(urls)} | "+ " | ".join(f"{k}: {v}" for k,v in counts.items())+"\n\n"+"\n".join(lines)
        send(report[:4000])
if __name__=="__main__":
    main()
