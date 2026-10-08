"""Parametrisches 3D-Modell des schwarzen Halters (Flansch + Hohlkoerper mit Rinne).

Alle Masse in mm, aus Fotos geschaetzt (Massstab: Daumen ~22 mm).
Koordinaten: X = nach vorn (ab Flansch-Vorderseite), Y = Breite, Z = hoch
(Z=0 = Oberkante Koerper).

    python3 halter.py            -> schreibt halter.stl
    python3 halter.py --scale 1.05   -> alles um 5 % groesser
"""
import argparse
import numpy as np
from manifold3d import CrossSection, JoinType, Manifold
import trimesh

# ---------------- Parameter ----------------
P = dict(
    length=95.0,          # Koerperlaenge Flansch -> Spitze (oben)
    front_drop=24.0,      # senkrechte Stirnflaeche an der Spitze
    body_bottom=-116.0,   # Unterkante Koerper / Flansch
    foot_depth=31.0,      # Koerpertiefe unten am Flansch
    w_top=62.0,           # Koerperbreite aussen oben am Flansch
    w_bot=56.0,           # Koerperbreite aussen unten am Flansch
    tip_scale=0.70,       # Breitenverjuengung zur Spitze hin
    wall=3.0,             # Wandstaerke
    groove_r=11.5,        # Rinnenradius (22,2 mm Lenkeraufsatz + Spiel)
    groove_depth=8.0,
    fl_t=4.0,             # Flanschdicke
    fl_top=19.0,          # Flansch ueberragt Koerperoberkante
    fl_w_top=75.0,
    fl_w_bot=64.0,
    fl_sag=7.0,           # Durchhang des Bogens oben
    hose_od=10.0,         # Aussendurchmesser Trinkschlauch (nachmessen!)
    hose_gap=0.8,         # Spiel im Kanal (Durchmesser)
    hose_wall=2.0,        # Wandstaerke Schlauchkanal
    hose_z=-18.0,         # Hoehe Austritt vorne (Mitte)
    hose_x_in=14.0,       # Eintritt unten: Abstand vom Flansch
)


def bezier(p0, p1, p2, n=24):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2


def side_profile(inset=0.0):
    """Seitenkontur (X,Z) - 'Pistolengriff'-Form, inset = Wandstaerke nach innen."""
    L, fd, zb, fdp = P["length"], P["front_drop"], P["body_bottom"], P["foot_depth"]
    curve = bezier(np.array([L, -fd]), np.array([46, -40]), np.array([fdp, -95.0]))
    pts = [(-20, 0), (L, 0)] + [tuple(p) for p in curve] + [(fdp, zb), (-20, zb)]
    cs = CrossSection([pts[::-1]])
    return cs.offset(-inset, JoinType.Miter) if inset else cs


def cross_section(inset=0.0):
    """Querschnitt (Y,Z) am Flansch: Trapez, oben breiter."""
    wt, wb, zb = P["w_top"] / 2 - inset, P["w_bot"] / 2 - inset, P["body_bottom"]
    return CrossSection([[(-wb, zb + inset), (wb, zb + inset), (wt, -inset), (-wt, -inset)]])


def along_x(cs, h, x0, scale_y=1.0):
    """Querschnitt (u=Y, v=Z) entlang X extrudieren."""
    m = Manifold.extrude(cs, h, scale_top=(scale_y, 1.0))
    m = m.transform(np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]], float))
    return m.translate((x0, 0, 0))


def along_y(cs, h=200.0):
    """Seitenkontur (u=X, v=Z) quer (Y) extrudieren, mittig."""
    m = Manifold.extrude(cs, h).translate((0, 0, -h / 2))
    return m.transform(np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0]], float))


def cyl_x(r, x0, x1, y, z, n=64):
    return Manifold.cylinder(x1 - x0, r, r, n).rotate((0, 90, 0)).translate((x0, y, z))


def slot(cx, cz, length, width, vertical, x0=-10, x1=10):
    """Langloch durch den Flansch (in YZ-Ebene)."""
    r = width / 2
    d = (length - width) / 2
    a = (0, d) if vertical else (d, 0)
    s = cyl_x(r, x0, x1, cx - a[0], cz - a[1], 32) + cyl_x(r, x0, x1, cx + a[0], cz + a[1], 32)
    box = Manifold.cube((x1 - x0, width if vertical else 2 * d, 2 * d if vertical else width))
    box = box.translate((x0, cx - (r if vertical else d), cz - (d if vertical else r)))
    return s + box


def tube(r, pts):
    """Rohr entlang eines Polygonzugs (Huellen aufeinanderfolgender Kugeln)."""
    balls = [Manifold.sphere(r, 32).translate((x, 0, z)) for x, z in pts]
    return Manifold.batch_boolean(
        [Manifold.batch_hull([a, b]) for a, b in zip(balls, balls[1:])],
        __import__("manifold3d").OpType.Add)


def hose_path(extra=0.0):
    """Kanal: unten senkrecht rein, sanfter Bogen, vorne waagerecht raus."""
    L, xi, zh = P["length"], P["hose_x_in"], P["hose_z"]
    return bezier(np.array([xi, P["body_bottom"] - 4 - extra]), np.array([xi, zh]),
                  np.array([L + 2 + extra, zh]), 40)


def build():
    L, w, t = P["length"], P["wall"], P["fl_t"]
    gz = P["groove_r"] - P["groove_depth"]          # Achse der Rinne

    outer = along_x(cross_section(), L + 5, -t, P["tip_scale"]) ^ along_y(side_profile())
    inner = along_x(cross_section(w), L + 5, -10, P["tip_scale"]) ^ along_y(side_profile(w))
    body = outer - inner

    # Rinne oben: Rohrwandung einfuegen, dann Rinne ausschneiden
    body += cyl_x(P["groove_r"] + w, 0, L, 0, gz) ^ outer
    body -= cyl_x(P["groove_r"], -20, L + 20, 0, gz)

    # Schraubendom mittig oben (Senkbohrung)
    boss_z = gz - P["groove_r"] - w - 6
    body += cyl_x(8, 0, 14, 0, boss_z) ^ outer

    # Flansch
    hwT, hwB, zT, zB = P["fl_w_top"] / 2, P["fl_w_bot"] / 2, P["fl_top"], P["body_bottom"]
    sag = P["fl_sag"]
    R = (hwT ** 2 + sag ** 2) / (2 * sag)
    arc = [(y, zT - sag + (R - np.sqrt(R ** 2 - y ** 2))) for y in np.linspace(hwT, -hwT, 41)]
    plate = along_x(CrossSection([[(-hwB, zB), (hwB, zB)] + arc]), t, -t)
    opening = along_x(cross_section(w), t + 2, -t - 1)
    lug_z = zT - 78
    lugs = cyl_x(7, -t - 2, 2, -24, lug_z) + cyl_x(7, -t - 2, 2, 24, lug_z)
    plate = plate - (opening - lugs) + (lugs ^ plate.hull())
    plate += cyl_x(8, -t, 0, 0, boss_z)

    m = body + plate
    # Bohrungen
    m -= cyl_x(2.75, -t - 1, 20, 0, boss_z)
    m -= cyl_x(5.0, -t - 1, -t + 2, 0, boss_z)          # Senkung
    for s in (-1, 1):
        m -= slot(s * 22, zT - 12, 9, 4.5, False)
        m -= slot(s * 24, lug_z, 9, 4.5, True)
    # Schlauchkanal: Eintritt unten, Austritt vorne Richtung Cockpit
    rb = (P["hose_od"] + P["hose_gap"]) / 2
    m += tube(rb + P["hose_wall"], hose_path()) ^ outer
    m -= tube(rb, hose_path(10))
    zb, xi = P["body_bottom"], P["hose_x_in"]
    flare = Manifold.cylinder(4, rb + 2, rb, 48).translate((xi, 0, zb - 0.01))
    m -= flare                                           # Fase Eintritt unten
    m -= Manifold.cylinder(4, rb + 2, rb, 48).rotate((0, -90, 0)).translate((L + 0.01, 0, P["hose_z"]))
    return m


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("-o", default="halter.stl")
    a = ap.parse_args()
    m = build().scale((a.scale,) * 3)
    mesh = m.to_mesh()
    tm = trimesh.Trimesh(mesh.vert_properties[:, :3], mesh.tri_verts, process=False)
    tm.export(a.o)
    b = tm.bounds
    print(f"{a.o}: {len(tm.faces)} Dreiecke, watertight={tm.is_watertight}, "
          f"Volumen={tm.volume / 1000:.1f} cm3, Abmessungen={np.round(b[1] - b[0], 1)} mm")
