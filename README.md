# mach — Claude-Skill für Medien-Generierung über kie.ai

Ein Skill für Claude Code / Claude, der Bilder, Videos, Musik und Audio über
die [kie.ai](https://kie.ai)-API generiert — mit Kostenkontrolle:

- **`/mach <prompt>`** startet den Skill mit einer Beschreibung dessen, was
  generiert werden soll.
- Jede Generierung läuft mit **zwei Modellen**: einem schnellen (günstige,
  schnelle Vorschau) und einem hochwertigen (bestes Ergebnis).
- **Vor** jeder Generierung zeigt der Skill die Kosten (Credits + USD) und
  das aktuelle Guthaben an. Generiert wird **erst nach expliziter
  Freigabe** — wahlweise beide Modelle, nur das schnelle oder nur das
  hochwertige.
- An den Prompt können **Referenzdateien** angehängt werden (Bilder, Texte,
  Audio, Videos). Sie werden über die kie.ai-Upload-API hochgeladen und den
  Modellen als Referenz übergeben.

## Installation

1. Repository in das Skill-Verzeichnis legen (global):

   ```bash
   git clone <repo-url> ~/.claude/skills/mach
   ```

   Oder projektbezogen nach `<projekt>/.claude/skills/mach`.

2. API-Key von https://kie.ai/api-key besorgen und als Umgebungsvariable
   setzen (z. B. in `~/.bashrc` / `~/.zshrc`):

   ```bash
   export KIE_AI_API_KEY="dein-key"
   ```

3. Python 3 muss verfügbar sein (nur Standardbibliothek, keine Pakete nötig).

## Verwendung

```
/mach ein 8-Sekunden-Video von einem Segelboot bei Sonnenuntergang, 16:9
/mach ein Logo im Stil des angehängten Bildes: ./referenz.png
/mach einen entspannten Lo-Fi-Track, 2 Minuten
/mach sprich diesen Text als Audio: ./text.md
```

Ablauf: Skill wählt das Modellpaar → lädt Referenzen hoch → zeigt
Kostenübersicht und Guthaben → wartet auf Freigabe → generiert → lädt die
Ergebnisse nach `./mach-output/` herunter und berichtet die tatsächlich
verbrauchten Credits.

## Aufbau

```
mach/
├── SKILL.md            # Anweisungen für Claude (Workflow, Freigabe-Regeln)
├── scripts/kie.py      # CLI-Helfer für die kie.ai-API (nur Python-Stdlib)
└── references/
    ├── models.md       # Modellpaare (Qualität/Schnell) je Modalität + Kosten
    └── api.md          # kie.ai-Endpoints, Formate, Upload, Fehler
```

`scripts/kie.py` lässt sich auch direkt nutzen, z. B.:

```bash
python3 scripts/kie.py credit
python3 scripts/kie.py upload bild.jpg
python3 scripts/kie.py run "google/nano-banana" --input '{"prompt":"..."}' --out ./mach-output
python3 scripts/kie.py veo-run --input '{"prompt":"...","model":"veo3_fast"}' --out ./mach-output
```

## Hinweise

- Preise in `references/models.md` sind Richtwerte; der Skill prüft die
  Modell-Doku vor der Kostenschätzung. Aktuelle Preise: https://kie.ai/pricing
- Upload-URLs für Referenzen sind 24 Stunden gültig.
- Ergebnis-URLs von kie.ai verfallen — der Skill lädt Ergebnisse deshalb
  sofort lokal herunter.
