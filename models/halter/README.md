# Trenner/Halter Vorratsbox + Abdeckung mit Schlauchführung

`halter.stl` (Trenner mit Körper) · `abdeckung.stl` (Abdeckung, ersetzt hier die Gummiabdeckung) ·
`baugruppe.stl` (beides, nur Ansicht) · `halter.py` (parametrisch) · `preview.png` · `schnitt.png`

## Maße (Zollstock-Fotos)

| Maß | Wert (mm) | Quelle |
|---|---|---|
| Flansch Breite oben / unten | 48 / 42 | gemessen |
| Flansch Höhe | 84 | gemessen |
| Bogen oben (Durchhang Mitte) | 7,5 | abgelesen |
| Flansch Dicke | 3 | abgelesen |
| Obere Langlöcher | 7 × 3,5, ±15 aus Mitte, 7 unter den Ecken | abgelesen |
| Mittlere Langlöcher | 7 × 3,5 hochkant, ±16, 30 über Unterkante | abgelesen |
| Körperbreite oben / unten | 42 / 38 | abgelesen |
| Körperlänge | 60 | **geschätzt – bitte messen** |
| Schlauch Außen-Ø | 10 | **geschätzt – bitte messen** |

## Abdeckung
- Füllt den Raum zwischen Körperoberkante und Flanschbogen → **bündig mit dem Trenner**.
- Schlauch liegt mittig in einer Rinne, 8 mm Schlitz oben → Schlauch wird eingedrückt und gehalten
  (wie der Schlitz der Gummiabdeckung). Oberkante Schlauch liegt nicht höher als die Bogenmitte.
- Kerbe im Flanschbogen: Schlauch kommt aus der Box (Gummiabdeckung dort abschneiden) und läuft durch.
- Befestigung: 2 Zapfen hinten in den **oberen Langlöchern** des Trenners, vorn 2 Rasthaken unter dem Dach.
- Montage: Abdeckung schräg ansetzen, Zapfen in die Langlöcher schieben, vorn runterdrücken bis es klickt.

Abweichung vom Original: Mittelbohrung sitzt tiefer (unter der Schlauchrinne).

Werte ändern in `P` in `halter.py`, dann `python3 halter.py` (benötigt `pip install manifold3d trimesh numpy`).
