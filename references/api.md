# kie.ai-API-Referenz

Basis-URL: `https://api.kie.ai` — Auth immer per Header
`Authorization: Bearer $KIE_AI_API_KEY`. Alle Generierungs-APIs sind
asynchron: Task anlegen → `taskId` erhalten → pollen. HTTP 200 beim
Anlegen heißt nur „Task angenommen", nicht „fertig".

Rate-Limit: 20 neue Generierungs-Requests pro 10 Sekunden (HTTP 429 bei
Überschreitung). `scripts/kie.py` wartet bei 429 automatisch und
wiederholt.

## Guthaben

```
GET /api/v1/chat/credit
```

Antwort: verbleibende Credits. 1 Credit ≈ 0,005 USD.
Via Skript: `python3 scripts/kie.py credit`

## Jobs-API (Markt-Modelle: Bilder, Seedance, ElevenLabs, …)

### Task anlegen

```
POST /api/v1/jobs/createTask
{
  "model": "google/nano-banana",
  "callBackUrl": "https://... (optional)",
  "input": { "prompt": "...", ... }
}
```

Die Felder in `input` sind modellspezifisch — exaktes Schema steht auf der
Doku-Seite des Modells (URLs in `references/models.md`).

Antwort: `{"code": 200, "msg": "success", "data": {"taskId": "..."}}`

### Task abfragen

```
GET /api/v1/jobs/recordInfo?taskId=...
```

Relevante Felder in `data`:

- `state`: `waiting` | `queuing` | `generating` | `success` | `fail`
- `resultJson` (String!): bei Erfolg z. B. `{"resultUrls": ["https://..."]}`;
  bei Text-/Objekt-Ausgaben `{"resultObject": {...}}`
- `failCode` / `failMsg`: bei `fail`
- `creditsConsumed`: tatsächlich verbrauchte Credits
- `progress`, `costTime`, `createTime`, `completeTime`

Via Skript: `create`, `status`, `wait` oder alles in einem: `run`.

## Veo-3-API (eigener Endpoint)

```
POST /api/v1/veo/generate
{
  "prompt": "...",
  "model": "veo3" | "veo3_fast",
  "aspect_ratio": "16:9" | "9:16" | "Auto",
  "duration": 4 | 6 | 8,
  "resolution": "720p" | "1080p",
  "imageUrls": ["https://..."],          // optional, 1–2 Bilder (i2v)
  "generationType": "TEXT_2_VIDEO" | "FIRST_AND_LAST_FRAMES_2_VIDEO" | "REFERENCE_2_VIDEO"
}
```

```
GET /api/v1/veo/record-info?taskId=...
```

- `successFlag`: `0` = generiert noch, `1` = Erfolg, `2`/`3` = fehlgeschlagen
- Ergebnis in `data.response.resultUrls` (dazu `originUrls`,
  `fullResultUrls`, `resolution`)
- Fehler in `errorCode` / `errorMessage`

Via Skript: `veo-create`, `veo-status`, `veo-wait`, `veo-run`.

## Suno-API (Musik, eigener Endpoint)

Doku: https://docs.kie.ai/suno-api/generate-music (Task anlegen) und
https://docs.kie.ai/suno-api/get-music-details (Status). Payload-Felder
vor Nutzung dort prüfen (u. a. `prompt`, `customMode`, `model`,
`instrumental`). Aufruf über die generischen Befehle:

```bash
python3 scripts/kie.py post /api/v1/generate --json '{...}'
python3 scripts/kie.py get /api/v1/generate/record-info --param taskId=...
```

Ergebnis-Audio-URLs anschließend mit `kie.py download <url> --out DIR`
sichern.

## Datei-Upload (Referenzen)

Eigene Basis-URL: `https://kieai.redpandaai.co`, gleicher Bearer-Key.

```
POST /api/file-stream-upload   (multipart/form-data)
  file:       Binärdaten
  uploadPath: Zielordner, z. B. "mach-skill"
  fileName:   optional
```

Antwort-`data.downloadUrl` ist die Referenz-URL für Modell-Inputs —
**24 Stunden gültig**, danach neu hochladen. Für kleine Dateien gibt es
auch `/api/file-base64-upload`, für entfernte Dateien
`/api/file-url-upload` (Doku: https://docs.kie.ai/file-upload-api/quickstart).

Via Skript: `python3 scripts/kie.py upload DATEI...`

## Ergebnisse sichern

Ergebnis-URLs von kie.ai verfallen (je nach Modell nach Stunden bis ~14
Tagen). Ergebnisse deshalb immer sofort herunterladen — `run`/`veo-run`
tun das automatisch (`--out`), sonst `kie.py download`.

## Typische Fehler

| Symptom | Ursache / Behandlung |
|---|---|
| HTTP 401 | API-Key fehlt/ungültig → `KIE_AI_API_KEY` prüfen |
| HTTP 402 oder Fehlermeldung zu Credits | Guthaben reicht nicht → aufladen unter https://kie.ai/pricing |
| HTTP 429 | Rate-Limit → warten (macht `kie.py` automatisch) |
| HTTP 422 | Input-Schema falsch → Modell-Doku erneut prüfen |
| `state: fail`, Inhaltsfilter-Meldung | Prompt umformulieren, Nutzer informieren |
| `fail` mit ungültiger Referenz-URL | Upload-URL abgelaufen (24 h) → neu hochladen |
