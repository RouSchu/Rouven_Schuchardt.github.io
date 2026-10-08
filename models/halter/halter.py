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
    hose_x_in=14.0,       # Eintritt unten: Abstand vom Flansch
    # Einklick-Deckel mit Schlauchdurchfuehrung (Prinzip Canyon)
    win_t=0.25,           # Lage des Fensters auf der Bogenkontur (0=Spitze, 1=unten)
    win_l=28.0,           # Fensterlaenge (entlang Kontur)
    win_w=20.0,           # Fensterbreite (Y)
    rebate=2.0,           # Falz rundum fuer die Deckelplatte
    lid_t=1.6,            # Deckelplattendicke (= Falztiefe)
    frame=5.0,            # Verstaerkungsrahmen innen um das Fenster
    clr=0.2,              # Spiel Deckel <-> Fenster
    clip_hole=(9.0, 1.8), # seitliche Rastloecher: Laenge x Hoehe
    clip_depth=4.6,       # Tiefe der Rastloch-Oberkante unter der Oberflaeche
    exit_angle=25.0,      # Schlauchaustritt: Grad unter der Waagerechten (nach vorn)
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


def solid(d=0.0):
    """Aussenkoerper, um d nach innen versetzt (d=wall -> Innenraum)."""
    L = P["length"]
    return along_x(cross_section(d), L + 5, -P["fl_t"], P["tip_scale"]) ^ along_y(side_profile(d))


def window_frame():
    """Lokales Koordinatensystem am Fenster: u entlang Kontur, v=Y, w nach innen."""
    L, fd, fdp, t = P["length"], P["front_drop"], P["foot_depth"], P["win_t"]
    p0, p1, p2 = np.array([L, -fd]), np.array([46, -40]), np.array([fdp, -95.0])
    o = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2
    d = -(2 * (1 - t) * (p1 - p0) + 2 * t * (p2 - p1))
    tu = d / np.linalg.norm(d)                      # Richtung Spitze
    n = np.array([tu[1], -tu[0]])                   # nach aussen
    T = np.array([[tu[0], 0, -n[0], o[0]],
                  [0, 1, 0, 0],
                  [tu[1], 0, -n[1], o[1]]])
    return T, np.array([o[0], 0, o[1]]), np.array([n[0], 0, n[1]])


def local_box(T, u, v, w):
    """Quader im Fenster-System: u,v,w = (min,max)-Paare."""
    b = Manifold.cube((u[1] - u[0], v[1] - v[0], w[1] - w[0])).translate((u[0], v[0], w[0]))
    return b.transform(T)


def sym(a):
    return (-a / 2, a / 2)


def hose_axis():
    a = np.radians(P["exit_angle"])
    return np.array([np.cos(a), 0, -np.sin(a)])


def cyl_along(r, p, d, l0, l1, r2=None):
    """Zylinder (r -> r2) auf Achse p + s*d, s in [l0, l1]."""
    d = d / np.linalg.norm(d)
    c = Manifold.cylinder(l1 - l0, r, r if r2 is None else r2, 64)
    ay = np.degrees(np.arctan2(d[0], d[2]))         # Drehung z -> d (d in XZ-Ebene)
    return c.translate((0, 0, l0)).rotate((0, ay, 0)).translate(tuple(p))


def clip_slots(T):
    """Kleine seitliche Rastloecher im Rahmen (links/rechts vom Fenster)."""
    hl, hh = P["clip_hole"]
    v0, w0 = P["win_w"] / 2, P["clip_depth"]
    return [local_box(T, sym(hl), (v0 - 0.5, v0 + 6), (w0, w0 + hh)),
            local_box(T, sym(hl), (-v0 - 6, -v0 + 0.5), (w0, w0 + hh))]


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

    # Verstaerkungsrahmen innen um das Deckelfenster
    T, _, _ = window_frame()
    fr, wl, ww = P["frame"], P["win_l"], P["win_w"]
    body += (inner - solid(w + fr)) ^ local_box(T, sym(wl + 2 * fr), sym(ww + 2 * fr), (-1, w + fr + 3))

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

    # Schlaucheintritt unten (von der Flasche), mit Fase
    rb = (P["hose_od"] + P["hose_gap"]) / 2
    zb, xi = P["body_bottom"], P["hose_x_in"]
    m -= Manifold.cylinder(w + 2, rb, rb, 48).translate((xi, 0, zb - 1))
    m -= Manifold.cylinder(2, rb + 2, rb, 48).translate((xi, 0, zb - 0.01))

    # Deckelfenster: Falz + Durchbruch + seitliche Rastloecher
    rbt, lt = P["rebate"], P["lid_t"]
    m -= (outer - solid(lt)) ^ local_box(T, sym(wl + 2 * rbt), sym(ww + 2 * rbt), (-5, 5))
    m -= local_box(T, sym(wl), sym(ww), (-5, w + fr + 0.5))
    for c in clip_slots(T):
        m -= c
    return m


def build_lid():
    """Einklick-Deckel: Platte im Falz, Stopfen im Fenster, 2 Rastarme, Schlauchtuelle."""
    T, o, n = window_frame()
    w, c, lt = P["wall"], P["clr"], P["lid_t"]
    wl, ww, rbt = P["win_l"], P["win_w"], P["rebate"]
    hl, hh = P["clip_hole"]
    cd = P["clip_depth"]

    plate = (solid(0) - solid(lt)) ^ local_box(T, sym(wl + 2 * rbt - 2 * c), sym(ww + 2 * rbt - 2 * c), (-5, 5))
    plug = (solid(lt) - solid(w)) ^ local_box(T, sym(wl - 2 * c), sym(ww - 2 * c), (-5, 8))
    lid = plate + plug

    # Rastarme mit Rampen-Nase (rastet in die seitlichen Loecher ein)
    at, nose = 1.4, 0.9
    for s in (-1, 1):
        vi = s * (ww / 2 - c)                          # Aussenkante Arm
        arm = local_box(T, sym(hl - 1.5), tuple(sorted((vi, vi - s * at))), (w - 0.5, cd + hh + 1.2))
        tip_top = local_box(T, sym(hl - 1.5), tuple(sorted((vi, vi + s * nose))), (cd + c, cd + c + 0.2))
        tip_bot = local_box(T, sym(hl - 1.5), tuple(sorted((vi, vi + s * 0.05))), (cd + hh - 0.1, cd + hh))
        lid += arm + Manifold.batch_hull([tip_top, tip_bot])

    # Schlauchtuelle: haelt den Schlauch, fuehrt ihn nach vorn Richtung Cockpit
    d = hose_axis()
    rh = P["hose_od"] / 2 + 0.15
    collar = cyl_along(rh + 1.8, o, d, 0, 9, rh + 1.2)
    collar -= solid(0) - local_box(T, sym(wl + 2 * rbt), sym(ww + 2 * rbt), (-5, 12))
    lid += collar
    lid -= cyl_along(rh, o, d, -25, 15)
    lid -= cyl_along(rh + 1.0, o, d, 7.5, 9.01, rh)    # Einlauffase vorne
    return lid


def export(m, path, scale):
    m = m.scale((scale,) * 3)
    mesh = m.to_mesh()
    tm = trimesh.Trimesh(mesh.vert_properties[:, :3], mesh.tri_verts, process=False)
    tm.export(path)
    b = tm.bounds
    print(f"{path}: {len(tm.faces)} Dreiecke, watertight={tm.is_watertight}, "
          f"Volumen={tm.volume / 1000:.1f} cm3, Abmessungen={np.round(b[1] - b[0], 1)} mm")
    return tm


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.0)
    a = ap.parse_args()
    body, lid = build(), build_lid()
    export(body, "halter.stl", a.scale)
    export(lid, "deckel.stl", a.scale)
    export(body + lid, "baugruppe.stl", a.scale)
    print("Ueberschneidung Deckel/Halter:", round((body ^ lid).volume(), 2), "mm3")
