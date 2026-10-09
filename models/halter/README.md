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
| Obere Langlöcher | 7 × 3,5 quer, ±15 aus Mitte, 9 unter den Ecken | abgelesen |
| Mittlere Langlöcher | 7 × 3,5 hochkant, ±16, 30 über Unterkante | abgelesen |
| Körperbreite oben / unten | 42 / 38 | abgelesen |
| Körperlänge | 60 | **geschätzt – bitte messen** |
| Schlauch Außen-Ø | 10 | **geschätzt – bitte messen** |

## Deckel für die offene Seite (Prinzip Canyon)
- Platte 2,5 mm mit der Kontur des Trenners (48/42 × 84, Bogen oben) → deckt die offene Seite bündig ab.
- **4 Rastnasen**, jede ausgerichtet wie ihr Langloch:
  - oben 2× **quer** (liegen an der oberen Lochkante, Haken rastet nach oben hinter dem Flansch ein)
  - Mitte 2× **hochkant** (liegen an der inneren Lochkante, Haken rastet zur Mitte hinter der Lasche ein)
  - Nase 1,2 mm dick, Haken 0,5 mm, Spiel 0,15 mm. Lösen: Haken von vorn mit kleinem Schraubendreher eindrücken.
- Schlauchführung **wie Canyon**: einfacher **Keil** (Dreiecksprisma, nur ebene Flächen, ca. 16 hoch × 19 lang × 15 breit)
  mit **gerader Schrägbohrung** (50° zur Platte, Richtung Cockpit) – kein Bogen, druckerfreundlich.
- Schlauch **klemmt am Eintritt** (Hülse innen + Platte, Ø = Schlauch − 0,2), im Keil hat er **Spiel** (Ø = Schlauch + 1,5).
- Druck: PETG oder Nylon, Platte flach aufs Bett (Außenseite oben, Keil wächst nach oben); kleine Stützen unter den Rastnasen und der Hülse.
- Parameter: `hose_od`, `hose_grip`, `hose_play`, `exit_angle`, `wedge_bore`, `port_z`, `plate_t`, `nose_t`, `nose_hook`.

Abweichung vom Original: Mittelbohrung sitzt tiefer (unter der Schlauchrinne).

Werte ändern in `P` in `halter.py`, dann `python3 halter.py` (benötigt `pip install manifold3d trimesh numpy`).
