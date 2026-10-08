# Halter – 3D-Modell aus Fotos

`halter.stl` (Körper) · `deckel.stl` (Einklick-Deckel) · `baugruppe.stl` (beides zusammen, nur zur Ansicht) · `halter.py` (parametrisch) · `preview.png` · `fenster_detail.png`

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
| Schlaucheintritt unten | Ø 10,8, 14 vom Flansch, mit Fase |
| Deckelfenster (vorn auf der Bogenfläche) | 28 × 20, Falz 2 rundum, 1,6 tief |
| Verstärkungsrahmen innen | 5 breit/tief |
| Seitliche Rastlöcher | 2× 9 × 1,8, Oberkante 4,6 unter Oberfläche |
| Deckel | Platte 1,6 + Stopfen, 2 Rastarme (1,4 dick, Nase 0,9), Spiel 0,2 |
| Schlauchtülle | Ø 10,3 innen, 25° nach vorn-unten, Einlauffase |

Nachmessen & skalieren: z. B. Flanschbreite oben messen (Soll 75) und
`python3 halter.py --scale <gemessen/75>` – oder einzelne Werte in `P` ändern.
Benötigt: `pip install manifold3d trimesh numpy`.

**Schlauchführung (Prinzip Canyon):** Schlauch unten in den Halter, innen hoch,
durch die Tülle im Deckel nach vorn ins Cockpit. Die Tülle hält den Schlauch.
Deckel von außen in das Fenster drücken, bis die Nasen in den seitlichen Löchern einrasten;
zum Lösen die Nasen von innen mit einem kleinen Schraubendreher eindrücken.

**Druck:** Deckel in PETG/ABS oder besser Nylon (federnde Rastarme), Rastarme nach oben,
Platte unten mit Stützmaterial unter der Tülle. Schlauch-Außendurchmesser nachmessen → `hose_od`.
