# Modellkatalog: Standard-Paare (Qualität + Schnell) je Modalität

Jede Generierung läuft mit beiden Modellen des Paars — außer der Nutzer
gibt bei der Kostenfreigabe nur eines frei.

**Preise sind Richtwerte** (Stand: August 2026, 1 Credit ≈ 0,005 USD).
kie.ai ändert Modelle und Preise laufend. Vor der Kostenübersicht die
Doku-Seite des Modells per WebFetch prüfen (exakte Modell-ID, Input-Schema,
aktueller Preis); die aktuelle Modellliste steht auf https://kie.ai/market,
Preise auf https://kie.ai/pricing. Mit „ca." gekennzeichnete Werte dem
Nutzer auch als Circa-Werte präsentieren.

## Bild

| Rolle | Modell-ID (Jobs-API) | Kosten (ca.) | Doku |
|---|---|---|---|
| Qualität | `google/nano-banana-pro` | ca. 0,10 $ / Bild | https://docs.kie.ai/market/google/pro-image-to-image |
| Schnell | `google/nano-banana` | ca. 0,02 $ / Bild | https://docs.kie.ai/market/google/nano-banana |

Wichtige Input-Felder: `prompt`, `image_urls` (Referenzbilder, nur bei
Edit-/i2i-Varianten), `output_format` (`png`/`jpeg`), `aspect_ratio` bzw.
`image_size`. Achtung: Für Bildbearbeitung mit Referenzbild ggf. die
Edit-Variante des Modells verwenden (eigene Modell-ID, siehe Doku).

Alternativen (bei Bedarf über https://kie.ai/market prüfen):
`bytedance/seedream-v4` (+ `.../seedream-v4-edit`), Flux-, GPT-Image- und
Grok-Imagine-Modelle.

## Video

| Rolle | Modell | Kosten (ca.) | Doku |
|---|---|---|---|
| Qualität | `veo3` (Veo-Endpoint) | ca. 2,00 $ / 8-s-Video (400 Credits) | https://docs.kie.ai/veo3-api/generate-veo-3-video |
| Schnell | `veo3_fast` (Veo-Endpoint) | ca. 0,40 $ / 8-s-Video (80 Credits) | dito |

Veo läuft über den eigenen Endpoint (`kie.py veo-run`), NICHT über die
Jobs-API. Wichtige Felder: `prompt`, `model` (`veo3` / `veo3_fast`),
`aspect_ratio` (`16:9`, `9:16`, `Auto`), `duration` (4/6/8 s),
`resolution` (`720p`/`1080p`), `imageUrls` (1–2 Referenzbilder für
Image-to-Video), `generationType` (`TEXT_2_VIDEO`,
`FIRST_AND_LAST_FRAMES_2_VIDEO`, `REFERENCE_2_VIDEO`).
Hinweis: `veo3` (Qualität) unterstützt nur Text-/Image-to-Video.

Alternative über die Jobs-API — sinnvoll bei Video-/Audio-Referenzen, die
Veo nicht annimmt: Qualität `bytedance/seedance-2`
(https://docs.kie.ai/market/bytedance/seedance-2), Schnell
`bytedance/seedance-2-fast`
(https://docs.kie.ai/market/bytedance/seedance-2-fast). Seedance 2 nimmt
`reference_image_urls`, `reference_video_urls`, `reference_audio_urls`,
`first_frame_url`, `last_frame_url`.

## Musik

Suno über den eigenen Suno-Endpoint (nicht Jobs-API):
Doku https://docs.kie.ai/suno-api/generate-music — vor Nutzung lesen und
per `kie.py post /api/v1/generate --json '...'` aufrufen; Status-Abfrage
laut Doku (siehe references/api.md).

| Rolle | Modell | Kosten (ca.) |
|---|---|---|
| Qualität | Suno, neuestes V-Modell (z. B. `V4_5` oder neuer, laut Doku) | ca. 0,06–0,10 $ / Generierung (2 Songs) |
| Schnell | Suno `V3_5` | ca. 0,04 $ / Generierung |

## Sprache (Text-to-Speech)

| Rolle | Modell-ID (Jobs-API) | Kosten (ca.) | Doku |
|---|---|---|---|
| Qualität | `elevenlabs/text-to-speech-multilingual-v2` | je nach Textlänge | https://docs.kie.ai/market/elevenlabs/text-to-speech-multilingual-v2 |
| Schnell | `elevenlabs/text-to-speech-turbo-2-5` | je nach Textlänge | https://docs.kie.ai/market/elevenlabs/text-to-speech-turbo-2-5 |

TTS-Kosten hängen von der Textlänge ab — vor der Kostenübersicht die
Doku-Seite prüfen und die Kosten für die konkrete Textlänge berechnen.

## Soundeffekte

`elevenlabs/sound-effect-v2` über die Jobs-API
(https://docs.kie.ai/market/elevenlabs/sound-effect-v2). Hier gibt es kein
sinnvolles Schnell/Qualität-Paar — dem Nutzer stattdessen EINE Generierung
mit Kosten anbieten und das kurz begründen.

## Text

Reine Textgenerierung direkt selbst erledigen (keine API-Kosten). Nur wenn
der Nutzer ausdrücklich ein bestimmtes Fremdmodell über kie.ai will, die
Chat-/LLM-Doku unter https://docs.kie.ai prüfen.
