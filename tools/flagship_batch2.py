"""Batch 2 of rebuilt motorcycle diagrams.  Run: python tools/flagship_batch2.py"""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from dg import Fig

OUT = os.path.join(os.path.dirname(__file__), "..", "books", "anatomy-of-a-motorcycle", "diagrams")


def ground(g, x0, x1, y, hatch=True):
    g.line(x0, y, x1, y, "k", 0)
    if hatch:
        x = x0 + 8
        while x < x1 - 8:
            g.line(x, y + 2, x - 11, y + 13, "s", None, "fade")
            x += 20


# ===================================================================== 1.1
def contact_patch():
    g = Fig("1.1-A", "Four wheels vs. two", "Why a motorcycle cannot stand on its own",
            "Top view comparing a car's four contact patches, which form a rectangle, with a motorcycle's two, which form a line.",
            "A car's centre of gravity sits inside the rectangle its four tyres define. A motorcycle's two tyres define only a line, "
            "so any sideways push moves the centre of gravity off it and the bike falls.")
    g.line(450, 118, 450, 500, "f", None, "fade")
    # ---- car
    cx = 225
    g.rect(cx - 78, 172, 156, 252, "k", 32, 0)
    for (x, y) in ((cx - 90, 186), (cx + 66, 186), (cx - 90, 368), (cx + 66, 368)):
        g.rect(x, y, 24, 38, "fill-k", 5, anim="fade", i=1)
    g.rect(cx - 78, 205, 156, 186, "tint-b", anim="fade", i=2)
    g.rect(cx - 78, 205, 156, 186, "fb", anim="fade", i=2)
    g.dot(cx, 298, 9, "fill-a", 3)
    g.text(cx + 16, 303, "CG", "tmb ta", i=3)
    g.text(cx, 458, "FOUR PATCHES", "tb mid", i=4)
    g.text(cx, 482, "make a rectangle.", "ts mid", i=4)
    g.text(cx, 504, "The CG sits inside it: stable at rest.", "tsm mid", i=4)
    # ---- motorcycle
    mx = 675
    g.rect(mx - 15, 196, 30, 200, "k", 15, 0)
    g.rect(mx - 15, 186, 30, 36, "fill-k", 5, anim="fade", i=1)
    g.rect(mx - 15, 370, 30, 36, "fill-k", 5, anim="fade", i=1)
    g.line(mx, 222, mx, 370, "f", None, "fade")
    g.dot(mx, 298, 9, "fill-a", 3)
    g.text(mx, 278, "CG", "tmb ta mid", i=3)
    g.arrow(560, 298, 652, 298, "a", 16, 4)
    g.text(560, 276, "ANY SIDE PUSH", "tm ta", i=5)
    g.add('<circle class="fill-a fade" data-i="6" cx="%d" cy="298" r="9" fill-opacity=".28"/>' % (mx + 46))
    g.add('<line class="a fade" data-i="6" x1="%d" y1="298" x2="%d" y2="298" stroke-dasharray="5 5"/>' % (mx + 12, mx + 36))
    g.text(mx + 46, 334, "off the line", "tsm mid", i=6)
    g.text(mx, 458, "TWO PATCHES", "tb mid", i=4)
    g.text(mx, 482, "make a line. No width", "ts mid", i=4)
    g.text(mx, 504, "to lean on: it falls.", "ts mid", i=4)
    return g


# ===================================================================== 4.5
def countersteer():
    g = Fig("4.5-A", "Countersteering", "Steer right to go left: seen from behind",
            "Three rear views showing a rider briefly steering the bars right, the tyre contact patch moving right, the bike falling left, then turning left.",
            "Pushing the bars right briefly moves the front contact patch right. The body, which keeps going straight, is now left of its support "
            "and the bike falls left. Once leaned, it turns left.")
    xs = [160, 450, 740]
    tilts = [0, 7.4, 30]
    Ps = [160, 476, 770]
    Lb = 190
    names = ["1 · STEER RIGHT", "2 · IT TIPS LEFT", "3 · IT TURNS LEFT"]
    cap = ["Push the right grip forward,", "The wheel swings out, the body", "Lean builds the curve. Then"]
    cap2 = ["just for a moment.", "keeps going: it tips over.", "steer normally and hold it."]
    for k, cx in enumerate(xs):
        b = k * 3
        gy = 392
        g.line(cx - 112, gy, cx + 112, gy, "k", b)
        for x in range(cx - 104, cx + 104, 22):
            g.line(x, gy + 2, x - 10, gy + 12, "s", None, "fade")
        a = math.radians(tilts[k])
        P = (Ps[k], gy)
        ux, uy = -math.sin(a), -math.cos(a)           # up the bike axis (leans left = toward -x)
        CG = (P[0] + 150 * ux, P[1] + 150 * uy)
        T = (P[0] + (Lb + 24) * ux, P[1] + (Lb + 24) * uy)
        tc = (P[0] + 40 * ux, P[1] + 40 * uy)
        g.add('<ellipse class="k draw" data-i="%d" cx="%.1f" cy="%.1f" rx="12" ry="42" transform="rotate(%.1f %.1f %.1f)"/>' % (b + 1, tc[0], tc[1], -tilts[k], tc[0], tc[1]))
        g.line(P[0] + 80 * ux, P[1] + 80 * uy, T[0], T[1], "s thick", b + 1)
        # handlebars
        nx, ny = math.cos(a), -math.sin(a)
        g.line(T[0] - 34 * nx, T[1] - 34 * ny, T[0] + 34 * nx, T[1] + 34 * ny, "k thick", b + 1)
        g.circle(CG[0], CG[1], 17, "fill-d k", b + 1)
        g.dot(CG[0], CG[1], 4, "fill-k", b + 2)
        g.dot(P[0], P[1], 6, "fill-a", b + 2)
        g.text(cx, 462, names[k], "tb mid", i=b + 2)
        g.text(cx, 486, cap[k], "tsm mid", i=b + 3)
        g.text(cx, 506, cap2[k], "tsm mid", i=b + 3)
    # panel 1: the steering input
    g.arrow(135, 150, 205, 150, "a", 16, 2)
    g.text(170, 130, "BARS TURN RIGHT", "tm ta mid", i=2)
    # panel 2: where the patch went
    g.add('<line class="f fade" data-i="5" x1="450" y1="392" x2="450" y2="196" stroke-dasharray="5 5" />')
    g.arrow(450, 418, 476, 418, "a", 12, 5)
    g.text(490, 423, "PATCH MOVES RIGHT", "tm ta", i=5)
    # panel 3: path
    g.arrow(790, 428, 700, 428, "b", 14, 8)
    g.text(790, 418, "PATH CURVES LEFT", "tm tbl end", i=8)
    # flow arrows between panels
    g.arrow(298, 296, 330, 296, "s", 12, 3)
    g.arrow(588, 296, 620, 296, "s", 12, 6)
    return g


# ===================================================================== 6.4
def friction_circle():
    g = Fig("6.4-A", "The friction circle", "Grip is one shared budget",
            "A circle whose axes are braking and cornering force. Any combination inside the circle is available; the edge is the limit of grip.",
            "Braking force is plotted vertically and cornering force horizontally. The tyre can produce any combination inside the circle. "
            "Using all grip for braking leaves none for cornering, and trail braking shares it.")
    cx, cy, R = 330, 298, 148
    g.circle(cx, cy, R, "tint-b", anim="fade", i=1)
    g.circle(cx, cy, R, "b", 0)
    g.circle(cx, cy, R * 0.5, "f", None, "fade")
    g.line(cx, cy - R - 26, cx, cy + R + 26, "s", 1)
    g.line(cx - R - 26, cy, cx + R + 26, cy, "s", 1)
    g.text(cx, cy - R - 38, "BRAKING", "tmb mid", i=2)
    g.text(cx, cy + R + 52, "ACCELERATING", "tmb mid", i=2)
    g.text(cx + R + 38, cy + 5, "CORNERING", "tmb", i=2)
    g.text(cx - R - 38, cy + 5, "CORNERING", "tmb end", i=2)
    a = math.radians(45)
    px, py = cx + R * math.cos(a), cy - R * math.sin(a)
    g.line(px, py, px, cy, "fb", None, "fade")
    g.line(px, py, cx, py, "fb", None, "fade")
    g.line(cx, cy, cx, py, "g thick", 3)
    g.line(cx, cy, px, cy, "g thick", 3)
    g.arrow(cx, cy, px, py, "a", 18, 3)
    g.dot(px, py, 8, "fill-a", 4)
    g.dot(cx, cy - R, 8, "fill-b", 4)
    g.dot(cx + R, cy, 8, "fill-b", 4)
    g.text(cx + 16, cy - R - 12, "ALL BRAKING", "tm tbl", i=4)
    g.text(cx + R + 14, cy - 14, "ALL CORNERING", "tm tbl", i=4)
    g.text(px + 14, py - 12, "TRAIL BRAKING", "tmb ta", i=5)
    g.text(px + 14, py + 8, "shares the grip", "tsm", i=5)
    g.text(cx - 12, (cy + py) / 2 + 5, "braking part", "tsm end", i=6)
    g.text((cx + px) / 2, cy + 26, "cornering part", "tsm mid", i=6)
    kx = 650
    g.text(kx, 168, "INSIDE THE CIRCLE", "tmb", i=7)
    g.text(kx, 192, "grip to spare", "ts", i=7)
    g.text(kx, 242, "ON THE EDGE", "tmb tg", i=8)
    g.text(kx, 266, "every bit of grip used", "ts", i=8)
    g.text(kx, 316, "OUTSIDE", "tmb ta", i=9)
    g.text(kx, 340, "the tyre slides", "ts", i=9)
    g.text(450, 530, "Braking and cornering draw from the same budget.", "ts mid", i=10)
    return g


# ===================================================================== 7.5
def weight_transfer():
    g = Fig("7.5-A", "Weight transfer under braking", "Why the front tyre can do most of the stopping",
            "Side view of a braking motorcycle showing load shifting from the rear tyre to the front tyre, with centre of mass height h and wheelbase L.",
            "Under braking the inertia at the centre of mass tends to carry the bike forward, pressing the front tyre harder and unloading the rear. "
            "The load moved equals mass times deceleration times h divided by L.")
    gy = 430
    rx, fx_ = 300, 640
    g.line(120, gy, 820, gy, "k", 0)
    for x in range(130, 820, 22):
        g.line(x, gy + 2, x - 11, gy + 13, "s", None, "fade")
    for cx in (rx, fx_):
        g.circle(cx, gy - 62, 62, "k", 1)
        g.circle(cx, gy - 62, 46, "s", 1)
        g.dot(cx, gy - 62, 6, "fill-k", 2)
    g.poly([(rx, gy - 62), (362, 296), (508, 296), (594, 252), (fx_, gy - 62)], "k thick", 2)
    g.line(336, 282, 440, 282, "s thick", 3)
    CG = (452, 232)
    g.circle(CG[0], CG[1], 20, "fill-d k", 3)
    g.dot(CG[0], CG[1], 5, "fill-a", 4)
    g.text(CG[0] - 2, CG[1] - 32, "CG", "tmb ta mid", i=4)
    # inertia
    g.line(CG[0] + 26, CG[1], 566, CG[1], "a", 5)
    g.add('<polygon class="fill-a pop" data-i="6" points="%d,%d %d,%d %d,%d"/>' % (580, CG[1], 562, CG[1] - 9, 562, CG[1] + 9))
    g.text(CG[0] + 90, CG[1] - 18, "INERTIA", "tmb ta", i=5)
    # braking forces at the tyres (point backwards = left)
    g.arrow(fx_, gy + 22, fx_ - 84, gy + 22, "a", 15, 6)
    g.arrow(rx, gy + 22, rx - 34, gy + 22, "a", 15, 6)
    g.text(fx_ - 40, gy + 52, "BRAKE FORCE", "tm ta mid", i=7)
    # h and L
    g.dim(404, gy, 404, CG[1], "b", 3, 7)
    g.text(392, (gy + CG[1]) / 2 + 12, "h", "fx tbl end", i=4)
    g.dim(rx, gy + 78, fx_, gy + 78, "b", 3, 7)
    g.text((rx + fx_) / 2, gy + 106, "wheelbase L", "tmb tbl mid", i=4)
    # load bars: before (dashed) vs braking (filled)
    for x, h0, h1, label, col in ((188, 66, 30, "REAR LOAD", "tint-a"), (748, 66, 112, "FRONT LOAD", "tint-b2")):
        g.add('<rect class="f fade" data-i="8" x="%d" y="%d" width="30" height="%d" stroke-dasharray="4 4"/>' % (x, gy - h0, h0))
        g.rect(x, gy - h1, 30, h1, col, anim="fade", i=9)
        g.rect(x, gy - h1, 30, h1, "b" if h1 > h0 else "a", anim="fade", i=9)
        g.text(x + 15, gy - max(h0, h1) - 14, label, "tmb mid", i=9)
    g.text(40, 140, "Load moved = m · a · h / L", "fx", i=10)
    g.text(40, 168, "A taller CG or a shorter wheelbase moves more.", "ts", i=10)
    g.text(40, 194, "Dashed = at rest. Solid = under braking.", "tsm", i=10)
    return g


# ===================================================================== 2.12
def power_curves():
    g = Fig("2.12-A", "Torque and power vs. RPM", "Two curves, two peaks, one useful band",
            "Chart of engine torque and power against RPM, with the torque peak earlier than the power peak and the band between them highlighted.",
            "Torque rises and falls with RPM. Power equals torque times RPM, so it keeps climbing after torque peaks and peaks later. "
            "The band between the two peaks is where the engine is most usable.")
    x0, x1, y0, y1 = 100, 820, 448, 138
    def X(r): return x0 + (r / 14.0) * (x1 - x0)
    pts = []
    for i in range(0, 61):
        r = 1.5 + (14 - 1.5) * i / 60.0
        t = 1 - 0.85 * ((r - 8) / 7.5) ** 2
        pts.append((r, t, t * r))
    tmax = max(p[1] for p in pts)
    pmax = max(p[2] for p in pts)
    tp = max(pts, key=lambda p: p[1])
    pp = max(pts, key=lambda p: p[2])
    def Y(v): return y0 - v * (y0 - y1 - 20)
    # band between peaks
    g.rect(X(tp[0]), y1 - 10, X(pp[0]) - X(tp[0]), y0 - y1 + 10, "tint-g", anim="fade", i=2)
    g.text((X(tp[0]) + X(pp[0])) / 2, y1 + 8, "USEFUL BAND", "tmb tg mid", i=7)
    # axes
    g.line(x0, y0, x1 + 10, y0, "k", 0)
    g.line(x0, y0, x0, y1 - 10, "k", 0)
    for r in range(0, 15, 2):
        g.line(X(r), y0, X(r), y0 + 8, "s", 1)
        g.text(X(r), y0 + 28, "%d" % r, "tm mid", i=1)
    g.text(x1 + 6, y0 + 28, "RPM x1000", "tm end", i=1)
    # curves
    dt = "M" + " L".join("%s %s" % ("%.1f" % X(p[0]), "%.1f" % Y(p[1] / tmax)) for p in pts)
    dp = "M" + " L".join("%s %s" % ("%.1f" % X(p[0]), "%.1f" % Y(p[2] / pmax)) for p in pts)
    g.path(dt, "b", 3)
    g.path(dp, "a", 4)
    # peak markers
    for p, vmax, idx, cls, lab, anchor in ((tp, tmax, 1, "fill-b", "PEAK TORQUE", 1), (pp, pmax, 2, "fill-a", "PEAK POWER", 2)):
        val = (p[1] / tmax) if idx == 1 else (p[2] / pmax)
        g.line(X(p[0]), Y(val), X(p[0]), y0, "f", None, "fade")
        g.dot(X(p[0]), Y(val), 8, cls, 6)
    g.text(X(tp[0]) - 12, Y(1.0) - 14, "PEAK TORQUE", "tmb tbl end", i=6)
    g.text(X(pp[0]) + 14, Y(1.0) - 14, "PEAK POWER", "tmb ta", i=6)
    g.text(X(2.1), Y(0.46) + 24, "TORQUE", "tb tbl", i=5)
    g.text(X(12.2), Y(0.80), "POWER", "tb ta", i=5)
    g.text(450, 524, "Power is torque times speed, so it peaks later than torque.", "ts mid", i=8)
    return g


# ===================================================================== 9.5
def line_choice():
    g = Fig("9.5-A", "Line choice sets your radius", "Same corner, two lines, two different arcs",
            "Top view of a right-hand corner comparing hugging the inside line with a wide-in, late-apex, wide-out line that has a larger radius.",
            "A tighter line through a corner has a smaller radius, so it needs more lean for the same speed. Entering wide, apexing late and exiting wide "
            "opens up a larger radius and asks for less lean.")
    # road
    g.path("M70 190 H500 A210 210 0 0 1 710 400 V535", "k", 0)
    g.path("M70 330 H500 A70 70 0 0 1 570 400 V535", "k", 0)
    g.add('<path class="tint-k fade" data-i="1" d="M70 190 H500 A210 210 0 0 1 710 400 V535 H570 V400 A70 70 0 0 0 500 330 H70 Z"/>')
    g.path("M70 260 H500 A140 140 0 0 1 640 400 V535", "f", None, "fade")
    # tight line
    g.path("M70 308 H500 A92 92 0 0 1 592 400 V535", "s thick", 2)
    # wide line
    g.path("M70 208 H300 C440 208 560 246 592 352 S682 470 694 535", "a", 3)
    g.arrow(160, 308, 220, 308, "s", 14, 4)
    g.arrow(160, 208, 220, 208, "a", 14, 4)
    g.dot(592, 352, 7, "fill-a", 5)
    g.text(612, 340, "LATE APEX", "tmb ta", i=5)
    g.text(70, 172, "ENTRY", "tm", i=1)
    g.text(718, 520, "EXIT", "tm", i=1)
    # legend
    lx = 80
    g.line(lx, 408, lx + 40, 408, "s thick", 6)
    g.text(lx + 54, 414, "HUG THE INSIDE", "t", i=6)
    g.text(lx + 54, 436, "tight arc: more lean at the same speed", "tsm", i=6)
    g.line(lx, 478, lx + 40, 478, "a", 7)
    g.text(lx + 54, 484, "WIDE IN · LATE APEX · WIDE OUT", "t ta", i=7)
    g.text(lx + 54, 506, "bigger arc: less lean, or more speed", "tsm", i=7)
    return g


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("fig-1-1-a.svg", contact_patch), ("fig-4-5-a.svg", countersteer), ("fig-6-4-a.svg", friction_circle),
                     ("fig-7-5-a.svg", weight_transfer), ("fig-2-12-a.svg", power_curves), ("fig-9-5-a.svg", line_choice)):
        print("wrote", os.path.normpath(fn().save(os.path.join(OUT, name))))
