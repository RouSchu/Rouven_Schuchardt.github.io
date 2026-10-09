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
    bend_r=20.0,          # Biegeradius Schlauchmitte (zu klein -> Schlauch knickt)
    bend_z=-10.0,         # Bogen beginnt so tief unter der Abdeckung (je tiefer, desto flacher die Haube)
    port_x=35.0,          # senkrechter Durchstoss: Abstand vom Trenner
    sleeve=8.0,           # Fuehrungshuelse unten: Laenge unterhalb des Bogenbeginns
    clr=0.2,              # Spiel Abdeckung <-> Halter
    # Loecher im Flansch (gemessen/abgelesen)
    slot_top=(15.0, 7.0), # obere Langloecher: +-Y, Abstand unter den Ecken
    slot_mid=(16.0, 30.0),# mittlere Langloecher: +-Y, Hoehe ueber Unterkante
    slot=(7.0, 3.5),      # Langloch L x B
    hole_d=4.0, csk_d=8.0,
    # Rastung der Abdeckung
    hook_x=12.0,          # Rasthaken: Abstand von der Spitze
    hook_y=12.3,          # Rasthaken: Abstand von der Mitte
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
    """Schlauch: senkrecht von unten, 90-Grad-Bogen, waagerecht nach vorn (Richtung Cockpit)."""
    xp, zb, R, L = P["port_x"], P["bend_z"], P["bend_r"], P["length"]
    pts = [(xp, zb - P["sleeve"] - ext), (xp, zb)]
    pts += [(xp + R - R * np.cos(a), zb + R * np.sin(a)) for a in np.linspace(0, np.pi / 2, 24)[1:]]
    pts += [(max(L, xp + R) + ext, zb + R)]
    return pts


def tube(r, pts):
    """Rohr entlang eines Polygonzugs (Huellen aufeinanderfolgender Kugeln)."""
    balls = [Manifold.sphere(r, 40).translate((x, 0, z)) for x, z in pts]
    return Manifold.batch_hull([balls[0], balls[1]]) + sum(
        (Manifold.batch_hull([a, b]) for a, b in zip(balls[1:], balls[2:])), Manifold())


def guide_outer():
    return tube(P["hose_od"] / 2 + P["hose_clr"] / 2 + P["guide_wall"], hose_path())


def roof_cutout():
    """Ausschnitt im Dach des Originalteils fuer die Fuehrung unter der Abdeckung."""
    lo, hi = (guide_outer() ^ box((-50, 150), (-50, 50), (-50, 0))).bounding_box()[:3], \
        (guide_outer() ^ box((-50, 150), (-50, 50), (-50, 0))).bounding_box()[3:]
    c = P["clr"] + 0.3
    return box((lo[0] - c, hi[0] + c), (lo[1] - c, hi[1] + c), (-30, 1))


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

    # Ausschnitt im Dach fuer die Schlauchfuehrung (am Original ausschneiden)
    m -= roof_cutout()

    # Schlitze im Dach fuer die Rasthaken
    for s in (-1, 1):
        y0 = P["hook_y"] - 0.9
        m -= box((L - P["hook_x"] - 4.2, L - P["hook_x"] + 4.2),
                 tuple(sorted((s * y0, s * (y0 + 2.8)))), (-w - 1, 1))
    return m


def build_cover():
    """Abdeckung buendig zum Flanschbogen; Schlauch kommt senkrecht von unten, wird in einer
    keilfoermigen Haube (wie Canyon) nach vorn umgelenkt und dort gehalten."""
    L, w, t, c = P["length"], P["wall"], P["fl_t"], P["clr"]
    rh = (P["hose_od"] + P["hose_clr"]) / 2

    hw = P["w_top"] / 2
    prof = CrossSection([[(-hw, 0), (hw, 0)] + arc_pts(hw)])
    cover = along_x(prof, L + 5, -t, P["tip_scale"]) ^ box((c, L), (-50, 50), (-50, 50))

    # Fuehrung: Huelle unten + Bogen; ueber der Oberflaeche zu einem Keil verrundet
    g = guide_outer() ^ box((-50, L), (-50, 50), (P["bend_z"] - P["sleeve"], 100))
    above = g ^ box((-50, 150), (-50, 50), (0, 100))
    ro = P["hose_od"] / 2 + P["hose_clr"] / 2 + P["guide_wall"]
    xp = P["port_x"]
    ramp_foot = box((xp - ro - 14, xp - ro - 13.9), (-ro * 0.6, ro * 0.6), (0, 3))   # Keil hinten (Canyon-Form)
    cover += g + Manifold.batch_hull([above, ramp_foot])
    cover -= tube(rh, hose_path(ext=15))                    # Schlauchkanal
    # Einlauffasen unten und am Austritt vorn
    xp, zb, R = P["port_x"], P["bend_z"], P["bend_r"]
    zl = zb - P["sleeve"]
    cover -= Manifold.cylinder(2.0, rh + 1.2, rh, 48).translate((xp, 0, zl - 0.01))
    xe = max(L, xp + R)
    cover -= Manifold.cylinder(2.0, rh, rh + 1.2, 48).rotate((0, 90, 0)).translate((xe - 1.99, 0, zb + R))

    # Zapfen hinten -> greifen in die oberen Langloecher des Flansches
    ty, td = P["slot_top"]
    zc = P["fl_top"] - td
    for s in (-1, 1):
        cover += slot(s * ty, zc, False, -t - 1.5, c + 1, shrink=0.25)

    # Rasthaken vorn -> rasten unter dem Dach des Koerpers ein
    xh = L - P["hook_x"]
    for s in (-1, 1):
        y0 = P["hook_y"] - 0.7
        arm = box((xh - 3.8, xh + 3.8), tuple(sorted((s * y0, s * (y0 + 1.4)))), (-w - 2.4, 0.5))
        top = box((xh - 3.8, xh + 3.8), tuple(sorted((s * (y0 + 1.4), s * (y0 + 2.3)))), (-w - 0.9, -w - 0.7))
        bot = box((xh - 3.8, xh + 3.8), tuple(sorted((s * (y0 + 1.4), s * (y0 + 1.45)))), (-w - 2.4, -w - 2.3))
        cover += arm + Manifold.batch_hull([top, bot])
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
