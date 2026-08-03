#!/usr/bin/env python3
"""kie.py — Kommandozeilen-Helfer für die kie.ai-API (nur Python-Standardbibliothek).

Befehle:
  set-key KEY                     API-Key einmalig lokal speichern (chmod 600)
  key-status                      Zeigt, ob und woher ein API-Key geladen wird
  credit                          Guthaben abfragen (Credits; 1 Credit ~ 0,005 USD)
  upload DATEI [DATEI...]         Datei(en) hochladen, gibt downloadUrl zurück (24 h gültig)

  create MODELL --input JSON      Task über die Jobs-API anlegen (Markt-Modelle)
  status TASKID                   Task-Status einmalig abfragen (Jobs-API)
  wait TASKID                     Pollen bis success/fail (Jobs-API)
  run MODELL --input JSON --out D Task anlegen, warten, Ergebnisse herunterladen

  veo-create --input JSON         Veo-3-Video-Task anlegen (eigener Endpoint)
  veo-status TASKID               Veo-Task-Status einmalig abfragen
  veo-wait TASKID                 Pollen bis Erfolg/Fehler (Veo)
  veo-run --input JSON --out D    Veo-Task anlegen, warten, herunterladen

  post PFAD --json JSON           Generischer POST auf api.kie.ai (z. B. /api/v1/generate für Suno)
  get PFAD [--param k=v ...]      Generischer GET auf api.kie.ai
  download URL [URL...] --out D   Ergebnis-URLs herunterladen

Authentifizierung: Umgebungsvariable KIE_AI_API_KEY (oder KIE_API_KEY),
alternativ gespeicherter Key aus ~/.config/mach/config.json (via set-key).
Alle Ausgaben sind JSON (eine Struktur pro Zeile), Fehler gehen nach stderr mit Exitcode != 0.
"""

import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

API_BASE = "https://api.kie.ai"
UPLOAD_BASE = "https://kieai.redpandaai.co"
USD_PER_CREDIT = 0.005

JOBS_CREATE = "/api/v1/jobs/createTask"
JOBS_RECORD = "/api/v1/jobs/recordInfo"
VEO_CREATE = "/api/v1/veo/generate"
VEO_RECORD = "/api/v1/veo/record-info"
CREDIT_PATH = "/api/v1/chat/credit"
UPLOAD_STREAM = "/api/file-stream-upload"


def die(msg, code=1):
    print(f"FEHLER: {msg}", file=sys.stderr)
    sys.exit(code)


def config_path():
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(
        os.path.expanduser("~"), ".config"
    )
    return os.path.join(base, "mach", "config.json")


def load_config():
    try:
        with open(config_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def api_key():
    key = (
        os.environ.get("KIE_AI_API_KEY")
        or os.environ.get("KIE_API_KEY")
        or load_config().get("api_key")
    )
    if not key:
        die(
            "Kein API-Key gefunden. Entweder die Umgebungsvariable KIE_AI_API_KEY "
            "setzen oder den Key einmalig speichern mit: kie.py set-key DEIN_KEY "
            "(Key erstellen unter https://kie.ai/api-key)."
        )
    return key


def request(method, url, body=None, headers=None, retries=3):
    hdrs = {"Authorization": f"Bearer {api_key()}"}
    if headers:
        hdrs.update(headers)
    data = None
    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body).encode("utf-8")
            hdrs.setdefault("Content-Type", "application/json")
        else:
            data = body
    last_err = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                payload = resp.read().decode("utf-8")
                try:
                    return json.loads(payload)
                except json.JSONDecodeError:
                    return {"raw": payload}
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            if e.code == 429 and attempt < retries - 1:
                time.sleep(5 * (attempt + 1))  # Rate-Limit: 20 Requests / 10 s
                last_err = f"HTTP 429 (Rate-Limit): {detail}"
                continue
            if e.code == 401:
                die("HTTP 401 – API-Key ungültig oder abgelaufen (KIE_AI_API_KEY prüfen).")
            die(f"HTTP {e.code} bei {url}: {detail}")
        except urllib.error.URLError as e:
            last_err = str(e)
            if attempt < retries - 1:
                time.sleep(2 ** (attempt + 1))
                continue
    die(f"Netzwerkfehler bei {url}: {last_err}")


def check_code(resp, context):
    # kie.ai antwortet mit {"code": 200, "msg": ..., "data": ...}
    code = resp.get("code")
    if code not in (200, None):
        die(f"{context}: API-Fehler code={code}, msg={resp.get('msg')}")
    return resp.get("data", resp)


def out(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------- Befehle


def cmd_set_key(args):
    path = config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cfg = load_config()
    cfg["api_key"] = args.key.strip()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(cfg, f)
    os.chmod(path, 0o600)
    out({"gespeichert": path, "hinweis": "Datei ist nur für den aktuellen Benutzer lesbar (600)."})


def cmd_key_status(_args):
    if os.environ.get("KIE_AI_API_KEY") or os.environ.get("KIE_API_KEY"):
        source = "Umgebungsvariable"
    elif load_config().get("api_key"):
        source = f"Konfigdatei ({config_path()})"
    else:
        source = None
    if source:
        key = api_key()
        masked = key[:4] + "…" + key[-4:] if len(key) > 10 else "…"
        out({"vorhanden": True, "quelle": source, "key": masked})
    else:
        out({"vorhanden": False, "quelle": None})


def cmd_credit(_args):
    data = check_code(request("GET", API_BASE + CREDIT_PATH), "Guthaben")
    credits = data if isinstance(data, (int, float)) else data.get("credits", data)
    result = {"credits": credits}
    if isinstance(credits, (int, float)):
        result["usd_approx"] = round(credits * USD_PER_CREDIT, 2)
    out(result)


def cmd_upload(args):
    results = []
    for path in args.files:
        if not os.path.isfile(path):
            die(f"Datei nicht gefunden: {path}")
        filename = os.path.basename(path)
        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        boundary = uuid.uuid4().hex
        with open(path, "rb") as f:
            content = f.read()

        parts = []
        for name, value in (("uploadPath", "mach-skill"), ("fileName", filename)):
            parts.append(
                (
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
                    f"{value}\r\n"
                ).encode("utf-8")
            )
        parts.append(
            (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
                f"Content-Type: {mime}\r\n\r\n"
            ).encode("utf-8")
        )
        parts.append(content)
        parts.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))
        body = b"".join(parts)

        resp = request(
            "POST",
            UPLOAD_BASE + UPLOAD_STREAM,
            body=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        data = check_code(resp, f"Upload {filename}")
        results.append(
            {
                "file": path,
                "downloadUrl": data.get("downloadUrl"),
                "fileSize": data.get("fileSize"),
                "mimeType": data.get("mimeType"),
                "hinweis": "URL ist 24 Stunden gültig",
            }
        )
    out(results)


def parse_input(args):
    try:
        return json.loads(args.input)
    except json.JSONDecodeError as e:
        die(f"--input ist kein gültiges JSON: {e}")


def cmd_create(args):
    payload = {"model": args.model, "input": parse_input(args)}
    if args.callback:
        payload["callBackUrl"] = args.callback
    data = check_code(request("POST", API_BASE + JOBS_CREATE, body=payload), "createTask")
    out({"taskId": data.get("taskId"), "model": args.model})


def jobs_record(task_id):
    url = API_BASE + JOBS_RECORD + "?" + urllib.parse.urlencode({"taskId": task_id})
    return check_code(request("GET", url), "recordInfo")


def cmd_status(args):
    out(jobs_record(args.task_id))


def jobs_wait(task_id, interval, timeout):
    start = time.time()
    while True:
        data = jobs_record(task_id)
        state = data.get("state")
        if state == "success":
            return data
        if state == "fail":
            die(
                f"Task {task_id} fehlgeschlagen: code={data.get('failCode')}, "
                f"msg={data.get('failMsg')}"
            )
        if time.time() - start > timeout:
            die(
                f"Timeout nach {timeout}s. Task {task_id} läuft serverseitig weiter – "
                f"später erneut prüfen mit: kie.py status {task_id}"
            )
        print(
            f"... Status: {state}, Fortschritt: {data.get('progress')}%",
            file=sys.stderr,
        )
        time.sleep(interval)


def cmd_wait(args):
    out(jobs_wait(args.task_id, args.interval, args.timeout))


def result_urls_from_jobs(data):
    urls = []
    result_json = data.get("resultJson")
    if result_json:
        try:
            parsed = json.loads(result_json) if isinstance(result_json, str) else result_json
            urls = parsed.get("resultUrls") or []
            if not urls and isinstance(parsed.get("resultObject"), dict):
                for v in parsed["resultObject"].values():
                    if isinstance(v, list):
                        urls.extend(u for u in v if isinstance(u, str) and u.startswith("http"))
        except json.JSONDecodeError:
            pass
    return urls


def download_urls(urls, out_dir, prefix=""):
    os.makedirs(out_dir, exist_ok=True)
    files = []
    for i, url in enumerate(urls):
        name = os.path.basename(urllib.parse.urlparse(url).path) or f"result_{i}"
        if prefix:
            name = f"{prefix}_{name}"
        dest = os.path.join(out_dir, name)
        req = urllib.request.Request(url, headers={"User-Agent": "mach-skill/1.0"})
        with urllib.request.urlopen(req, timeout=600) as resp, open(dest, "wb") as f:
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
        files.append(dest)
    return files


def cmd_run(args):
    payload = {"model": args.model, "input": parse_input(args)}
    data = check_code(request("POST", API_BASE + JOBS_CREATE, body=payload), "createTask")
    task_id = data.get("taskId")
    print(f"Task erstellt: {task_id} ({args.model})", file=sys.stderr)
    record = jobs_wait(task_id, args.interval, args.timeout)
    urls = result_urls_from_jobs(record)
    files = download_urls(urls, args.out, prefix=args.model.replace("/", "_")) if urls else []
    out(
        {
            "taskId": task_id,
            "model": args.model,
            "state": record.get("state"),
            "creditsConsumed": record.get("creditsConsumed"),
            "costTimeMs": record.get("costTime"),
            "resultUrls": urls,
            "localFiles": files,
        }
    )


# ------------------------------------------------------------ Veo-Befehle


def cmd_veo_create(args):
    payload = parse_input(args)
    data = check_code(request("POST", API_BASE + VEO_CREATE, body=payload), "veo/generate")
    out({"taskId": data.get("taskId"), "model": payload.get("model", "veo3")})


def veo_record(task_id):
    url = API_BASE + VEO_RECORD + "?" + urllib.parse.urlencode({"taskId": task_id})
    return check_code(request("GET", url), "veo/record-info")


def cmd_veo_status(args):
    out(veo_record(args.task_id))


def veo_wait(task_id, interval, timeout):
    start = time.time()
    while True:
        data = veo_record(task_id)
        flag = data.get("successFlag")
        if flag == 1:
            return data
        if flag in (2, 3):
            die(
                f"Veo-Task {task_id} fehlgeschlagen: code={data.get('errorCode')}, "
                f"msg={data.get('errorMessage')}"
            )
        if time.time() - start > timeout:
            die(
                f"Timeout nach {timeout}s. Task {task_id} läuft serverseitig weiter – "
                f"später erneut prüfen mit: kie.py veo-status {task_id}"
            )
        print("... Veo generiert noch", file=sys.stderr)
        time.sleep(interval)


def cmd_veo_wait(args):
    out(veo_wait(args.task_id, args.interval, args.timeout))


def cmd_veo_run(args):
    payload = parse_input(args)
    data = check_code(request("POST", API_BASE + VEO_CREATE, body=payload), "veo/generate")
    task_id = data.get("taskId")
    model = payload.get("model", "veo3")
    print(f"Veo-Task erstellt: {task_id} ({model})", file=sys.stderr)
    record = veo_wait(task_id, args.interval, args.timeout)
    response = record.get("response") or {}
    urls = response.get("resultUrls") or []
    files = download_urls(urls, args.out, prefix=model) if urls else []
    out(
        {
            "taskId": task_id,
            "model": model,
            "resolution": response.get("resolution"),
            "resultUrls": urls,
            "localFiles": files,
        }
    )


# ------------------------------------------------------- generische Befehle


def cmd_post(args):
    try:
        body = json.loads(args.json)
    except json.JSONDecodeError as e:
        die(f"--json ist kein gültiges JSON: {e}")
    out(request("POST", API_BASE + args.path, body=body))


def cmd_get(args):
    url = API_BASE + args.path
    if args.param:
        params = dict(p.split("=", 1) for p in args.param)
        url += "?" + urllib.parse.urlencode(params)
    out(request("GET", url))


def cmd_download(args):
    files = download_urls(args.urls, args.out)
    out({"localFiles": files})


# ----------------------------------------------------------------- Parser


def main():
    p = argparse.ArgumentParser(
        description="Helfer für die kie.ai-API (mach-Skill).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("credit").set_defaults(func=cmd_credit)

    sp = sub.add_parser("set-key", help="API-Key lokal speichern (~/.config/mach/config.json)")
    sp.add_argument("key")
    sp.set_defaults(func=cmd_set_key)

    sub.add_parser("key-status", help="Zeigt, ob und woher ein API-Key geladen wird").set_defaults(
        func=cmd_key_status
    )

    sp = sub.add_parser("upload")
    sp.add_argument("files", nargs="+")
    sp.set_defaults(func=cmd_upload)

    def poll_args(sp):
        sp.add_argument("--interval", type=int, default=10, help="Poll-Intervall in Sekunden")
        sp.add_argument("--timeout", type=int, default=1800, help="Timeout in Sekunden")

    sp = sub.add_parser("create")
    sp.add_argument("model")
    sp.add_argument("--input", required=True, help="Input-Objekt als JSON")
    sp.add_argument("--callback", help="Optionale Webhook-URL")
    sp.set_defaults(func=cmd_create)

    sp = sub.add_parser("status")
    sp.add_argument("task_id")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("wait")
    sp.add_argument("task_id")
    poll_args(sp)
    sp.set_defaults(func=cmd_wait)

    sp = sub.add_parser("run")
    sp.add_argument("model")
    sp.add_argument("--input", required=True, help="Input-Objekt als JSON")
    sp.add_argument("--out", default="./mach-output", help="Zielverzeichnis für Ergebnisse")
    poll_args(sp)
    sp.set_defaults(func=cmd_run)

    sp = sub.add_parser("veo-create")
    sp.add_argument("--input", required=True, help="Kompletter Veo-Payload als JSON")
    sp.set_defaults(func=cmd_veo_create)

    sp = sub.add_parser("veo-status")
    sp.add_argument("task_id")
    sp.set_defaults(func=cmd_veo_status)

    sp = sub.add_parser("veo-wait")
    sp.add_argument("task_id")
    poll_args(sp)
    sp.set_defaults(func=cmd_veo_wait)

    sp = sub.add_parser("veo-run")
    sp.add_argument("--input", required=True, help="Kompletter Veo-Payload als JSON")
    sp.add_argument("--out", default="./mach-output")
    poll_args(sp)
    sp.set_defaults(func=cmd_veo_run)

    sp = sub.add_parser("post")
    sp.add_argument("path", help="API-Pfad, z. B. /api/v1/generate")
    sp.add_argument("--json", required=True)
    sp.set_defaults(func=cmd_post)

    sp = sub.add_parser("get")
    sp.add_argument("path")
    sp.add_argument("--param", action="append", help="Query-Parameter k=v (mehrfach möglich)")
    sp.set_defaults(func=cmd_get)

    sp = sub.add_parser("download")
    sp.add_argument("urls", nargs="+")
    sp.add_argument("--out", default="./mach-output")
    sp.set_defaults(func=cmd_download)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
