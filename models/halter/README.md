# Trenner/Halter Vorratsbox + Abdeckung mit Schlauchführung

`halter.stl` (Trenner mit Körper) · `abdeckung.stl` (Abdeckung, ersetzt hier die Gummiabdeckung) ·
`baugruppe.stl` (beides, nur Ansicht) · `halter.py` (parametrisch) · `abdeckung_ansicht.png`

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

## Abdeckung (Prinzip Canyon)
- Oberfläche folgt dem Flanschbogen → **bündig mit dem Trenner**; Gummiabdeckung dort abschneiden.
- Schlauch kommt **senkrecht von unten** (Tank im Rahmendreieck) durch eine Hülse mit Einlauffase,
  wird in einer keilförmigen Haube im Bogen (Radius 20) umgelenkt und tritt **waagerecht nach vorn** zum Cockpit aus.
  Der Kanal ist nur 0,3 mm größer als der Schlauch → der Schlauch bleibt an seinem Platz.
- Kein Einfüllstutzen (der sitzt unten am Tank).
- Befestigung: 2 Zapfen hinten in den **oberen Langlöchern** des Trenners, vorn 2 Rasthaken.
- Durchstoß 35 mm hinter dem Trenner; im Original muss das Dach dort für die Hülse ausgeschnitten werden.
- Wichtige Parameter: `hose_od`, `bend_r`, `bend_z` (Haubenhöhe), `port_x`, `length`.

Abweichung vom Original: Mittelbohrung sitzt tiefer (unter der Schlauchrinne).

Werte ändern in `P` in `halter.py`, dann `python3 halter.py` (benötigt `pip install manifold3d trimesh numpy`).
