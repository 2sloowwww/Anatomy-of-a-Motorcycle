"""Flagship motorcycle diagrams, rebuilt on the Knowbase diagram kit.
Run:  python tools/flagship_motorcycle.py
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from dg import Fig

OUT = os.path.join(os.path.dirname(__file__), "..", "books", "anatomy-of-a-motorcycle", "diagrams")


# =====================================================================
# 2.2  The four-stroke cycle
# =====================================================================
def four_stroke():
    g = Fig("2.2-A", "The four-stroke cycle", "720 degrees of crank rotation, one power stroke",
            "The four-stroke cycle: intake, compression, power and exhaust.",
            "Four cylinders side by side show piston position, valve state and gas flow for intake, compression, power and exhaust, "
            "with a small crank icon under each showing which half-turn of the crankshaft it takes. Only the power stroke makes work.")
    cols = [130, 340, 550, 760]
    names = ["Intake", "Compression", "Power", "Exhaust"]
    ranges = ["0° → 180°", "180° → 360°", "360° → 540°", "540° → 720°"]
    desc = [("Piston falls, intake", "valve opens, mixture", "is drawn in."),
            ("Both valves shut.", "The rising piston", "squeezes the mixture."),
            ("Spark! The burn", "shoves the piston down.", "The only work done."),
            ("Exhaust valve opens,", "the rising piston", "pushes burnt gas out.")]
    piston_y = [214, 226, 180, 226]          # top of piston
    g.rect(cols[2] - 102, 100, 204, 424, "tint-a", 8, anim="fade", i=2)
    g.text(860, 84, "= 2 crank turns", "tm end", i=1)
    for k, cx in enumerate(cols):
        b = k * 2
        g.path("M%d 150V300M%d 150V300" % (cx - 46, cx + 46), "k", b)
        g.line(cx - 58, 150, cx + 58, 150, "k thick", b)
        h = piston_y[k] - 150
        tint = ["tint-b", "tint-b2", "tint-a2", "tint-k"][k]
        g.rect(cx - 44, 152, 88, h - 2, tint, anim="fade", i=b + 1)
        g.rect(cx - 44, piston_y[k], 88, 30, "fill-d k", 3, i=b + 1)
        g.line(cx - 44, piston_y[k] + 9, cx + 44, piston_y[k] + 9, "s", b + 1)
        g.line(cx - 44, piston_y[k] + 17, cx + 44, piston_y[k] + 17, "s", b + 1)
        for vx, opened, col in ((cx - 24, k == 0, "b"), (cx + 24, k == 3, "a")):
            dy = 14 if opened else 0
            g.line(vx, 112, vx, 150 + dy - 2, col if opened else "k", b + 1)
            g.rect(vx - 14, 148 + dy, 28, 6, ("fill-b" if col == "b" else "fill-a") if opened else "fill-k", 2, anim="fade", i=b + 1)
        if k == 0:
            g.arrow(cx - 74, 120, cx - 34, 142, "b", 14, b + 2)
        if k == 3:
            g.arrow(cx + 34, 142, cx + 74, 120, "a", 14, b + 2)
        if k == 2:
            g.poly([(cx - 8, 112), (cx + 4, 126), (cx - 4, 130), (cx + 8, 146)], "a", b + 1)
            g.text(cx + 46, 126, "SPARK", "tm ta", i=b + 3)
        py = piston_y[k] + 15
        if k in (0, 2):
            g.arrow(cx + 70, py - 26, cx + 70, py + 30, "g" if k == 2 else "s", 14, b + 2)
        else:
            g.arrow(cx + 70, py + 26, cx + 70, py - 30, "s", 14, b + 2)
        cy = 346
        g.circle(cx, cy, 24, "s", b + 2)
        if k % 2 == 0:
            g.arc(cx, cy, 24, -90, 90, "g" if k == 2 else "b", b + 2, head=11)
        else:
            g.arc(cx, cy, 24, 90, 270, "g" if k == 2 else "b", b + 2, head=11)
        g.text(cx, 398, "STROKE %d" % (k + 1), "tm mid", i=b + 2)
        g.text(cx, 424, names[k], "tb mid" + (" ta" if k == 2 else ""), i=b + 2)
        g.text(cx, 446, ranges[k], "tm mid", i=b + 2)
        for n, line in enumerate(desc[k]):
            g.text(cx, 474 + n * 20, line, "tsm mid", i=b + 3)
    return g


# =====================================================================
# 4.4  Rake and trail
# =====================================================================
def rake_trail():
    g = Fig("4.4-A", "Rake and trail", "Why the front wheel wants to go straight",
            "Side view of a motorcycle front end showing the steering axis, rake angle, fork offset and trail.",
            "The steering axis tilts back from vertical by the rake angle. It meets the ground ahead of the tyre's contact patch; "
            "that distance along the ground is trail, which drags the wheel straight like a caster.")
    th = math.radians(25)
    R, H = 120, (470, 338)
    P = (H[0], H[1] + R)                          # contact patch
    off = 12                                      # fork offset (axle ahead of axis)
    ax_hub = H[0] + off / math.cos(th)            # axis x at hub height
    A = (ax_hub - math.tan(th) * R, P[1])         # axis meets ground
    T = (A[0] + math.tan(th) * (P[1] - 170), 170) # top of the axis
    # ground + hatch
    g.line(110, P[1], 800, P[1], "k", 0)
    for x in range(120, 800, 22):
        g.line(x, P[1] + 2, x - 12, P[1] + 14, "s", None, "fade")
    # wheel
    g.circle(H[0], H[1], R, "k", 1)
    g.circle(H[0], H[1], R - 15, "s", 1)
    for a in (0, 60, 120):
        g.line(H[0] + (R - 15) * math.cos(math.radians(a)), H[1] + (R - 15) * math.sin(math.radians(a)),
               H[0] - (R - 15) * math.cos(math.radians(a)), H[1] - (R - 15) * math.sin(math.radians(a)), "s", 1, "fade")
    g.dot(H[0], H[1], 7, "fill-k", 3)
    # fork (through the hub, parallel to the axis)
    u = (math.sin(th), -math.cos(th))
    fk_top = (H[0] + 235 * u[0], H[1] + 235 * u[1])
    g.line(H[0], H[1], fk_top[0], fk_top[1], "s thick", 2)
    # steering axis (extends a little below the ground)
    below = (A[0] - 16 * math.sin(th), A[1] + 16 * math.cos(th))
    g.line(below[0], below[1], T[0] + 24 * math.sin(th), T[1] - 24 * math.cos(th), "b", 3)
    # head tube
    g.line(T[0] - 56 * math.sin(th), T[1] + 56 * math.cos(th), T[0], T[1], "k thick", 3)
    # vertical reference + rake arc
    g.line(T[0], T[1], T[0], T[1] + 118, "f", None, "fade")
    g.arc(T[0], T[1], 96, 90, 90 + 25, "g", 4)
    g.text(T[0] + 14, T[1] + 70, "RAKE", "tmb tg", i=5)
    g.text(T[0] + 14, T[1] + 96, "25°", "tb tg", i=5)
    # vertical through the contact patch
    g.line(P[0], P[1], P[0], H[1] + 2, "f", None, "fade")
    # axis foot + contact patch markers
    g.dot(A[0], A[1], 7, "fill-b", 4)
    g.dot(P[0], P[1], 7, "fill-a", 4)
    # trail dimension
    ydim = P[1] + 34
    g.line(A[0], P[1] + 8, A[0], ydim + 12, "fb", None, "fade")
    g.line(P[0], P[1] + 8, P[0], ydim + 12, "fb", None, "fade")
    g.dim(A[0], ydim, P[0], ydim, "a", 6)
    g.text((A[0] + P[0]) / 2, ydim + 36, "TRAIL", "tb ta mid", i=7)
    g.text(A[0] - 16, ydim + 5, "AXIS MEETS GROUND", "tmb tbl end", i=4)
    g.text(P[0] + 18, ydim + 5, "TYRE TOUCHES", "tmb ta", i=4)
    # fork offset callout
    yo = 292
    xf = H[0] + (H[1] - yo) * math.tan(th)
    xa = A[0] + (P[1] - yo) * math.tan(th)
    g.line((xf + xa) / 2, yo, 640, yo, "f", None, "fade")
    g.text(648, yo + 6, "FORK OFFSET", "tmb", i=6)
    g.text(648, yo + 26, "axle sits ahead of the axis", "ts", i=6)
    # travel
    g.arrow(330, 412, 200, 412, "s", 14, 0)
    g.text(265, 396, "TRAVEL", "tm mid", i=1)
    # explanation
    for n, s in enumerate(["The axis hits the ground AHEAD of the tyre.",
                           "That gap is trail. It drags the wheel straight,",
                           "the way a trolley caster follows its handle."]):
        g.text(40, 128 + n * 26, s, "ts", i=8)
    g.text(640, 366, "MORE TRAIL", "tb", i=8)
    g.text(640, 388, "steadier, slower to turn", "ts", i=8)
    g.text(640, 418, "LESS TRAIL", "tb", i=9)
    g.text(640, 440, "quicker, twitchier", "ts", i=9)
    return g


# =====================================================================
# 8.3  Lean balances weight and grip
# =====================================================================
def lean_balance():
    g = Fig("8.3-A", "Lean balances the forces", "Rear view of a bike in a steady corner",
            "Rear view of a leaned motorcycle showing weight, ground push, grip and the resultant force passing through the centre of mass.",
            "In a steady turn the ground pushes up and friction pushes toward the corner's centre. Their resultant lies along the lean "
            "line through the centre of mass, so the bike balances. The lean angle satisfies tan theta = v squared over g r.")
    ph = math.radians(30)
    P = (520, 470)
    d = 240
    CG = (P[0] - d * math.sin(ph), P[1] - d * math.cos(ph))
    # ground + hatch
    g.line(110, P[1], 800, P[1], "k", 0)
    for x in range(120, 800, 22):
        g.line(x, P[1] + 2, x - 12, P[1] + 14, "s", None, "fade")
    # vertical reference
    g.line(P[0], P[1], P[0], 215, "f", None, "fade")
    # bike: tyre, frame line, rider mass
    tc = (P[0] - 48 * math.sin(ph), P[1] - 48 * math.cos(ph))
    g.add('<ellipse class="k draw" data-i="1" cx="%.1f" cy="%.1f" rx="14" ry="50" transform="rotate(-30 %.1f %.1f)"/>' % (tc[0], tc[1], tc[0], tc[1]))
    top = (P[0] - 300 * math.sin(ph), P[1] - 300 * math.cos(ph))
    g.line(P[0] - 96 * math.sin(ph), P[1] - 96 * math.cos(ph), top[0], top[1], "s thick", 1)
    g.circle(CG[0], CG[1], 22, "fill-d k", 2)
    g.dot(CG[0], CG[1], 5, "fill-k", 3)
    g.text(CG[0] - 36, CG[1] - 4, "CENTRE OF", "tmb end", i=3)
    g.text(CG[0] - 36, CG[1] + 14, "MASS", "tmb end", i=3)
    # contact point
    g.dot(P[0], P[1], 7, "fill-k", 2)
    # parallelogram of forces at the contact patch
    N = 130
    F = N * math.tan(ph)
    tipN = (P[0], P[1] - N)
    tipF = (P[0] - F, P[1])
    corner = (P[0] - F, P[1] - N)
    g.line(tipN[0], tipN[1], corner[0], corner[1], "fb", None, "fade")
    g.line(tipF[0], tipF[1], corner[0], corner[1], "fb", None, "fade")
    g.arrow(P[0], P[1], tipN[0], tipN[1] + 2, "b", 15, 4)
    g.arrow(P[0], P[1], tipF[0] + 2, tipF[1], "a", 15, 4)
    g.arrow(P[0], P[1], corner[0] + 5, corner[1] + 8, "k", 16, 6)
    g.text(P[0] + 14, P[1] - N + 10, "GROUND PUSHES UP", "tmb tbl", i=5)
    g.text(P[0] - F - 12, P[1] - 12, "GRIP", "tb ta end", i=5)
    g.text(P[0] - F - 12, P[1] - 36, "friction pulls toward the turn", "ts end", i=5)
    # lean angle
    g.arc(P[0], P[1], 78, -90, -120, "g", 7)
    g.text(P[0] - 22, P[1] - 100, "θ", "fx tg mid", i=7)
    # forces at the centre of mass
    g.arrow(CG[0], CG[1] + 22, CG[0], CG[1] + 22 + 104, "k", 15, 8)
    g.text(CG[0] - 12, CG[1] + 92, "WEIGHT", "tmb end", i=8)
    g.add('<line class="a fade" data-i="9" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke-dasharray="7 6"/>' % (CG[0] + 24, CG[1], CG[0] + 24 + F, CG[1]))
    g.text(CG[0] + 28 + F + 6, CG[1] + 5, "FELT PUSH OUTWARD", "tm ta", i=9)
    # turn centre
    g.arrow(250, 150, 130, 150, "s", 14, 0)
    g.text(40, 134, "CENTRE OF THE TURN", "tm", i=1)
    # formula
    g.text(560, 124, "FASTER OR TIGHTER", "tb", i=10)
    g.text(560, 150, "needs MORE lean", "ts", i=10)
    g.text(560, 204, "tan θ = v² / (g · r)", "fx", i=11)
    g.text(560, 232, "v speed · r corner radius", "tm", i=11)
    g.text(560, 252, "g gravity", "tm", i=11)
    g.text(40, 528, "Ground push and grip add up to one force that points straight through the centre of mass.", "ts", i=12)
    return g


# =====================================================================
# 7.2  Disc size and stopping torque
# =====================================================================
def disc_torque():
    g = Fig("7.2-A", "Disc size and stopping torque", "Same squeeze, same friction, a longer lever arm",
            "Two brake discs of different size with equal pad friction force, showing a longer lever arm produces more stopping torque.",
            "A small and a large brake disc each get the same friction force F from the pad. The pad on the large disc sits twice as far "
            "from the axle, so the stopping torque F times r is twice as large.")
    discs = [("SMALL DISC", 230, 300, 64, 50, "r"), ("LARGE DISC", 650, 300, 114, 100, "R")]
    for k, (name, cx, cy, rr, lever, sym) in enumerate(discs):
        b = k * 3
        g.text(cx, 130, name, "tb mid", i=b)
        g.circle(cx, cy, rr, "k", b)
        g.circle(cx, cy, rr - 12, "s", b)
        g.circle(cx, cy, 16, "k", b + 1)
        for a in range(0, 360, 45):
            g.dot(cx + (rr - 36) * math.cos(math.radians(a)), cy + (rr - 36) * math.sin(math.radians(a)), 4, "fill-s", b + 1)
        # pad at 12 o'clock
        py = cy - lever
        g.rect(cx - 26, py - 11, 52, 22, "tint-a2", 3, anim="fade", i=b + 1)
        g.rect(cx - 26, py - 11, 52, 22, "a", 3, i=b + 1)
        # friction force F (same length on both)
        g.arrow(cx + 40, py - 30, cx - 40, py - 30, "a", 15, b + 2)
        g.text(cx, py - 40, "F", "tb ta mid", i=b + 2)
        # lever arm
        g.line(cx, cy - 2, cx, py + 11, "b", b + 1)
        dx = cx - rr - 26
        g.line(cx - 16, cy, dx - 8, cy, "fb", None, "fade")
        g.line(cx - 26, py, dx - 8, py, "fb", None, "fade")
        g.dim(dx, cy, dx, py, "b", b + 2, 7)
        g.text(dx - 12, (cy + py) / 2 + 10, sym, "fx tbl end", i=b + 2)
        # torque arc around the hub (counter-clockwise, thicker for bigger lever)
        g.arc(cx, cy, 40 if k == 0 else 50, 160, 20, "g", b + 2, head=13)
        # bar chart of resulting torque
        bw = lever * 2.4
        by = 440
        g.rect(cx - 120, by, 240, 20, "s", 2, anim="fade", i=b + 2)
        g.rect(cx - 120, by, bw, 20, "fill-g", 2, anim="fade", i=b + 3)
        g.text(cx - 120, by + 46, "STOPPING TORQUE", "tm", i=b + 3)
        g.text(cx + 120, by + 46, "F × " + sym, "t tg end", i=b + 3)
    g.text(450, 300, "×2", "th ta mid", i=7)
    g.arrow(380, 318, 520, 318, "g", 14, 6)
    g.text(450, 160, "Bigger disc, same pad force:", "ts mid", i=8)
    g.text(450, 184, "the lever does the work.", "ts mid", i=8)
    return g


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("fig-2-2-a.svg", four_stroke), ("fig-4-4-a.svg", rake_trail),
                     ("fig-8-3-a.svg", lean_balance), ("fig-7-2-a.svg", disc_torque)):
        p = fn().save(os.path.join(OUT, name))
        print("wrote", os.path.normpath(p))
