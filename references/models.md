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

Video weicht vom Zwei-Modell-Schema ab: Hier laufen standardmäßig DREI
Modelle — ein schnelles und zwei Qualitätsmodelle:

| Rolle | Modell | API | Kosten (ca.) | Doku |
|---|---|---|---|---|
| Schnell | `bytedance/seedance-2-mini` | Jobs-API | günstigstes der drei; live prüfen | https://docs.kie.ai/market/bytedance/seedance-2-mini |
| Qualität | `veo3` (= Veo 3.1) | Veo-Endpoint | ca. 2,00 $ / 8-s-Video (400 Credits) | https://docs.kie.ai/veo3-api/generate-veo-3-video |
| Qualität | `kling-3.0/video` (Kling 3.0) | Jobs-API | live prüfen | https://docs.kie.ai/market/kling/kling-3-0 |

Für Kling 3 und Seedance 2 Mini liegen keine verlässlichen Richtpreise
vor — vor der Kostenübersicht IMMER live prüfen (Doku-Seite bzw.
https://kie.ai/pricing) und im Zweifel als „ca."-Wert kennzeichnen.

**Seedance 2 Mini** (Jobs-API): `prompt`, `duration` (4–15 s, Default 5),
`resolution` (`480p`/`720p`), `aspect_ratio` (`16:9`, `9:16`, `1:1`,
`4:3`, `3:4`, `21:9`, `adaptive`), `generate_audio` (bool),
`first_frame_url`, `last_frame_url`, `reference_image_urls` (bis 9),
`reference_video_urls` (bis 3, max. 15 s), `reference_audio_urls` (bis 3).
Nimmt als einziges der drei auch Video- und Audio-Referenzen an.

**Veo 3.1** läuft über den eigenen Endpoint (`kie.py veo-run`), NICHT über
die Jobs-API. Felder: `prompt`, `model` (`veo3` = Qualität; `veo3_fast` /
`veo3_lite` existieren als günstigere Varianten, sind hier aber nicht Teil
des Standard-Trios), `aspect_ratio` (`16:9`, `9:16`, `Auto`), `duration`
(4/6/8 s), `resolution` (`720p`/`1080p`), `imageUrls` (1–2 Referenzbilder),
`generationType` (`TEXT_2_VIDEO`, `FIRST_AND_LAST_FRAMES_2_VIDEO`,
`REFERENCE_2_VIDEO`). `veo3` unterstützt nur Text-/Image-to-Video.

**Kling 3.0** (Jobs-API): `prompt`, `image_urls` (First/Last-Frame),
`duration` (3–15 s), `aspect_ratio` (`16:9`, `9:16`, `1:1`), `mode`
(`std` = 720p, `pro` = 1080p, `4K`), `sound` (bool), `multi_shots` +
`multi_prompt` für Mehrschnitt-Videos. Der `mode` beeinflusst den Preis —
bei der Kostenprüfung berücksichtigen.

Da die drei Modelle unterschiedliche Parameter haben: gemeinsame Wünsche
des Nutzers (Dauer, Format, Ton) auf die jeweiligen Felder jedes Modells
abbilden und Abweichungen (z. B. Veo kann max. 8 s) in der Kostenübersicht
erwähnen. Referenzen, die ein Modell nicht annimmt (z. B. Videoreferenz
bei Veo/Kling), nur bei Seedance 2 Mini verwenden und das transparent
machen.

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
