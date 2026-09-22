"""Animation 0 (the opening scene, before animation 1): the question, and why it is answered badly.

An airport with three runways. One question: which of tomorrow's flights are likely to be delayed,
so the people on them can be told the night before instead of at the gate. It comes down to how
many aircraft are flying that day and what the weather is doing.

Today that question is answered inside the airport by several people at once, and their answers do
not agree. The scene ends on the new data analyst, who is there to turn that into one answer,
worked out the same way every day.

This one stands alone: it does not hand off to animation 1's first frame.

    python anim_0_airport_day.py            # 4K GIF -> output/anim_0_airport_day.gif
    python anim_0_airport_day.py --preview  # fast 1080p check
"""

from common import (INK, MUTED, WHITE, clamp01, ease_in_out_cubic, lerp, main, mix, progress)
from split_common import CAMERA

DURATION = 13.5  # s

ASPHALT = mix(WHITE, INK, 0.76)
TERMINAL = mix(WHITE, INK, 0.22)
GATE = mix(WHITE, INK, 0.34)
TRACK = mix(WHITE, INK, 0.16)
SPREAD = mix(WHITE, INK, 0.45)
CX = CAMERA[0]

TITLE = ("The problem we are here to solve",
         "Telling passengers the night before, instead of at the gate")

AIR_BIG = (2.5, 2.6, 34.1, 10.2)
AIR_SMALL = (2.5, 2.4, 34.1, 5.6)
RUNWAYS = (0.45, 0.645, 0.84)
TRAFFIC = ((0.185, 0.08), (0.125, 0.52), (0.095, 0.81))

QUESTION = "Which of tomorrow's flights are likely to be delayed?"
DEPENDS = "It comes down to two things: how many aircraft are flying that day, and the weather."

LEFT_CX, RIGHT_CX = 10.1, 26.9
TRACK_Y = 11.8
HEAD_Y, SUB_Y, CAP_Y, NOTE_Y = 10.1, 10.75, 12.8, 13.3
DOTS = (5.9, 7.9, 9.4, 12.1, 14.4)

LEFT = ("TODAY", "decided inside the airport, by several people at once",
        "Five people, five different answers", "and no way to say which one to trust")
RIGHT = ("WITH MACHINE LEARNING", "Erika Mustermann, Data Analyst",
         "One answer, for everyone", "worked out the same way every day")

FOOTER = "The goal is to standardize decision making for this process"


class Scene:
    """Free-form drawing on the shared renderer (same element lists as the other animations)."""

    def __init__(self):
        self.tiles, self.boxes, self.lines, self.texts, self.pills = [], [], [], [], []

    def text(self, x, y, s, size, col, a, bold=False, anchor="mm"):
        if a > 0.004:
            self.texts.append((x, y, s, size, col, a, bold, anchor))

    def tile(self, col, rect, a, r=0.06):
        if a > 0.004:
            self.tiles.append((col, *rect, r, a))

    def dot(self, x, y, r, col, a):
        self.tile(col, (x - r, y - r, x + r, y + r), a, r)

    def pill(self, x, y, s, size, a, bg=None, fg=None):
        if a > 0.004:
            self.pills.append((x, y, s, size, a) + ((bg, fg) if bg else ()))

    def line(self, x0, y0, x1, y1, a, w=0.06, dashed=False, color=None):
        if a > 0.004:
            self.lines.append((x0, y0, x1, y1, w, a, dashed) + ((color,) if color else ()))

    def state(self, camera=CAMERA):
        return dict(camera=camera, tiles=self.tiles, boxes=self.boxes, lines=self.lines,
                    texts=self.texts, pills=self.pills)


def plane(sc, x, y, s, a, col=INK):
    """An aircraft seen from above, nose pointing right: fuselage, swept wings, tailplane."""
    sc.tile(col, (x - 1.15 * s, y - 0.19 * s, x + 1.25 * s, y + 0.19 * s), a, 0.19 * s)
    for d in (-1, 1):
        sc.line(x + 0.34 * s, y, x - 0.48 * s, y + d * 1.02 * s, a, 0.21 * s, False, col)
        sc.line(x - 0.78 * s, y, x - 1.10 * s, y + d * 0.46 * s, a, 0.15 * s, False, col)


def airport(sc, rect, a, t):
    x0, y0, x1, y1 = rect
    h = y1 - y0
    sc.tile(TERMINAL, (x0 + 1.4, y0 + 0.03 * h, x1 - 1.4, y0 + 0.15 * h), a, 0.2)
    for k in range(20):
        gx = lerp(x0 + 2.4, x1 - 2.4, k / 19)
        sc.tile(GATE, (gx - 0.14, y0 + 0.15 * h, gx + 0.14, y0 + 0.23 * h), a, 0.07)
    s = 0.075 * h
    for k, ry in enumerate(RUNWAYS):
        ry0, ry1 = y0 + ry * h, y0 + (ry + 0.07) * h
        sc.tile(ASPHALT, (x0 + 3.3, ry0, x1 - 0.5, ry1), a, 0.08)
        sc.line(x0 + 4.0, (ry0 + ry1) / 2, x1 - 1.2, (ry0 + ry1) / 2, a * 0.7, 0.045, True, WHITE)
        sc.text(x0 + 3.05, (ry0 + ry1) / 2, f"RUNWAY {k + 1}", 0.28, MUTED, a, True, "rm")
        speed, off = TRAFFIC[k]
        u = (t * speed + off) % 1.0
        plane(sc, lerp(x0 + 3.8, x1 - 0.9, u), (ry0 + ry1) / 2, s,
              a * clamp01(min(u, 1 - u) / 0.07))


def side(sc, cx, words, a, caption):
    head, sub, cap, note = words
    sc.text(cx, HEAD_Y, head, 0.46, INK, a, True)
    sc.text(cx, SUB_Y, sub, 0.29, MUTED, a)
    sc.line(cx - 5.1, TRACK_Y, cx + 5.1, TRACK_Y, a * 0.9, 0.05, False, TRACK)
    sc.text(cx, CAP_Y, cap, 0.32, INK, caption, True)
    sc.text(cx, NOTE_Y + 0.14, note, 0.275, MUTED, caption)


def timeline(t):
    sc = Scene()
    shrink = progress(t, 3.0, 1.4, ease_in_out_cubic)
    rect = tuple(lerp(p, q, shrink) for p, q in zip(AIR_BIG, AIR_SMALL))

    sc.text(CX, 0.2, TITLE[0], 0.62, INK, 1.0, True)
    sc.text(CX, 1.35, TITLE[1], 0.38, MUTED, 1.0)
    airport(sc, rect, progress(t, 0.3, 0.8), t)

    sc.text(CX, 6.9, QUESTION, 0.72, INK, progress(t, 3.9, 0.6), True)
    sc.text(CX, 7.95, DEPENDS, 0.36, MUTED, progress(t, 4.9, 0.6))

    side(sc, LEFT_CX, LEFT, progress(t, 6.2, 0.5), progress(t, 8.8, 0.5))
    for k, x in enumerate(DOTS):
        sc.dot(x, TRACK_Y, 0.21, SPREAD, progress(t, 6.8 + k * 0.35, 0.4))

    arrow = progress(t, 9.6, 0.5)
    sc.line(17.7, TRACK_Y, 19.3, TRACK_Y, arrow, 0.06, False, MUTED)
    sc.line(18.95, TRACK_Y - 0.22, 19.3, TRACK_Y, arrow, 0.06, False, MUTED)
    sc.line(18.95, TRACK_Y + 0.22, 19.3, TRACK_Y, arrow, 0.06, False, MUTED)

    side(sc, RIGHT_CX, RIGHT, progress(t, 10.0, 0.5), progress(t, 11.4, 0.5))
    sc.dot(RIGHT_CX, TRACK_Y, 0.32, INK, progress(t, 10.8, 0.5))

    sc.pill(CX, 14.9, FOOTER, 0.36, progress(t, 12.2, 0.5))
    return sc.state()


if __name__ == "__main__":
    main("anim_0_airport_day", DURATION, timeline)
