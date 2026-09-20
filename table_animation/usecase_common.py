"""Shared scene for the use-case animations (38-39), 1080p only.

A self-contained slide about the dataset the workshop works on; it does not continue from the
delay-prediction story, but keeps the same drawing style, fonts and camera as the rest of the deck.

    38  use case         the headline facts about the dataset, as five cards with icons
    39  dataset sample   the cards squeeze into a strip at the top and a sample of the table
                         builds below it, column by column and row by row

Animation 39 starts on animation 38's last frame, as everywhere else in the deck. All figures are
the real shape of the dataset; the eight sample rows are illustrative.
"""

import math
import random

from common import (HEADER_BG, INK, MUTED, RED_TINT, WHITE, clamp01, ease_in_out_cubic, fit_scale,
                    lerp, mix, progress)
from map_common import SHARE_RED

CAM_USE = (50.0, 29.0, fit_scale(104.0, 58.5, 0.02))

TITLE = "The use case"
SUB_META = "Airbus in-service fleet: how much every aircraft flies, month by month"
SUB_DATA = "What the data looks like: one row is one aircraft in one month"
SUB_GOAL = "Eleven years of monthly history per aircraft, and one year to predict"

ROW_A = (248, 249, 251)
ROW_B = (240, 242, 245)
HEAD_BG = (226, 230, 236)


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

    def pill(self, x, y, s, size, a, bg=None, fg=None):
        if a > 0.004:
            self.pills.append((x, y, s, size, a) + ((bg, fg) if bg else ()))

    def box(self, rect, a, r=0.35, w=0.07, color=None):
        if a > 0.004:
            self.boxes.append((*rect, r, a, w) + ((color,) if color else ()))

    def line(self, x0, y0, x1, y1, a, w=0.06, dashed=False, color=None):
        if a > 0.004:
            self.lines.append((x0, y0, x1, y1, w, a, dashed) + ((color,) if color else ()))

    def state(self, camera=CAM_USE):
        return dict(camera=camera, tiles=self.tiles, boxes=self.boxes, lines=self.lines,
                    texts=self.texts, pills=self.pills)


# ---------------------------------------------------------------- icons

def _ellipse(sc, cx, cy, rx, ry, a, w, col=INK, n=32):
    pts = [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n))
           for k in range(n + 1)]
    for p, q in zip(pts, pts[1:]):
        sc.line(*p, *q, a, w, color=col)


def _arc(sc, cx, cy, r, deg0, deg1, a, w, col=INK, n=18):
    pts = [(cx + r * math.cos(math.radians(lerp(deg0, deg1, k / n))),
            cy + r * math.sin(math.radians(lerp(deg0, deg1, k / n)))) for k in range(n + 1)]
    for p, q in zip(pts, pts[1:]):
        sc.line(*p, *q, a, w, color=col)
    return pts[-2], pts[-1]


def _arrow_head(sc, p, q, a, w, size, col=INK):
    d = max(1e-6, math.hypot(q[0] - p[0], q[1] - p[1]))
    ux, uy = (q[0] - p[0]) / d, (q[1] - p[1]) / d
    for side in (1, -1):
        sc.line(q[0], q[1], q[0] - size * ux + side * 0.7 * size * uy,
                q[1] - size * uy - side * 0.7 * size * ux, a, w, color=col)


def draw_icon(sc, kind, cx, cy, s, a):
    """One line-art icon, drawn around (cx, cy) at scale s."""
    w = 0.19 * s
    if kind == "plane":
        sc.line(cx - 1.2 * s, cy, cx + 1.25 * s, cy, a, w)
        for side in (-1, 1):
            sc.line(cx + 0.1 * s, cy, cx - 0.6 * s, cy + side * 0.95 * s, a, w)
            sc.line(cx - 0.95 * s, cy, cx - 1.25 * s, cy + side * 0.5 * s, a, w)
    elif kind == "calendar":
        sc.box((cx - 1.1 * s, cy - 0.9 * s, cx + 1.1 * s, cy + 1.05 * s), a, 0.22 * s, w)
        sc.tile(INK, (cx - 1.1 * s, cy - 0.9 * s, cx + 1.1 * s, cy - 0.42 * s), a, 0.22 * s)
        for side in (-1, 1):
            sc.line(cx + side * 0.55 * s, cy - 1.25 * s, cx + side * 0.55 * s, cy - 0.75 * s, a, w)
        for r in range(2):
            for c in range(3):
                x, y = cx + (c - 1) * 0.62 * s, cy + (0.02 + r * 0.55) * s
                sc.tile(MUTED, (x - 0.16 * s, y - 0.16 * s, x + 0.16 * s, y + 0.16 * s), a,
                        0.08 * s)
    elif kind == "rows":
        for j in range(4):
            y = cy - 1.05 * s + j * 0.62 * s
            sc.tile(INK if j == 0 else MUTED,
                    (cx - 1.15 * s, y, cx + 1.15 * s, y + 0.38 * s), a if j == 0 else a * 0.55,
                    0.15 * s)
    elif kind == "globe":
        _ellipse(sc, cx, cy, 1.05 * s, 1.05 * s, a, w)
        _ellipse(sc, cx, cy, 0.42 * s, 1.05 * s, a * 0.8, w * 0.8, MUTED)
        sc.line(cx - 1.05 * s, cy, cx + 1.05 * s, cy, a * 0.8, w * 0.8, color=MUTED)
        sc.line(cx - 0.9 * s, cy - 0.5 * s, cx + 0.9 * s, cy - 0.5 * s, a * 0.8, w * 0.8,
                color=MUTED)
        sc.line(cx - 0.9 * s, cy + 0.5 * s, cx + 0.9 * s, cy + 0.5 * s, a * 0.8, w * 0.8,
                color=MUTED)
    elif kind == "gauge":  # a cycle arrow around a clock: cycles and hours, month after month
        p, q = _arc(sc, cx, cy, 1.15 * s, -40, 250, a, w)
        _arrow_head(sc, p, q, a, w, 0.42 * s)
        _ellipse(sc, cx, cy, 0.62 * s, 0.62 * s, a * 0.8, w * 0.8, MUTED)
        sc.line(cx, cy, cx, cy - 0.45 * s, a, w * 0.9, color=INK)
        sc.line(cx, cy, cx + 0.34 * s, cy, a, w * 0.9, color=INK)


# ---------------------------------------------------------------- the five facts

STATS = [  # (icon, big text, big size, label, short text for the strip)
    ("plane", lambda p: f"{round(14000 * p):,}", 2.2, "unique aircraft  ·  MSN",
     "14,000 aircraft"),
    ("calendar", lambda p: "2014 - 2024", 2.2, "Jan 2014 to Dec 2024  ·  132 months",
     "2014 - 2024"),
    ("rows", lambda p: f"{1.2 * p:.1f} M+", 2.2, "rows of monthly data", "1.2 M+ rows"),
    ("globe", lambda p: f"{round(860 * p)}", 2.2, "airline operators", "860 operators"),
    ("gauge", lambda p: "Flight cycles   ·   Flight hours", 1.7,
     "recorded for every aircraft, in every month", "cycles + hours"),
]

CARD_Y0, CARD_H, CARD_W, CARD_PITCH = 13.6, 15.4, 22.7, 25.1
WIDE_RECT = (1.0, 32.2, 99.0, 44.2)
STRIP_Y0, STRIP_H, STRIP_W, STRIP_PITCH = 7.4, 4.3, 18.8, 19.8
META_NOTE = "Every row: one aircraft, one month"
META_NOTE_Y = 50.5


def card_rect(k, squeeze):
    big = WIDE_RECT if k == 4 else (1.0 + k * CARD_PITCH, CARD_Y0, 1.0 + k * CARD_PITCH + CARD_W,
                                    CARD_Y0 + CARD_H)
    strip = (1.0 + k * STRIP_PITCH, STRIP_Y0, 1.0 + k * STRIP_PITCH + STRIP_W, STRIP_Y0 + STRIP_H)
    return tuple(lerp(u, v, squeeze) for u, v in zip(big, strip))


def draw_title(sc, a=1.0, meta_a=1.0, data_a=0.0, goal_a=0.0):
    sc.text(50.0, 2.0, TITLE, 2.2, INK, a, True)
    sc.text(50.0, 4.6, SUB_META, 1.15, MUTED, a * meta_a)
    sc.text(50.0, 4.6, SUB_DATA, 1.15, MUTED, a * data_a)
    sc.text(50.0, 4.6, SUB_GOAL, 1.15, MUTED, a * goal_a)


def piecewise(knots, t):
    """Linear interpolation through (t, value) knots, clamped at both ends."""
    if t <= knots[0][0]:
        return knots[0][1]
    for (t0, v0), (t1, v1) in zip(knots, knots[1:]):
        if t <= t1:
            return lerp(v0, v1, clamp01((t - t0) / (t1 - t0)))
    return knots[-1][1]


def draw_stats(sc, appear=(1.0,) * 5, counts=(1.0,) * 5, rise=(0.0,) * 5, squeeze=0.0, a=1.0):
    """The five fact cards. squeeze 0 = full cards, 1 = a compact strip under the title."""
    big_a = 1 - clamp01(squeeze * 1.8)
    short_a = clamp01((squeeze - 0.4) / 0.4)
    for k, (icon, big, big_size, label, short) in enumerate(STATS):
        al = a * appear[k]
        if al <= 0.004:
            continue
        x0, y0, x1, y1 = card_rect(k, squeeze)
        dy = rise[k]
        x0, y0, x1, y1 = x0, y0 + dy, x1, y1 + dy
        cx = (x0 + x1) / 2
        sc.tile(HEADER_BG, (x0, y0, x1, y1), al, lerp(0.8, 0.5, squeeze))
        wide = k == 4
        draw_icon(sc, icon, cx, y0 + (3.6 if wide else 4.6), 2.3 if wide else 2.5, al * big_a)
        sc.text(cx, lerp(y0 + (7.6 if wide else 9.3), (y0 + y1) / 2, squeeze), big(counts[k]),
                lerp(big_size, 1.0, squeeze), INK, al * big_a, True)
        sc.text(cx, y0 + (10.2 if wide else 12.6), label, 0.8, MUTED, al * big_a)
        sc.text(cx, (y0 + y1) / 2, short, 1.0, INK, al * short_a, True)


# ---------------------------------------------------------------- the dataset sample

DS_COLS = [  # (name, what it is, width, alignment)
    ("manufacturer_aircraft_id", "the aircraft (MSN)", 13.0, "l"),
    ("ds", "the month", 11.0, "l"),
    ("flight_cycles", "take-offs that month", 10.0, "r"),
    ("flight_hours", "hours flown that month", 10.0, "r"),
    ("aircraft_program", "family", 12.0, "l"),
    ("aircraft_series", "exact variant", 12.0, "l"),
    ("operator_code_icao", "airline code", 11.0, "l"),
    ("operator_name", "the airline", 19.0, "l"),
]
DS_ROWS = [
    ("10042", "2019-01-01", "118", "271.4", "A320", "A320-200", "DLH", "Lufthansa"),
    ("10042", "2019-02-01", "104", "243.9", "A320", "A320-200", "DLH", "Lufthansa"),
    ("10042", "2019-03-01", "121", "286.2", "A320", "A320-200", "DLH", "Lufthansa"),
    ("10583", "2019-01-01", "96", "402.7", "A350", "A350-900", "AFR", "Air France"),
    ("10583", "2019-02-01", "88", "371.5", "A350", "A350-900", "AFR", "Air France"),
    ("11726", "2021-07-01", "142", "214.8", "A220", "A220-300", "SWR", "Swiss"),
    ("12490", "2023-11-01", "63", "508.1", "A350", "A350-1000", "QTR", "Qatar Airways"),
    ("13317", "2024-06-01", "155", "289.6", "A320", "A321-200N", "WZZ", "Wizz Air"),
]
TABLE_X0, HEAD_Y0, HEAD_H, ROW_H = 1.0, 15.4, 3.6, 3.1
MEASURES = (2, 3)  # flight_cycles and flight_hours
SAMPLE_LABEL = "DATASET SAMPLE  ·  8 of more than 1.2 million rows"
NOTE_Y = 50.0
NOTES = {
    "rows": "The same aircraft comes back every month: 10042 in January, February, March",
    "measures": "The two numbers we actually measure: how often and how long it flew",
}
FINAL_NOTE = "1.2 million rows like these: 14,000 aircraft x 132 months"


def col_x(j):
    return TABLE_X0 + sum(w for _, _, w, _ in DS_COLS[:j])


def row_y(k):
    return HEAD_Y0 + HEAD_H + k * ROW_H


def _cell(sc, j, y, text, size, col, a, bold=False):
    x0, w, align = col_x(j), DS_COLS[j][2], DS_COLS[j][3]
    if align == "l":
        sc.text(x0 + 0.7, y, text, size, col, a, bold, "lm")
    else:
        sc.text(x0 + w - 0.7, y, text, size, col, a, bold, "rm")


def draw_table(sc, label_a=1.0, head_a=(1.0,) * 8, rows_a=(1.0,) * 9, a=1.0):
    """Header (per column) and rows (8 sample rows plus a continuation row)."""
    sc.text(TABLE_X0, 13.2, SAMPLE_LABEL, 1.0, INK, a * label_a, True, "lm")
    for j, (name, what, w, _) in enumerate(DS_COLS):
        ha = a * head_a[j]
        x0 = col_x(j)
        sc.tile(HEAD_BG, (x0 + 0.1, HEAD_Y0, x0 + w - 0.1, HEAD_Y0 + HEAD_H), ha, 0.3)
        _cell(sc, j, HEAD_Y0 + 1.25, name, 0.72, INK, ha, True)
        _cell(sc, j, HEAD_Y0 + 2.55, what, 0.62, MUTED, ha)
    for k, row in enumerate(DS_ROWS):
        ra = a * rows_a[k]
        y0 = row_y(k)
        sc.tile(ROW_A if k % 2 == 0 else ROW_B, (TABLE_X0 + 0.1, y0, 99.0 - 0.1, y0 + ROW_H - 0.1),
                ra, 0.3)
        for j, value in enumerate(row):
            _cell(sc, j, y0 + ROW_H / 2 - 0.05, value, 0.85, INK, ra, j in MEASURES)
    last = a * rows_a[8]
    y0 = row_y(len(DS_ROWS))
    sc.tile(ROW_A, (TABLE_X0 + 0.1, y0, 99.0 - 0.1, y0 + 2.1), last, 0.3)
    for j in range(len(DS_COLS)):
        _cell(sc, j, y0 + 1.0, "...", 0.85, MUTED, last)


def highlight_rect(kind):
    if kind == "rows":
        return (TABLE_X0 - 0.1, row_y(0) - 0.2, col_x(2) - 0.1, row_y(3) - 0.2)
    x0, x1 = col_x(MEASURES[0]), col_x(MEASURES[1]) + DS_COLS[MEASURES[1]][2]
    return (x0 - 0.1, HEAD_Y0 - 0.3, x1 - 0.1, row_y(len(DS_ROWS)) + 2.3)


def draw_highlight(sc, kind, a):
    if a > 0.004:
        sc.box(highlight_rect(kind), a, 0.5, 0.22, SHARE_RED)


def squeeze_at(t, start, dur=1.5):
    return progress(t, start, dur, ease_in_out_cubic)


# ---------------------------------------------------------------- one aircraft, 2014 - 2025

MSN = "10042"
MSN_LABEL = "MSN 10042  ·  A320-200  ·  Lufthansa"
YEAR0, N_HIST, N_ALL = 2014, 132, 144  # 2014-01 .. 2024-12 observed, 2025 to predict
MAINT = {40: 0.30, 92: 0.25, 116: 0.34}  # months the aircraft barely flew


def _month_factor(m):
    """Seasonality, slow growth, the 2020 collapse and the odd very quiet month."""
    season = 1 + 0.13 * math.sin(2 * math.pi * (m % 12 - 2.5) / 12)
    growth = 1 + 0.015 * (m / 12)
    covid = 1.0
    if 74 <= m < 100:  # 2020-03 onwards, back to normal by mid 2022
        covid = [0.35, 0.05, 0.06, 0.14, 0.24, 0.31, 0.36, 0.33, 0.28, 0.30][m - 74] \
            if m < 84 else lerp(0.34, 1.0, (m - 84) / 16)
    return season * growth * covid * MAINT.get(m, 1.0)


def _msn_series(seed=3):
    rng = random.Random(seed)
    cycles, hours = [], []
    for m in range(N_HIST):
        c = 118 * _month_factor(m) + rng.gauss(0, 3.5)
        cycles.append(max(0.0, round(c)))
        hours.append(max(0.0, round(cycles[-1] * (2.08 + rng.gauss(0, 0.05)), 1)))
    return cycles, hours


CYCLES, HOURS = _msn_series()
SERIES = [  # (rect of the plot area, title, unit, values, y max, gridlines)
    ((10.0, 16.6, 96.0, 29.4), "flight_cycles", "take-offs per month", CYCLES, 200, (0, 100, 200)),
    ((10.0, 35.0, 96.0, 47.8), "flight_hours", "hours flown per month", HOURS, 400, (0, 200, 400)),
]
PREDICT_NOTE = "2025 is missing: that is what we have to predict"
GOAL_NOTE = "The goal: predict flight cycles and flight hours for every month of 2025"
GOAL_Y, COUNT_Y, FLEET_NOTE_Y = 51.5, 51.3, 55.0


def _px(rect, m):
    return lerp(rect[0], rect[2], m / (N_ALL - 1))


def _py(rect, v, ymax):
    return lerp(rect[3], rect[1], v / ymax)


def draw_series(sc, k, a, reveal=1.0, band=0.0, marks=0.0, q=None, pred=0.0, act=0.0, err=0.0,
                zoom=0.0):
    """One of the two charts. reveal sweeps the monthly line in, band shades 2025, zoom 0..1 pulls
    the time axis in from eleven years to the last two."""
    rect, name, unit, values, ymax, grid = SERIES[k]
    x0, y0, x1, y1 = rect
    w0 = lerp(0.0, 120.0, zoom)
    span = (N_ALL - 1) - w0

    def px(m):
        return lerp(x0, x1, (m - w0) / span)

    def py(v):
        return lerp(y1, y0, v / ymax)

    def vis(x):
        return x0 - 0.25 <= x <= x1 + 0.25

    sc.text(x0, y0 - 2.4, name, 1.15, INK, a, True, "lm")
    sc.text(x0, y0 - 1.0, unit, 0.8, MUTED, a, False, "lm")
    sc.text(x1, y0 - 2.4, MSN_LABEL, 0.9, MUTED, a, True, "rm")
    sc.text(x0 + 24.0, y0 - 1.0, "dashed red: predicted", 0.8, SHARE_RED,
            a * clamp01(pred * 2), True, "lm")
    sc.text(x0 + 42.0, y0 - 1.0, "black: what really happened", 0.8, INK,
            a * clamp01(act * 2), True, "lm")
    if band > 0:  # the year to predict
        sc.tile(RED_TINT, (px(N_HIST - 0.5), y0, x1 + 0.2, y1), a * band, 0.2)
        sc.line(px(N_HIST - 0.5), y0 - 0.3, px(N_HIST - 0.5), y1, a * band, 0.09, True, SHARE_RED)
        sc.text(px(N_HIST + 5.5), y0 + 0.9, "2025", 1.0, SHARE_RED, a * band, True)
    for v in grid:
        sc.line(x0, py(v), x1, py(v), a * (1.0 if v == 0 else 0.35), 0.06)
        sc.text(x0 - 0.5, py(v), str(v), 0.75, MUTED, a, False, "rm")
    for year in range(YEAR0, YEAR0 + 12):
        m = (year - YEAR0) * 12
        if vis(px(m + 5.5)):
            sc.text(px(m + 5.5), y1 + 1.0, str(year), 0.75,
                    SHARE_RED if year == 2025 else MUTED,
                    a * (band if year == 2025 else 1.0))
        if vis(px(m - 0.5)):
            sc.line(px(m - 0.5), y1, px(m - 0.5), y1 + 0.3, a * 0.6, 0.05)
    shown = reveal * (N_HIST - 1)
    for m in range(N_HIST - 1):
        if m > shown or not vis(px(m)):
            continue
        f = clamp01(shown - m)
        xa, ya, xb, yb = px(m), py(values[m]), px(m + 1), py(values[m + 1])
        sc.line(xa, ya, lerp(xa, xb, f), lerp(ya, yb, f), a, 0.13, color=INK)
        sc.tile(INK, (xa - 0.14, ya - 0.14, xa + 0.14, ya + 0.14), a, 0.14)
    if reveal >= 1:
        xa, ya = px(N_HIST - 1), py(values[-1])
        sc.tile(INK, (xa - 0.14, ya - 0.14, xa + 0.14, ya + 0.14), a, 0.14)
    if marks > 0:  # the twelve months we owe a number for: one empty slot each
        y = py(values[-1])
        slots = a * (1 - clamp01(pred * 1.5))
        for j in range(12):
            f = clamp01(marks * 12 - j)
            sc.box((px(N_HIST + j) - 0.22, y - 0.22, px(N_HIST + j) + 0.22, y + 0.22),
                   slots * f, 0.22, 0.09, SHARE_RED)
        qa = marks if q is None else q
        sc.text(px(N_HIST + 5.5), y - 2.6, "?", 2.0, SHARE_RED, a * clamp01(qa * 2 - 1), True)
    start = (px(N_HIST - 1), py(values[-1]))
    for series, amount, col, dash in ((PRED[k], pred, SHARE_RED, True), (ACT[k], act, INK, False)):
        if amount <= 0:
            continue
        pts = [start] + [(px(N_HIST + j), py(series[j])) for j in range(12)]
        shown = amount * 12
        for j in range(12):
            if j > shown:
                break
            f = clamp01(shown - j)
            (xa, ya), (xb, yb) = pts[j], pts[j + 1]
            sc.line(xa, ya, lerp(xa, xb, f), lerp(ya, yb, f), a, 0.13, dash, col)
            if f >= 1:
                sc.tile(col, (xb - 0.2, yb - 0.2, xb + 0.2, yb + 0.2), a, 0.2)
    if err > 0:  # the gap between the two, month by month
        for j in range(12):
            f = clamp01(err * 12 - j)
            x, yp, ya = px(N_HIST + j), py(PRED[k][j]), py(ACT[k][j])
            sc.line(x, yp, x, lerp(yp, ya, f), a, 0.16, color=SHARE_RED)
            sc.text(x, min(yp, ya) - 0.9, str(abs(ACT[k][j] - PRED[k][j])) if k == 0 else "",
                    0.7, SHARE_RED, a * f * zoom, True)


# ---------------------------------------------------------------- 2025: prediction and truth

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _future(seed=5):
    """What the model predicts for 2025 and what the aircraft really flew."""
    rng = random.Random(seed)
    pc, ac, ph, ah = [], [], [], []
    for j in range(12):
        base = 118 * _month_factor(N_HIST + j)
        pc.append(round(base))
        ac.append(max(0, round(base * (1 + rng.gauss(0, 0.05)) + rng.gauss(0, 2.0))))
        ph.append(round(pc[-1] * 2.08, 1))
        ah.append(round(ac[-1] * (2.08 + rng.gauss(0, 0.05)), 1))
    return [pc, ph], [ac, ah]


PRED, ACT = _future()
ERR = [abs(a - p) for p, a in zip(PRED[0], ACT[0])]
SUM_ERR, SUM_ACT = sum(ERR), sum(ACT[0])
MAE = SUM_ERR / 12
WAPE = SUM_ERR / SUM_ACT
FLEET_WAPE = 0.068  # illustrative: the same sum over every aircraft and every month
PRED_NOTE = "The model's answer for 2025, one number per month"
ACT_NOTE = "And this is what the aircraft really flew"
ERR_NOTE = "The gap between the two is the error we are judged on"

# ---- mean absolute error

MAE_TITLE = "MEAN ABSOLUTE ERROR  ·  flight_cycles, 2025"
MAE_BOTH = "flight_hours is scored exactly the same way, and counts for half the score"
MAE_X0, MAE_X1, MAE_BASE, MAE_SCALE = 14.0, 92.0, 44.6, 0.62
MAE_FORMULA = (f"MAE  =  (sum of the 12 monthly errors) / 12  =  {SUM_ERR} / 12  "
               f"=  {MAE:.1f} flight cycles a month")
MAE_NOTE = "One number for how far off we are - but is 6 cycles a lot, or a little?"


def draw_mae(sc, a, bars=0.0, formula=0.0):
    sc.text(MAE_X0 - 4.0, 32.4, MAE_TITLE, 1.15, INK, a, True, "lm")
    sc.text(MAE_X1 + 4.0, 32.4, MAE_BOTH, 0.85, MUTED, a, False, "rm")
    sc.line(MAE_X0 - 4.0, MAE_BASE, MAE_X1 + 4.0, MAE_BASE, a, 0.07)
    for j in range(12):
        f = clamp01(bars * 12 - j)
        if f <= 0:
            continue
        x = lerp(MAE_X0, MAE_X1, j / 11)
        h = ERR[j] * MAE_SCALE * f
        sc.tile(SHARE_RED, (x - 1.5, MAE_BASE - h, x + 1.5, MAE_BASE), a, 0.2)
        sc.text(x, MAE_BASE - h - 0.9, f"{ERR[j]}", 0.8, SHARE_RED, a * f, True)
        sc.text(x, MAE_BASE + 1.0, MONTHS[j], 0.75, MUTED, a * f)
        sc.text(x, MAE_BASE + 2.2, f"|{ACT[0][j]} \u2212 {PRED[0][j]}|", 0.6, MUTED, a * f)
    sc.text(53.0, 48.4, MAE_FORMULA, 1.15, INK, a * formula, True)


# ---- every other aircraft

MINI_N, MINI_COLS = 12, 4
MINI_X0, MINI_X1, MINI_Y0, MINI_Y1, MINI_GAP = 8.0, 96.0, 16.2, 47.0, 2.5
MINI_W = (MINI_X1 - MINI_X0 - (MINI_COLS - 1) * MINI_GAP) / MINI_COLS
MINI_H = (MINI_Y1 - MINI_Y0 - 2 * MINI_GAP) / 3
MINI_NOTE = "Every aircraft gets its own 2025, and every one of them is scored"
MINI_MORE = "... and 13,988 more"
MINI_HEAD = "TWELVE OF THE AIRCRAFT  ·  2024, then 2025: predicted against actual"


def _mini_fleet(n=MINI_N, seed=21):
    """24 months (2024 and 2025) per aircraft: history, prediction, truth."""
    rng = random.Random(seed)
    out = []
    for k in range(n):
        msn = rng.randint(10000, 13999)
        prog = rng.choice(["A320", "A321", "A220", "A330", "A350"])
        level = rng.uniform(0.55, 1.35)
        phase = rng.uniform(-1.0, 1.0)
        bias = rng.gauss(0, 0.06)
        hist, pred, act = [], [], []
        for j in range(24):
            m = N_HIST - 12 + j
            season = 1 + 0.13 * math.sin(2 * math.pi * ((m % 12) - 2.5 + phase) / 12)
            base = 118 * level * season * (1 + 0.015 * (m / 12))
            if j < 12:
                hist.append(max(0.0, base + rng.gauss(0, 4)))
            else:
                pred.append(max(0.0, base))
                act.append(max(0.0, base * (1 + bias + rng.gauss(0, 0.05))))
        out.append((f"MSN {msn}  ·  {prog}", hist, pred, act))
    return out


MINIS = [(MSN_LABEL.split("  ·  ")[0] + "  ·  A320", CYCLES[-12:], PRED[0], [float(v) for v in
          ACT[0]])] + _mini_fleet(MINI_N - 1)


def mini_rect(k):
    col, row = k % MINI_COLS, k // MINI_COLS
    x0 = MINI_X0 + col * (MINI_W + MINI_GAP)
    y0 = MINI_Y0 + row * (MINI_H + MINI_GAP)
    return (x0, y0, x0 + MINI_W, y0 + MINI_H)


def draw_minis(sc, a, appear=None, more_a=0.0, focus=0.0):
    """The same story for twelve aircraft at once. focus dims all but the first cell."""
    appear = [1.0] * MINI_N if appear is None else appear
    sc.text(MINI_X0, 14.0, MINI_HEAD, 1.0, INK, a * appear[0], True, "lm")
    for k, (label, hist, pred, act) in enumerate(MINIS):
        ca = a * appear[k] * (1 - 0.72 * focus * (k > 0))
        if ca <= 0.004:
            continue
        x0, y0, x1, y1 = mini_rect(k)
        sc.tile(HEADER_BG, (x0, y0, x1, y1), ca * 0.55, 0.4)
        sc.text(x0 + 1.0, y0 + 1.2, label, 0.62, INK, ca, True, "lm")
        px0, px1 = x0 + 1.0, x1 - 1.0
        py0, py1 = y0 + 2.2, y1 - 1.0
        ymax = max(max(hist), max(pred), max(act)) * 1.2
        px = lambda i: lerp(px0, px1, i / 23)
        py = lambda v: lerp(py1, py0, v / ymax)
        sc.tile(RED_TINT, (px(11.5), py0 - 0.3, px1 + 0.2, py1), ca, 0.2)
        sc.line(px0, py1, px1, py1, ca * 0.7, 0.05)
        for i in range(11):
            sc.line(px(i), py(hist[i]), px(i + 1), py(hist[i + 1]), ca, 0.1, color=INK)
        sc.line(px(11), py(hist[11]), px(12), py(pred[0]), ca, 0.1, True, SHARE_RED)
        sc.line(px(11), py(hist[11]), px(12), py(act[0]), ca, 0.1, color=INK)
        for i in range(11):
            sc.line(px(12 + i), py(pred[i]), px(13 + i), py(pred[i + 1]), ca, 0.1, True, SHARE_RED)
            sc.line(px(12 + i), py(act[i]), px(13 + i), py(act[i + 1]), ca, 0.1, color=INK)
    sc.text(50.0, MINI_Y1 + 1.8, MINI_MORE, 1.0, MUTED, a * more_a, True)


# ---- WAPE, exactly as the evaluation script computes it

CARD = (10.0, 13.4, 90.0, 47.6)
JAN = [(1412600, 0.284, "flight_cycles"), (3051400, 0.316, "flight_hours")]
JAN_ROWS = [(name, round(act * r), act, round(act * r) / act) for act, r, name in JAN]
JAN_SCORE = sum(r[3] for r in JAN_ROWS) / 2
MONTH_WAPES = [JAN_SCORE, 0.284, 0.291, 0.305, 0.312, 0.298, 0.287, 0.294, 0.309, 0.318,
               0.301, 0.295]
FINAL_WAPE = sum(MONTH_WAPES) / 12

WAPE_TITLE = "WAPE  =  sum of the errors  /  sum of the actual values"
WAPE_SUB = "Σ | actual − predicted |   /   Σ actual"
WAPE_STEPS = [
    ("ONE MONTH, ONE AIRCRAFT", "how far off we are, as a share of what really flew",
     f"| {ACT[0][0]} − {PRED[0][0]} |  /  {ACT[0][0]}  =  {100 * ERR[0] / ACT[0][0]:.1f}%"),
    ("THAT MONTH, ALL 14,000 AIRCRAFT",
     "cycles and hours are scored separately, then averaged: that is the month's score", ""),
    ("ALL TWELVE MONTHS", "every month counts the same, whatever the season, and the twelve "
     "scores are averaged", ""),
]
WAPE_PLAIN = (f"A WAPE of {100 * FINAL_WAPE:.0f}% means: for every 100 flight cycles or flight "
              f"hours the fleet really flew, the forecast is off by about "
              f"{100 * FINAL_WAPE:.0f} of them")
WAPE_NOTE = "Lower is better: 0% would be a perfect forecast, and every point you shave off is real"


def draw_wape(sc, a, lines=(0.0, 0.0, 0.0), months=0.0, plain=0.0):
    """The metric, built the way the evaluation script builds it."""
    x0, y0, x1, y1 = CARD
    mid = (x0 + x1) / 2
    sc.tile(WHITE, CARD, a, 0.8)
    sc.box(CARD, a, 0.8, 0.12)
    sc.text(mid, y0 + 2.0, WAPE_TITLE, 1.5, INK, a, True)
    sc.text(mid, y0 + 3.9, WAPE_SUB, 0.95, MUTED, a)
    tops = [y0 + 6.6, y0 + 12.6, y0 + 24.0]
    for k, (head, note, value) in enumerate(WAPE_STEPS):
        la = a * lines[k]
        if la <= 0.004:
            continue
        sc.text(x0 + 3.0, tops[k], head, 0.85, MUTED, la, True, "lm")
        sc.text(x0 + 3.0, tops[k] + 1.7, note, 0.8, MUTED, la, False, "lm")
        if value:
            sc.text(x1 - 3.0, tops[k] + 0.8, value, 1.5, INK, la, True, "rm")
        if k:
            sc.line(x0 + 3.0, tops[k] - 2.4, x1 - 3.0, tops[k] - 2.4, la * 0.5, 0.05)
    la = a * lines[1]
    for j, (name, err, act, ratio) in enumerate(JAN_ROWS):
        sc.text(x1 - 3.0, tops[1] + 3.6 + j * 1.7,
                f"{name}     {err:,}  /  {act:,}  =  {100 * ratio:.1f}%", 1.0, INK, la, True,
                "rm")
    sc.text(x1 - 3.0, tops[1] + 7.3, f"month score  =  ({100 * JAN_ROWS[0][3]:.1f}% + "
            f"{100 * JAN_ROWS[1][3]:.1f}%) / 2  =  {100 * JAN_SCORE:.1f}%", 1.1, SHARE_RED, la,
            True, "rm")
    for j, w in enumerate(MONTH_WAPES):  # the twelve monthly scores
        f = clamp01(months * 12 - j)
        x = lerp(x0 + 7.0, x1 - 7.0, j / 11)
        sc.text(x, tops[2] + 4.4, MONTHS[j], 0.75, MUTED, a * f)
        sc.text(x, tops[2] + 6.0, f"{100 * w:.1f}%", 0.95, INK, a * f, True)
    fin = a * clamp01(months * 12 - 11)
    sc.text(x1 - 3.0, tops[2] + 0.8, f"average  =  {100 * FINAL_WAPE:.1f}%", 2.2, SHARE_RED, fin,
            True, "rm")
    sc.text(mid, y1 - 2.2, WAPE_PLAIN, 1.05, INK, a * plain, True)
