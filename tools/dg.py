"""Knowbase diagram kit.

One design system for every figure: 900x560 sheet, theme-aware colours (CSS variables
with light fallbacks), legible type, and animation hooks (draw / pop / fade) that the
site's reader-aids.js plays when a diagram scrolls into view.

Rules the kit enforces:
  * one concept per figure, labels >= 14px at 900px wide
  * dashed lines never animate (they use .fade), solid strokes use .draw
  * colour has a job: ink = the object, signal(red) = the force/cause, blueprint = geometry/measure,
    brass = the quantity you should remember
"""
import math

W, H = 900, 560

STYLE = """<style>
svg.dg{--c-ink:var(--ink,#22252B);--c-soft:var(--ink-soft,#5A5748);--c-faint:var(--ink-faint,#8C876F);--c-sig:var(--signal,#AE3527);--c-blu:var(--blueprint,#33505E);--c-brs:var(--brass,#6B5A22);--c-paper:var(--paper,#EEE8DA);--c-deep:var(--paper-deep,#E2D9C3);--c-line:var(--line,rgba(34,37,43,.22))}
svg.dg .bgp{fill:var(--c-paper)}
svg.dg .frm{fill:none;stroke:var(--c-ink);stroke-width:1.4}
svg.dg .k,svg.dg .s,svg.dg .a,svg.dg .b,svg.dg .g,svg.dg .f,svg.dg .fk{fill:none;stroke-linecap:round;stroke-linejoin:round}
svg.dg .k{stroke:var(--c-ink);stroke-width:2.8}
svg.dg .s{stroke:var(--c-soft);stroke-width:1.8}
svg.dg .a{stroke:var(--c-sig);stroke-width:3.4}
svg.dg .b{stroke:var(--c-blu);stroke-width:2.6}
svg.dg .g{stroke:var(--c-brs);stroke-width:3}
svg.dg .f{stroke:var(--c-faint);stroke-width:1.5;stroke-dasharray:6 5}
svg.dg .fb{stroke:var(--c-blu);stroke-width:1.5;stroke-dasharray:6 5;fill:none}
svg.dg .thick{stroke-width:7}
svg.dg .fill-d{fill:var(--c-deep)}
svg.dg .fill-k{fill:var(--c-ink)}
svg.dg .fill-a{fill:var(--c-sig)}
svg.dg .fill-b{fill:var(--c-blu)}
svg.dg .fill-g{fill:var(--c-brs)}
svg.dg .fill-s{fill:var(--c-soft)}
svg.dg .tint-a{fill:var(--c-sig);fill-opacity:.16}
svg.dg .tint-a2{fill:var(--c-sig);fill-opacity:.34}
svg.dg .tint-b{fill:var(--c-blu);fill-opacity:.16}
svg.dg .tint-b2{fill:var(--c-blu);fill-opacity:.3}
svg.dg .tint-g{fill:var(--c-brs);fill-opacity:.14}
svg.dg .tint-k{fill:var(--c-ink);fill-opacity:.08}
svg.dg text{paint-order:stroke;stroke:var(--c-paper);stroke-width:5px;stroke-linejoin:round}
svg.dg .th{font:800 34px 'Big Shoulders Display','Arial Narrow',sans-serif;fill:var(--c-ink);text-transform:uppercase;letter-spacing:.01em}
svg.dg .tm{font:500 14px 'JetBrains Mono',Consolas,monospace;fill:var(--c-soft);text-transform:uppercase;letter-spacing:.09em}
svg.dg .tmb{font:700 14px 'JetBrains Mono',Consolas,monospace;fill:var(--c-ink);text-transform:uppercase;letter-spacing:.09em}
svg.dg .t{font:600 21px 'Big Shoulders Text','Arial Narrow',sans-serif;fill:var(--c-ink)}
svg.dg .tb{font:800 25px 'Big Shoulders Text','Arial Narrow',sans-serif;fill:var(--c-ink);text-transform:uppercase;letter-spacing:.02em}
svg.dg .ts{font:italic 400 18px 'Source Serif 4',Georgia,serif;fill:var(--c-soft)}
svg.dg .tsm{font:italic 400 16px 'Source Serif 4',Georgia,serif;fill:var(--c-soft)}
svg.dg .ta{fill:var(--c-sig)}
svg.dg .tbl{fill:var(--c-blu)}
svg.dg .tg{fill:var(--c-brs)}
svg.dg .mid{text-anchor:middle}
svg.dg .end{text-anchor:end}
svg.dg .fx{font:italic 600 30px 'Source Serif 4',Georgia,serif;fill:var(--c-ink)}
</style>"""


def f(n):
    return ("%.1f" % n).rstrip("0").rstrip(".")


class Fig:
    def __init__(self, fig, title, sub, alt, desc):
        self.fig, self.title, self.sub, self.alt, self.desc = fig, title, sub, alt, desc
        self.parts = []
        self.i = 0

    # ---- low level -------------------------------------------------------
    def add(self, s):
        self.parts.append(s)

    def step(self, n=1):
        self.i += n
        return self.i

    def attrs(self, cls, i, anim):
        a = 'class="%s%s"' % (cls, (" " + anim) if anim else "")
        if anim and i is not None:
            a += ' data-i="%d"' % i
        return a

    # ---- shapes ----------------------------------------------------------
    def line(self, x1, y1, x2, y2, cls="k", i=None, anim="draw"):
        self.add('<line %s x1="%s" y1="%s" x2="%s" y2="%s"/>' % (self.attrs(cls, i, anim), f(x1), f(y1), f(x2), f(y2)))

    def path(self, d, cls="k", i=None, anim="draw"):
        self.add('<path %s d="%s"/>' % (self.attrs(cls, i, anim), d))

    def circle(self, cx, cy, r, cls="k", i=None, anim="draw"):
        self.add('<circle %s cx="%s" cy="%s" r="%s"/>' % (self.attrs(cls, i, anim), f(cx), f(cy), f(r)))

    def rect(self, x, y, w, h, cls="k", rx=0, i=None, anim="draw"):
        self.add('<rect %s x="%s" y="%s" width="%s" height="%s" rx="%s"/>' % (self.attrs(cls, i, anim), f(x), f(y), f(w), f(h), f(rx)))

    def poly(self, pts, cls="k", i=None, anim="draw"):
        self.add('<polyline %s points="%s"/>' % (self.attrs(cls, i, anim), " ".join("%s,%s" % (f(x), f(y)) for x, y in pts)))

    def dot(self, x, y, r=6, cls="fill-k", i=None):
        self.add('<circle %s cx="%s" cy="%s" r="%s"/>' % (self.attrs(cls, i, "pop"), f(x), f(y), f(r)))

    def text(self, x, y, s, cls="t", anchor=None, i=None, anim="fade"):
        c = cls + (" " + anchor if anchor else "")
        self.add('<text %s x="%s" y="%s">%s</text>' % (self.attrs(c, i, anim), f(x), f(y), s))

    def arrow(self, x1, y1, x2, y2, cls="a", head=14, i=None, width=None):
        """Line with a solid arrowhead whose tip lands exactly on (x2,y2)."""
        ang = math.atan2(y2 - y1, x2 - x1)
        bx, by = x2 - head * 0.82 * math.cos(ang), y2 - head * 0.82 * math.sin(ang)
        self.line(x1, y1, bx, by, cls, i)
        l = head * 0.52
        p = [(x2, y2),
             (x2 - head * math.cos(ang) + l * math.sin(ang), y2 - head * math.sin(ang) - l * math.cos(ang)),
             (x2 - head * math.cos(ang) - l * math.sin(ang), y2 - head * math.sin(ang) + l * math.cos(ang))]
        fill = {"a": "fill-a", "b": "fill-b", "g": "fill-g", "k": "fill-k", "s": "fill-s"}[cls]
        self.add('<polygon class="%s pop" data-i="%d" points="%s"/>' % (fill, (i or 0) + 1, " ".join("%s,%s" % (f(x), f(y)) for x, y in p)))

    def dim(self, x1, y1, x2, y2, cls="b", i=None, tick=9):
        """Dimension line with end ticks (horizontal or vertical)."""
        self.arrow(x1, y1, x2, y2, cls, 11, i)
        self.arrow(x2, y2, x1, y1, cls, 11, i)
        ang = math.atan2(y2 - y1, x2 - x1)
        nx, ny = -math.sin(ang) * tick, math.cos(ang) * tick
        for (x, y) in ((x1, y1), (x2, y2)):
            self.line(x - nx, y - ny, x + nx, y + ny, cls, i)

    def arc(self, cx, cy, r, a0, a1, cls="b", i=None, head=0):
        """Arc from screen-angle a0 to a1 (degrees, clockwise-positive). Optional arrowhead at a1."""
        x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
        x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
        sweep = 1 if a1 > a0 else 0
        large = 1 if abs(a1 - a0) > 180 else 0
        self.path("M%s %sA%s %s 0 %d %d %s %s" % (f(x0), f(y0), f(r), f(r), large, sweep, f(x1), f(y1)), cls, i)
        if head:
            direction = 1 if a1 > a0 else -1
            tx, ty = -math.sin(math.radians(a1)) * direction, math.cos(math.radians(a1)) * direction
            ex, ey = x1, y1
            sx, sy = ex - tx * 6, ey - ty * 6
            self.arrow(sx, sy, ex + tx * 4, ey + ty * 4, cls, head, i)

    # ---- document --------------------------------------------------------
    def render(self):
        head = (
            '<svg class="dg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" aria-labelledby="t d">\n' % (W, H)
            + '<title id="t">%s</title><desc id="d">%s</desc>\n' % (self.alt, self.desc)
            + STYLE + "\n"
            + '<rect class="bgp" width="%d" height="%d"/>\n' % (W, H)
            + '<rect class="frm" x="10" y="10" width="%d" height="%d"/>\n' % (W - 20, H - 20)
            + '<g class="frm">'
            + '<path d="M10,30V10H30M%d,10H%d V30M%d,%dV%dH%d M30,%dH10V%d"/></g>\n' % (W - 30, W - 10, W - 10, H - 30, H - 10, W - 30, H - 10, H - 30)
        )
        top = (
            '<text class="th" x="40" y="58">%s</text>\n' % self.title
            + '<text class="tm tbl" x="40" y="84">%s</text>\n' % self.sub
            + '<text class="tm end" x="%d" y="%d" style="stroke-width:0">FIG. %s</text>\n' % (W - 32, H - 26, self.fig)
        )
        return head + top + "\n".join(self.parts) + "\n</svg>\n"

    def save(self, path):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(self.render())
        return path
