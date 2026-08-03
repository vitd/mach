---
name: mach
description: >
  Generiert Bilder, Videos, Musik, Sprache und Soundeffekte über die kie.ai-API
  (Veo, Nano Banana, Seedance, Suno, ElevenLabs u. a.). Jede Generierung läuft
  parallel mit einem schnellen UND einem hochwertigen Modell, und zwar erst nach
  expliziter Kostenfreigabe durch den Nutzer. Referenzdateien (Bilder, Texte,
  Audio, Video) können angehängt werden. Diesen Skill immer verwenden, wenn der
  Nutzer "/mach" oder "mach" gefolgt von einem Generierungswunsch eingibt, oder
  wenn er Bilder, Videos, Musik oder Audio über kie.ai erzeugen möchte — auch
  wenn er kie.ai nicht ausdrücklich nennt, aber KI-Medien-Generierung mit
  Kostenkontrolle gemeint ist. Use this skill whenever the user invokes /mach
  or asks to generate images, video, music, or audio via the kie.ai API.
---

# mach — Medien-Generierung über kie.ai mit Kostenfreigabe

Dieser Skill erzeugt Bilder, Videos, Musik und Audio über die kie.ai-API.
Drei Grundprinzipien bestimmen jeden Durchlauf:

1. **Mehrfachgenerierung:** Jeder Auftrag läuft mit ZWEI Modellen — einem
   schnellen (günstige Vorschau, schnelles Ergebnis) und einem hochwertigen
   (bestes Ergebnis). Ausnahme Video: dort sind es DREI Modelle (Seedance 2
   Mini als schnelles, Veo 3.1 und Kling 3 als Qualitätsmodelle). Bei Bild
   stehen zwei Qualitätsmodelle zur Wahl (Nano Banana Pro und GPT Image 2).
   Alle freigegebenen Tasks starten parallel nach der Freigabe.
2. **Kostenfreigabe:** Vor JEDER Generierung werden die Kosten (Credits und
   USD, pro Modell und Summe) sowie das aktuelle Guthaben angezeigt. Ohne
   ausdrückliche Freigabe des Nutzers wird NICHTS generiert — das ist der
   Kern dieses Skills, denn jede Generierung kostet echtes Geld.
3. **Referenzen:** Der Nutzer kann lokale Dateien (Bilder, Texte, Audio,
   Videos) anhängen. Sie werden zu kie.ai hochgeladen und als Referenz-URLs
   an das Modell übergeben.

## Voraussetzungen

- Ein kie.ai-API-Key (erstellen unter https://kie.ai/api-key). Der Key wird
  in dieser Reihenfolge gesucht: Umgebungsvariable `KIE_AI_API_KEY` (oder
  `KIE_API_KEY`), dann Konfigdatei `~/.config/mach/config.json`.
- Python 3 (nur Standardbibliothek, keine Installation nötig).

**Erste Einrichtung:** Ist kein Key vorhanden (prüfbar mit
`python3 scripts/kie.py key-status`), den Nutzer EINMALIG nach seinem
API-Key fragen und ihn speichern:

```bash
python3 scripts/kie.py set-key DER_KEY
```

Dabei transparent dazusagen: Der Key wird lokal in
`~/.config/mach/config.json` gespeichert (nur für den Benutzer lesbar),
und die Eingabe im Chat bleibt im Chatverlauf sichtbar — wer das vermeiden
will, setzt stattdessen die Umgebungsvariable. In Umgebungen ohne
persistentes Dateisystem (z. B. claude.ai-Chats) gilt der gespeicherte Key
nur für die laufende Unterhaltung und muss beim nächsten Mal neu angegeben
werden. Den Key niemals ungefragt ausgeben, loggen oder committen;
`key-status` zeigt ihn nur maskiert.

Alle API-Aufrufe laufen über `scripts/kie.py` (relativ zu diesem Skill-
Verzeichnis). Aufruf: `python3 <skill-dir>/scripts/kie.py <befehl> ...`.
Übersicht: `python3 scripts/kie.py --help`.

## Ablauf

### Schritt 1: Auftrag verstehen

Aus dem Prompt des Nutzers bestimmen:

- **Modalität:** Bild, Video, Musik, Sprache (TTS) oder Soundeffekt.
  Bei Unklarheit (z. B. „mach etwas zu Sonnenuntergang") nachfragen.
- **Referenzen:** Hat der Nutzer Dateipfade oder URLs angehängt bzw. erwähnt?
- **Parameter:** Seitenverhältnis, Dauer, Auflösung, Stil — sofern genannt.
  Nicht Genanntes mit sinnvollen Defaults belegen und diese in der
  Kostenübersicht mit anzeigen.

Reine Textgenerierung braucht keine kie.ai-API — Texte direkt selbst
schreiben und dem Nutzer sagen, dass dafür keine Kosten anfallen.

### Schritt 2: Modelle wählen

`references/models.md` lesen. Dort stehen für jede Modalität die
Standard-Modelle (Qualität + Schnell; bei Video ein Trio aus Seedance 2
Mini, Veo 3.1 und Kling 3), die ungefähren Kosten und die Doku-URLs.

Wichtig: kie.ai ändert Modelle und Preise laufend. Vor der ersten Nutzung
eines Modells in einer Session die in `references/models.md` verlinkte
Doku-Seite per WebFetch prüfen (exakte Modell-ID, Input-Schema, aktueller
Preis). Erst wenn ID und Schema bestätigt sind, weiter zu Schritt 4.

### Schritt 3: Referenzen hochladen

Für jede angehängte lokale Datei:

```bash
python3 scripts/kie.py upload /pfad/zur/datei.jpg
```

Das lädt die Datei zu kie.ai hoch und gibt eine `downloadUrl` zurück
(24 Stunden gültig). Diese URLs je nach Modell als `image_urls`,
`imageUrls`, `reference_image_urls`, `reference_video_urls`,
`reference_audio_urls` usw. in den Input einsetzen — die genauen
Feldnamen stehen in der Modell-Doku (siehe `references/api.md`).

Sonderfälle:
- **Textdateien** nicht hochladen, sondern lesen und den Inhalt sinnvoll in
  den Prompt einarbeiten (z. B. als Stil- oder Inhaltsvorgabe).
- **URLs**, die der Nutzer direkt angibt, unverändert verwenden (kein
  Upload nötig).
- Dateien über ~100 MB: den Nutzer warnen, dass der Upload dauern kann.

### Schritt 4: Kosten ermitteln und Freigabe einholen

1. Guthaben abfragen: `python3 scripts/kie.py credit`
   (Ausgabe in Credits; 1 Credit ≈ 0,005 USD).
2. Kosten beider Modelle aus `references/models.md` bzw. der live geprüften
   Doku bestimmen. Bei Werten, die nur „ca." bekannt sind, das auch so
   kennzeichnen — niemals geschätzte Kosten als exakt ausgeben.
3. Übersicht anzeigen, etwa so:

   | Modell | Rolle | Kosten |
   |---|---|---|
   | bytedance/seedance-2-mini | Schnell | ca. 30 Credits (~0,15 $) |
   | veo3 (Veo 3.1) | Qualität | 400 Credits (~2,00 $) |
   | kling-3.0/video | Qualität | ca. 220 Credits (~1,10 $) |
   | **Summe** | | **ca. 650 Credits (~3,25 $)** |

   (Beispielwerte — die echten Zahlen kommen aus Schritt 2.)

   Dazu: aktuelles Guthaben, gewählte Parameter (Dauer, Format, …) und die
   Referenz-URLs. Reicht das Guthaben nicht, das klar sagen und auf
   https://kie.ai/pricing zum Aufladen verweisen — nicht generieren.

4. Freigabe einholen — mit AskUserQuestion. Bei zwei Modellen:
   - „Beide generieren" (Empfohlen — schnelle Vorschau + beste Qualität)
   - „Nur schnelles Modell"
   - „Nur Qualitätsmodell"
   - „Abbrechen"

   Bei Bild (ein schnelles Modell, zwei Qualitätsmodelle zur Wahl):
   - „Nano Banana + Nano Banana Pro" (Empfohlen)
   - „Nano Banana + GPT Image 2"
   - „Alle drei generieren"
   - „Abbrechen"

   Geht es erkennbar um Fotorealismus oder Text im Bild (Plakate, Logos
   mit Schriftzug), stattdessen „Nano Banana + GPT Image 2" als
   empfohlene Option zuerst nennen — das ist die Stärke von GPT Image 2.

   Bei Video (drei Modelle):
   - „Alle drei generieren" (Empfohlen)
   - „Nur Seedance 2 Mini (schnell)"
   - „Nur die Qualitätsmodelle (Veo 3.1 + Kling 3)"
   - „Abbrechen"

   Andere Kombinationen kann der Nutzer über „Other" frei angeben. In den
   Options-Beschreibungen jeweils die Kosten der Auswahl nennen.

   Ohne ausdrückliche Zustimmung wird KEIN Task erstellt. Das gilt auch,
   wenn der Nutzer im ursprünglichen Prompt schon „mach einfach" gesagt
   hat — die Freigabe bezieht sich auf die konkrete Kostensumme und muss
   nach deren Anzeige erfolgen. Läuft die Session nicht-interaktiv (keine
   Rückfrage möglich), die Kostenübersicht ausgeben und stoppen.

### Schritt 5: Generieren

Nach der Freigabe die freigegebenen Tasks starten — bei „Beide" wirklich
beide direkt nacheinander anlegen, dann gemeinsam pollen.

**Markt-Modelle (Jobs-API)** — Bilder, Seedance- und Kling-Videos,
ElevenLabs-Audio:

```bash
python3 scripts/kie.py run "google/nano-banana" \
  --input '{"prompt": "...", "image_urls": ["https://..."]}' \
  --out ./mach-output
```

**Veo-Videos** (eigener Endpoint):

```bash
python3 scripts/kie.py veo-run \
  --input '{"prompt": "...", "model": "veo3_fast", "aspect_ratio": "16:9"}' \
  --out ./mach-output
```

**Suno-Musik** (eigener Endpoint): Die Doku-Seite aus `references/models.md`
lesen und die generischen Befehle `kie.py post` / `kie.py get` verwenden
(Details in `references/api.md`).

`run`/`veo-run` erstellen den Task, pollen bis zum Abschluss und laden die
Ergebnisse nach `--out` herunter. Videos können mehrere Minuten dauern —
das ist normal, nicht abbrechen. Bei zwei parallelen Tasks: beide mit
`create`/`veo-create` starten, dann nacheinander mit `wait`/`veo-wait`
abholen (die Generierung läuft serverseitig parallel weiter).

### Schritt 6: Ergebnisse herunterladen und im Chat zeigen

**Immer herunterladen, nie nur verlinken.** kie.ai-Ergebnis-URLs verfallen
nach einiger Zeit — die lokalen Dateien sind das eigentliche Ergebnis.
`run`/`veo-run` laden automatisch herunter (`--out`, Standard
`./mach-output`); nach jedem Lauf prüfen, dass `localFiles` gefüllt ist.
Bei Abläufen, die nur URLs liefern (z. B. Suno über `post`/`get`), sofort
`kie.py download <urls> --out ./mach-output` nachschieben.

**Ergebnisse direkt im Chat präsentieren**, damit der Nutzer sie sofort
beurteilen kann, statt Pfade oder Links abzutippen:

- Die Ergebnisdateien mit dem in der Umgebung verfügbaren
  Datei-Präsentations-Tool an den Nutzer senden — z. B. `SendUserFile`
  (bei Bildern mit `display: "render"`, damit sie inline erscheinen) oder
  `present_files`. Bilder einzeln und klar beschriftet senden (welches
  Modell, welche Variante), damit der Vergleich schnell/Qualität leicht
  fällt. Videos und Audiodateien ebenfalls als Datei senden.
- Gibt es kein solches Tool (z. B. lokale CLI), die Dateipfade nennen —
  das ist der Fallback, nicht der Normalfall.
- Bilder zusätzlich selbst ansehen (Read auf die Bilddatei) und in ein,
  zwei Sätzen einordnen: Was unterscheidet die schnelle von der
  Qualitäts-Variante, gibt es sichtbare Fehler (Artefakte, falscher Text,
  ignorierte Vorgaben)? Bei offensichtlichen Fehlschlägen gleich eine
  konkrete Prompt-Verbesserung vorschlagen — aber nicht ungefragt neu
  generieren (neue Kosten).

**Außerdem berichten:**

- Tatsächlich verbrauchte Credits (`creditsConsumed` aus der Task-Antwort)
  je Modell, Vergleich mit der Schätzung, Restguthaben.
- Bei Fehlschlag eines Tasks: Fehlermeldung (`failMsg`) wiedergeben.
  Fehlgeschlagene Tasks kosten in der Regel nichts — das Guthaben
  gegenprüfen. Nur nach Rücksprache erneut versuchen (neue Kosten!).

## Referenzdateien

- `references/models.md` — Modellkatalog: Standard-Paare (Qualität/Schnell)
  je Modalität, Kosten, Doku-URLs. Vor jeder Kostenschätzung lesen.
- `references/api.md` — kie.ai-API-Details: Endpoints, Request/Response-
  Formate, Upload-API, Fehlerbehandlung. Lesen, wenn `kie.py` nicht reicht
  (z. B. Suno, neue Modelle, Debugging).

## Fehlerbehandlung

- **401:** API-Key ungültig/fehlt → Nutzer bitten, `KIE_AI_API_KEY` zu prüfen.
- **402 / Guthaben-Fehler:** Credits reichen nicht → Guthaben anzeigen,
  auf https://kie.ai/pricing verweisen.
- **429:** Rate-Limit (20 Requests/10 s) → kurz warten, dann weiter.
- **`state: fail`:** `failCode`/`failMsg` dem Nutzer zeigen. Häufige
  Ursachen: Inhaltsfilter (Prompt umformulieren), ungültige Referenz-URL
  (Upload wiederholen — URLs verfallen nach 24 h).
- **Timeout beim Pollen:** Task-ID nennen; mit
  `python3 scripts/kie.py status <taskId>` kann später weiter gepollt
  werden — der Task läuft serverseitig weiter.
