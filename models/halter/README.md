# Halter – 3D-Modell aus Fotos

`halter.stl` (druckbar, wasserdicht) · `halter.py` (parametrisch) · `preview.png` · `schnitt.png`

Maßstab aus den Fotos: Daumenbreite ≈ 22 mm → ca. 0,1 mm/px. Toleranz realistisch **±5–10 %**.

| Maß | Wert (mm) |
|---|---|
| Flansch Höhe gesamt | 135 |
| Flansch Breite oben / unten | 75 / 64 |
| Flansch Dicke | 4 |
| Bogen oben (Durchhang) | 7 |
| Körperlänge oben (ab Flansch) | 95 |
| Stirnfläche vorne (senkrecht) | 24 |
| Körpertiefe unten am Flansch | 31 |
| Flansch über Körperoberkante | 19 |
| Körperbreite am Flansch oben / unten | 62 / 56 |
| Verjüngung zur Spitze | auf 70 % |
| Wandstärke | 3 |
| Rinne oben | R 11,5, 8 tief (für Ø 22,2 Aufsatz) |
| Langlöcher | 9 × 4,5 (2× oben quer, 2× Mitte hoch) |
| Mittelbohrung | Ø 5,5, Senkung Ø 10 |
| Schlauchkanal | Ø 10,8 innen (Schlauch Ø 10 + 0,8 Spiel), Wand 2 |
| Kanalführung | Eintritt unten (14 vom Flansch, Fase), Bogen, Austritt vorne waagerecht auf Z = −18 (Fase) |

Nachmessen & skalieren: z. B. Flanschbreite oben messen (Soll 75) und
`python3 halter.py --scale <gemessen/75>` – oder einzelne Werte in `P` ändern.
Benötigt: `pip install manifold3d trimesh numpy`.

**Schlauchkanal:** Schlauch-Außendurchmesser nachmessen und `hose_od` in `P` anpassen.
Zum Einfädeln Beißventil abziehen; der Bogen ist groß genug, damit der Schlauch nicht abknickt.
