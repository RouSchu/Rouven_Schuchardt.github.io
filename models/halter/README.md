# Halter – 3D-Modell aus Fotos

`halter.stl` (druckbar, wasserdicht) · `halter.py` (parametrisch) · `preview.png`

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

Nachmessen & skalieren: z. B. Flanschbreite oben messen (Soll 75) und
`python3 halter.py --scale <gemessen/75>` – oder einzelne Werte in `P` ändern.
Benötigt: `pip install manifold3d trimesh numpy`.
