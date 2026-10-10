"""Parametrisches 3D-Modell: Trenner/Halter der Vorratsbox + Abdeckung mit Schlauchfuehrung.

Masse in mm, gemessen mit Zollstock an den Fotos (Flansch 48/42 breit, 84 hoch).
Koordinaten: X = nach vorn (ab Flansch-Vorderseite), Y = Breite, Z = hoch
(Z=0 = Oberkante Koerper = Unterseite der Abdeckung).

Die Abdeckung fuellt den Raum zwischen Koerperoberkante und Flanschbogen und schliesst
damit buendig mit dem Trenner ab. Der Schlauch liegt mittig in einer Rinne mit
Schnapplippen (wie der Schlitz der Gummiabdeckung), laeuft durch eine Kerbe im
Flanschbogen und vorn heraus Richtung Cockpit.

    python3 halter.py            -> halter.stl, abdeckung.stl, baugruppe.stl
    python3 halter.py --scale 1.02
"""
import argparse
import numpy as np
from manifold3d import CrossSection, JoinType, Manifold
import trimesh

# ---------------- Parameter ----------------
P = dict(
    # Flansch / Trenner (gemessen)
    fl_w_top=48.0,        # Breite oben (Ecke zu Ecke)
    fl_w_bot=42.0,        # Breite unten
    fl_h=84.0,            # Hoehe gesamt
    fl_t=3.0,             # Dicke
    fl_sag=7.5,           # Bogen oben: Mitte liegt so tief unter den Ecken
    fl_top=12.0,          # Ecken ueberragen die Koerperoberkante
    # Koerper (Laenge NICHT gemessen -> bitte nachmessen)
    length=60.0,          # Koerperlaenge Flansch -> Spitze
    front_drop=15.0,      # senkrechte Stirnflaeche an der Spitze
    foot_depth=20.0,      # Koerpertiefe unten am Flansch
    w_top=42.0,           # Koerperbreite aussen oben am Flansch
    w_bot=38.0,           # Koerperbreite aussen unten am Flansch
    tip_scale=0.80,       # Breitenverjuengung zur Spitze
    wall=2.5,             # Wandstaerke
    # Schlauch
    hose_od=10.0,         # Aussendurchmesser Trinkschlauch (nachmessen!)
    hose_clr=0.3,         # Spiel Schlauch in der Rinne (Durchmesser)
    guide_wall=1.8,       # Wand der Schlauchfuehrung
    hose_grip=0.2,        # Eintritt: Bohrung so viel KLEINER als der Schlauch -> klemmt
    wedge_h=9.0,          # Keilhoehe ueber der Platte (flaches Profil)
    wedge_len=32.0,       # Keillaenge entlang der Platte
    port_z=-28.0,         # Durchstoss: Hoehe Mitte auf der Plattenaussenseite (Z=0 = Koerperoberkante)
    sleeve=5.0,           # kurze Fuehrungshuelse innen
    plate_t=2.5,          # Dicke der Deckelplatte
    nose_t=1.2,           # Dicke der federnden Rastnase
    nose_hook=0.5,        # Ueberstand des Rasthakens hinter dem Flansch
    clr=0.2,              # Spiel Abdeckung <-> Halter
    # Loecher im Flansch (gemessen/abgelesen)
    slot_top=(15.0, 9.0), # obere Langloecher: +-Y, Abstand unter den Ecken
    slot_mid=(16.0, 30.0),# mittlere Langloecher: +-Y, Hoehe ueber Unterkante
    slot=(7.0, 3.5),      # Langloch L x B
    hole_d=4.0, csk_d=8.0,
)


def H():
    return -(P["fl_h"] - P["fl_top"])  # Unterkante Koerper / Flansch


def bezier(p0, p1, p2, n=24):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2


def side_profile(inset=0.0):
    """Seitenkontur (X,Z) - 'Pistolengriff'-Form."""
    L, fd, zb, fdp = P["length"], P["front_drop"], H(), P["foot_depth"]
    curve = bezier(np.array([L, -fd]), np.array([0.48 * L, 0.35 * zb]), np.array([fdp, 0.82 * zb]))
    pts = [(-20, 0), (L, 0)] + [tuple(p) for p in curve] + [(fdp, zb), (-20, zb)]
    cs = CrossSection([pts[::-1]])
    return cs.offset(-inset, JoinType.Miter) if inset else cs


def cross_section(inset=0.0):
    wt, wb, zb = P["w_top"] / 2 - inset, P["w_bot"] / 2 - inset, H()
    return CrossSection([[(-wb, zb + inset), (wb, zb + inset), (wt, -inset), (-wt, -inset)]])


def along_x(cs, h, x0, scale_y=1.0):
    m = Manifold.extrude(cs, h, scale_top=(scale_y, 1.0))
    m = m.transform(np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]], float))
    return m.translate((x0, 0, 0))


def along_y(cs, h=200.0):
    m = Manifold.extrude(cs, h).translate((0, 0, -h / 2))
    return m.transform(np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0]], float))


def cyl_x(r, x0, x1, y, z, n=64):
    return Manifold.cylinder(x1 - x0, r, r, n).rotate((0, 90, 0)).translate((x0, y, z))


def box(x, y, z):
    return Manifold.cube((x[1] - x[0], y[1] - y[0], z[1] - z[0])).translate((x[0], y[0], z[0]))


def slot(cy, cz, vertical, x0=-10, x1=10, shrink=0.0):
    """Langloch durch den Flansch (shrink>0: passender Zapfen mit Spiel)."""
    length, width = P["slot"]
    r, d = width / 2 - shrink, (length - width) / 2
    if vertical:
        ends = cyl_x(r, x0, x1, cy, cz - d, 32) + cyl_x(r, x0, x1, cy, cz + d, 32)
        return ends + box((x0, x1), (cy - r, cy + r), (cz - d, cz + d))
    ends = cyl_x(r, x0, x1, cy - d, cz, 32) + cyl_x(r, x0, x1, cy + d, cz, 32)
    return ends + box((x0, x1), (cy - d, cy + d), (cz - r, cz + r))


def arc_pts(hw):
    """Flanschbogen oben, von +hw nach -hw."""
    hwT, sag, zT = P["fl_w_top"] / 2, P["fl_sag"], P["fl_top"]
    R = (hwT ** 2 + sag ** 2) / (2 * sag)
    return [(y, zT - sag + (R - np.sqrt(R ** 2 - y ** 2))) for y in np.linspace(hw, -hw, 61)]


def hose_path(ext=0.0):
    """Schlauch: kommt innen von unten, durchstoesst den Deckel waagerecht, Haube lenkt ihn nach oben."""
    zp, R = P["port_z"], P["bend_r"]
    xs = -P["fl_t"] - P["plate_t"] - 1.0              # Bogenbeginn knapp ausserhalb der Platte
    pts = [(P["sleeve"] + ext, zp), (xs, zp)]
    pts += [(xs - R * np.sin(a), zp + R - R * np.cos(a)) for a in np.linspace(0, np.pi / 2, 24)[1:]]
    pts += [(xs - R, P["fl_top"] + ext)]
    return pts


def cyl_along(r, p, d, l0, l1, n=64):
    """Zylinder auf Achse p + s*d (d in der XZ-Ebene), s in [l0, l1]."""
    d = np.array(d, float) / np.linalg.norm(d)
    ay = np.degrees(np.arctan2(d[0], d[2]))
    return Manifold.cylinder(l1 - l0, r, r, n).translate((0, 0, l0)).rotate((0, ay, 0)).translate(tuple(p))


def tube(r, pts):
    """Rohr entlang eines Polygonzugs (Huellen aufeinanderfolgender Kugeln)."""
    balls = [Manifold.sphere(r, 40).translate((x, 0, z)) for x, z in pts]
    return sum((Manifold.batch_hull([a, b]) for a, b in zip(balls, balls[1:])), Manifold())


def nose(cy, cz, vertical, behind=0.0):
    """Federnde Rastnase in einem Langloch, ausgerichtet wie das Loch.
    quer (oben): Nase liegt an der oberen Lochkante, Haken nach oben.
    hochkant (Mitte): Nase liegt an der inneren Lochkante, Haken zur Mitte."""
    t, pt, nt, hk = P["fl_t"], P["plate_t"], P["nose_t"], P["nose_hook"]
    sl, sw = P["slot"]
    w = sl - sw - 0.4                                  # Breite = gerader Teil des Langlochs
    gap = 0.15
    x0 = -t - pt + 0.01                                # Nase von der Platte ...
    x1, xt = behind + 0.4, behind + 2.0                # ... bis hinter den Flansch (bzw. die Lasche)
    if not vertical:                                   # quer: duenn in Z
        z1 = cz + sw / 2 - gap
        tab = box((x0, xt), (cy - w / 2, cy + w / 2), (z1 - nt, z1))
        a = box((x1, x1 + 0.3), (cy - w / 2, cy + w / 2), (z1 - 0.1, z1 + hk + gap))
        b = box((xt - 0.1, xt), (cy - w / 2, cy + w / 2), (z1 - 0.1, z1))
    else:                                              # hochkant: duenn in Y, Haken zur Mitte (aussen ist die Seitenwand)
        s = -1 if cy > 0 else 1
        y1 = cy + s * (sw / 2 - gap)
        tab = box((x0, xt), tuple(sorted((y1, y1 - s * nt))), (cz - w / 2, cz + w / 2))
        a = box((x1, x1 + 0.3), tuple(sorted((y1 - s * 0.1, y1 + s * (hk + gap)))), (cz - w / 2, cz + w / 2))
        b = box((xt - 0.1, xt), tuple(sorted((y1 - s * 0.1, y1))), (cz - w / 2, cz + w / 2))
    return tab + Manifold.batch_hull([a, b])


def build_body():
    L, w, t = P["length"], P["wall"], P["fl_t"]
    outer = along_x(cross_section(), L + 5, -t, P["tip_scale"]) ^ along_y(side_profile())
    inner = along_x(cross_section(w), L + 5, -t, P["tip_scale"]) ^ along_y(side_profile(w))
    body = outer - inner

    # Flansch / Trenner
    hwB, zB = P["fl_w_bot"] / 2, H()
    plate = along_x(CrossSection([[(-hwB, zB), (hwB, zB)] + arc_pts(P["fl_w_top"] / 2)]), t, -t)
    opening = along_x(cross_section(w), t + 2, -t - 1)
    my, mh = P["slot_mid"]
    lug_z = zB + mh
    lugs = cyl_x(6, -t - 2, 2, -my, lug_z) + cyl_x(6, -t - 2, 2, my, lug_z)
    plate = plate - (opening - lugs) + (lugs ^ plate.hull())
    boss_z = -12.0
    plate += cyl_x(6, -t, 0, 0, boss_z)
    body += cyl_x(6, 0, 10, 0, boss_z) ^ outer

    m = body + plate
    m -= cyl_x(P["hole_d"] / 2, -t - 1, 15, 0, boss_z)
    m -= cyl_x(P["csk_d"] / 2, -t - 1, -t + 1.5, 0, boss_z)
    ty, td = P["slot_top"]
    for s in (-1, 1):
        m -= slot(s * ty, P["fl_top"] - td, False)     # hier greifen die Zapfen der Abdeckung
        m -= slot(s * my, lug_z, True)

    return m


def build_cover():
    """Deckel fuer die offene Seite des Trenners: Platte mit Flanschkontur, 4 Rastnasen in den
    4 Langloechern, waagerechter Schlauchdurchstoss mit Haube (Prinzip Canyon)."""
    t, pt = P["fl_t"], P["plate_t"]
    rh = (P["hose_od"] + P["hose_clr"]) / 2
    ro = rh + P["guide_wall"]
    hwB, zB = P["fl_w_bot"] / 2, H()
    outline = CrossSection([[(-hwB, zB), (hwB, zB)] + arc_pts(P["fl_w_top"] / 2)])
    cover = along_x(outline, pt, -t - pt - P["clr"])

    # Rastnasen: oben quer, Mitte hochkant
    ty, td = P["slot_top"]
    my, mh = P["slot_mid"]
    for s in (-1, 1):
        cover += nose(s * ty, P["fl_top"] - td, False)
        cover += nose(s * my, zB + mh, True)

    # Schlauchfuehrung wie Canyon: flacher Keil (nur ebene Flaechen) unter dem Austritt.
    # Der Schlauch geht GERADE durch Platte + Keil (kein Knick), der Keil fuehrt ihn am Ausgang
    # sanft nach oben Richtung Cockpit.
    od, wall = P["hose_od"], P["guide_wall"]
    r_grip = od / 2 - P["hose_grip"] / 2              # Durchfuehrung: klemmt den Schlauch
    xo, xi = -t - pt - P["clr"], -t - P["clr"]        # Platte aussen / innen
    zp = P["port_z"]
    W = 2 * (r_grip + wall)
    zA = zp - r_grip - wall                            # hohe Keilflaeche unten (hinter dem Schlauch)
    zC = zA + P["wedge_len"]                           # flache Schraege laeuft oben in die Platte aus
    h = P["wedge_h"]
    tri = CrossSection([[(zA, 0), (zC, 0), (zA, h)]])  # (Z, Abstand von der Platte)
    wedge = Manifold.extrude(tri, W).translate((0, 0, -W / 2))
    wedge = wedge.transform(np.array([[0, -1, 0, xo + 0.01], [0, 0, 1, 0], [1, 0, 0, 0]], float))
    cover += wedge
    cover += cyl_x(r_grip + wall, xi - 0.5, xi + P["sleeve"], 0, zp)      # kurze Huelse innen
    cover -= cyl_x(r_grip, xo - h - 5, xi + P["sleeve"] + 1, 0, zp)       # gerade Durchfuehrung
    # Fasen: innen Einlauf, aussen oben verrundet (Schlauch legt sich nach oben um)
    cover -= Manifold.cylinder(1.5, r_grip + 1.0, r_grip, 48).rotate((0, -90, 0)).translate((xi + P["sleeve"] + 0.01, 0, zp))
    hz = h * (zC - zp) / (zC - zA)                     # Keildicke an der Bohrungsmitte
    cover -= Manifold.cylinder(2.5, r_grip, r_grip + 2.0, 48).rotate((0, -90, 0)).translate((xo - hz + 2.5, 0, zp))
    return cover


def export(m, path, scale):
    mesh = m.scale((scale,) * 3).to_mesh()
    tm = trimesh.Trimesh(mesh.vert_properties[:, :3], mesh.tri_verts, process=False)
    tm.export(path)
    b = tm.bounds
    print(f"{path}: {len(tm.faces)} Dreiecke, watertight={tm.is_watertight}, "
          f"Volumen={tm.volume / 1000:.1f} cm3, Abmessungen={np.round(b[1] - b[0], 1)} mm")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.0)
    a = ap.parse_args()
    body, cover = build_body(), build_cover()
    export(body, "halter.stl", a.scale)
    export(cover, "abdeckung.stl", a.scale)
    export(body + cover, "baugruppe.stl", a.scale)
    print("Ueberschneidung Abdeckung/Halter:", round((body ^ cover).volume(), 2), "mm3")
