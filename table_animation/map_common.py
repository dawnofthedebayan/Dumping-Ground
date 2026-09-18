"""Shared layout for the "machine learning map" animations (27-32).

The camera pulls far back so the whole evaluation slide from animation 26 becomes the
CLASSIFICATION panel, and the other problem types are drawn beside it in the same scene units:

    SUPERVISED LEARNING (labelled)                    UNSUPERVISED (no labels)
    [ CLASSIFICATION ]   [ REGRESSION ]               [ CLUSTERING ]
                              |
                         [ FORECASTING ]
    ======================== > 90% ===================|= < 10% =

`map_state(**progress)` draws everything; each animation animates its own element's progress and
passes 1.0 for everything added before it, so each GIF starts exactly where the last one ended.
The regression, forecasting and clustering points are illustrative, not the flight data.
"""

import math
import random

import anim_26_f1_score as f1
from common import (HEADER_BG, INK, MUTED, WHITE, clamp01, fit_scale, lerp)
from model_common import TITLE as _TITLE_POS, Scene

BLUE, AMBER, PURPLE = (59, 130, 246), (245, 158, 11), (139, 92, 246)
LIGHT = (203, 213, 225)

CLS = (-2.0, -1.5, 38.0, 13.5)
REG = (44.0, -1.5, 84.0, 13.5)
CLU = (90.0, -1.5, 130.0, 13.5)
FC = (50.0, 18.5, 78.0, 29.5)
CAM_MAP = (64.0, 11.2, fit_scale(137.0, 55.0, 0.03))

HEADINGS = {
    "cls": ("CLASSIFICATION", "Predict a category: delayed or on time?"),
    "reg": ("REGRESSION", "Predict a number: how many minutes late?"),
    "clu": ("CLUSTERING", "Find natural groups, no labels needed"),
}
TOP_TITLE = "Types of machine learning problems"


# ---------------------------------------------------------------- the classification thumbnail

def _classification_content():
    """Animation 26's final frame without its title and closing note: matrix + score cards."""
    st = f1.timeline(f1.DURATION)
    titles = {_TITLE_POS["y"], _TITLE_POS["sub"]}
    return dict(tiles=st["tiles"], boxes=st["boxes"], lines=st["lines"],
                texts=[x for x in st["texts"] if x[1] not in titles])


CLS_CONTENT = _classification_content()


# ---------------------------------------------------------------- illustrative data

def _regression_points(n=32, seed=3):
    rng = random.Random(seed)
    pts = []
    for _ in range(n):
        x = rng.uniform(2, 24)
        pts.append((x, max(1.0, 3 + 2.4 * x + rng.gauss(0, 6))))
    mx, my = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
    slope = sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts)
    return pts, slope, my - slope * mx


REG_POINTS, REG_SLOPE, REG_ICPT = _regression_points()


def _weekly_delays(n_hist=22, n_fc=8, seed=9):
    rng = random.Random(seed)
    level = lambda w: 14 + 0.25 * w + 5 * math.sin(w / 3.2)
    hist = [level(w) + rng.gauss(0, 1.6) for w in range(n_hist)]
    fc = [level(w) for w in range(n_hist - 1, n_hist + n_fc)]
    return hist, fc


FC_HIST, FC_FUTURE = _weekly_delays()


def _clusters(seed=4):
    rng = random.Random(seed)
    centres = [((6, 60), BLUE), ((19, 30), AMBER), ((33, 70), PURPLE)]
    pts = []
    for (cx, cy), col in centres:
        for _ in range(14):
            pts.append((cx + rng.gauss(0, 2.6), cy + rng.gauss(0, 7), col))
    rng.shuffle(pts)
    return pts, centres


CLU_POINTS, CLU_CENTRES = _clusters()


# ---------------------------------------------------------------- drawing

def _panel(sc, rect, a, key=None):
    sc.box(rect, a, 0.9, 0.16)
    if key:
        name, sub = HEADINGS[key]
        cx = (rect[0] + rect[2]) / 2
        sc.text(cx, rect[1] - 3.2, name, 1.9, INK, a, True)
        sc.text(cx, rect[1] - 1.2 + (1 - a) * 0.3, sub, 1.0, MUTED, a)


def _dot(sc, col, x, y, a, r=0.32):
    sc.tile(col, (x - r, y - r, x + r, y + r), a, r)


def _axes(sc, x0, y0, x1, y1, a, xlabel, ylabel):
    sc.line(x0, y1, x1, y1, a, 0.1)
    sc.line(x0, y0, x0, y1, a, 0.1)
    sc.text((x0 + x1) / 2, y1 + 0.95, xlabel, 0.8, MUTED, a)
    sc.text(x0 + 0.4, y0 - 0.2, ylabel, 0.8, MUTED, a, False, "lm")


def draw_regression(sc, frame, axes, dots, fit):
    _panel(sc, REG, frame, "reg")
    x0, y0, x1, y1 = 48.0, 1.6, 81.5, 11.2
    _axes(sc, x0, y0, x1, y1, axes, "Departures in the same hour", "Minutes late")
    px = lambda v: lerp(x0 + 0.8, x1 - 0.8, v / 25)
    py = lambda v: lerp(y1 - 0.4, y0 + 0.4, v / 70)
    for k, (x, y) in enumerate(REG_POINTS):
        _dot(sc, MUTED, px(x), py(y), clamp01(dots * len(REG_POINTS) - k))
    if fit > 0:
        xa, xb = 1.0, lerp(1.0, 24.5, fit)
        sc.line(px(xa), py(REG_SLOPE * xa + REG_ICPT), px(xb), py(REG_SLOPE * xb + REG_ICPT),
                1.0, 0.2)
        sc.text(px(9.5), py(7), f"minutes late  ≈  {REG_SLOPE:.1f} × departures  +  {REG_ICPT:.0f}",
                0.85, INK, clamp01(fit * 2 - 1), True, "lm")


def draw_forecast(sc, link, frame, history, future):
    mid = (FC[0] + FC[2]) / 2
    sc.line(mid, REG[3], mid, FC[1], link, 0.12, dashed=True)
    sc.text(mid + 0.8, (REG[3] + FC[1]) / 2, "a special case of regression", 0.85, MUTED, link,
            False, "lm")
    sc.box(FC, frame, 0.9, 0.16)
    sc.text(FC[0] + 1.2, FC[1] + 1.4, "FORECASTING", 1.3, INK, frame, True, "lm")
    sc.text(FC[0] + 1.2, FC[1] + 2.7, "Regression over time: predict next weeks' delays", 0.85,
            MUTED, frame, False, "lm")
    x0, y0, x1, y1 = 52.0, 22.4, 76.5, 27.7
    sc.line(x0, y1, x1, y1, frame, 0.08)
    sc.text(x0, y1 + 0.75, "past weeks", 0.75, MUTED, frame, False, "lm")
    n = len(FC_HIST) + len(FC_FUTURE) - 1
    px = lambda w: lerp(x0 + 0.3, x1 - 0.3, w / (n - 1))
    py = lambda v: lerp(y1 - 0.4, y0, (v - 8) / 22)
    now = px(len(FC_HIST) - 1)
    sc.line(now, y0 - 0.2, now, y1, frame * 0.8, 0.06, dashed=True)
    sc.text(now + 0.3, y1 + 0.75, "next weeks", 0.75, MUTED, future, False, "lm")
    shown = history * (len(FC_HIST) - 1)
    for w in range(len(FC_HIST) - 1):
        seg = clamp01(shown - w)
        if seg > 0:
            a, b = FC_HIST[w], FC_HIST[w + 1]
            sc.line(px(w), py(a), px(w + seg), py(lerp(a, b, seg)), 1.0, 0.16)
    base = len(FC_HIST) - 1
    for j in range(len(FC_FUTURE) - 1):
        seg = clamp01(future * (len(FC_FUTURE) - 1) - j)
        if seg > 0:
            a, b = FC_FUTURE[j], FC_FUTURE[j + 1]
            for q in range(8):  # uncertainty band widening into the future, in thin slices
                u = (q + 0.5) / 8
                if u <= seg:
                    spread = 0.25 + 0.2 * (j + u)
                    v = py(lerp(a, b, u))
                    sc.tile(HEADER_BG, (px(base + j + q / 8), v - spread,
                                        px(base + j + (q + 1) / 8) + 0.02, v + spread), 1.0, 0.0)
            sc.line(px(base + j), py(a), px(base + j + seg), py(lerp(a, b, seg)), 1.0, 0.16,
                    dashed=True)


def draw_clustering(sc, frame, dots, group):
    _panel(sc, CLU, frame, "clu")
    x0, y0, x1, y1 = 93.5, 1.6, 127.5, 11.2
    _axes(sc, x0, y0, x1, y1, dots, "Average delay (min)", "Flights per day")
    px = lambda v: lerp(x0 + 0.8, x1 - 0.8, v / 40)
    py = lambda v: lerp(y1 - 0.4, y0 + 0.4, v / 95)
    for (cx, cy), col in CLU_CENTRES:
        r = 4.3
        sc.box((px(cx) - r, py(cy) - r * 0.62, px(cx) + r, py(cy) + r * 0.62), group * 0.5,
               2.6, 0.1)
    for k, (x, y, col) in enumerate(CLU_POINTS):
        c = tuple(round(lerp(m, v, group)) for m, v in zip(MUTED, col))
        _dot(sc, c, px(x), py(y), clamp01(dots * len(CLU_POINTS) - k))


def draw_groups(sc, sup, unsup):
    for (x0, x1), a, name, sub in [
            ((CLS[0], REG[2]), sup, "SUPERVISED LEARNING", "we have labels: the right answers to learn from"),
            ((CLU[0], CLU[2]), unsup, "UNSUPERVISED", "no labels")]:
        if a <= 0:
            continue
        y = -6.9
        mid = (x0 + x1) / 2
        half = (x1 - x0) / 2 * a
        sc.line(mid - half, y, mid + half, y, 1.0, 0.14)
        sc.line(x0, y, x0, y + 1.0, clamp01(a * 2 - 1), 0.14)
        sc.line(x1, y, x1, y + 1.0, clamp01(a * 2 - 1), 0.14)
        sc.text(mid, y - 2.4, name, 1.35, INK, a, True)
        sc.text(mid, y - 1.1, sub, 0.95, MUTED, a)


SHARE = 0.9
BAR = (CLS[0], 33.4, CLU[2], 38.4)
SHARE_RED = (221, 83, 88)  # soft red for the headline share


def draw_share(sc, headline, bar, rest):
    x0, y0, x1, y1 = BAR
    sc.text((x0 + x1) / 2, y0 - 1.4, "Of all the ML problems our company will face", 1.4, INK,
            headline, True)
    split = lerp(x0, x1, SHARE)
    fill = lerp(x0, split, bar)
    label = clamp01(bar * 3 - 1)
    if bar > 0:
        sc.tile(SHARE_RED, (x0, y0, max(x0 + 0.01, fill), y1), 1.0, 0.9)
        sc.text((x0 + split) / 2, (y0 + y1) / 2,
                f"> {round(90 * bar)}%   CLASSIFICATION + REGRESSION", 2.4, WHITE, label, True)
        sc.text((x0 + split) / 2, y1 + 1.2, "supervised learning", 0.95, SHARE_RED, label, True)
    if rest > 0:
        sc.tile(LIGHT, (split + 0.3, y0, lerp(split + 0.3, x1, rest), y1), 1.0, 0.9)
        sc.text((split + x1) / 2 + 0.15, (y0 + y1) / 2, "< 10%", 1.7, INK, clamp01(rest * 2 - 1),
                True)
        sc.text((split + x1) / 2 + 0.15, y1 + 1.2, "clustering & other unsupervised", 0.85, MUTED,
                clamp01(rest * 2 - 1))


def map_state(camera=CAM_MAP, cls_content=1.0, top=1.0, cls=1.0, reg=(0, 0, 0, 0),
              fc=(0, 0, 0, 0), clu=(0, 0, 0), groups=(0, 0), share=(0, 0, 0)):
    sc = Scene()
    c = CLS_CONTENT
    sc.tiles = [(*x[:6], x[6] * cls_content) for x in c["tiles"]]
    sc.boxes = [(*x[:5], x[5] * cls_content, x[6]) for x in c["boxes"]]
    sc.lines = [(*x[:5], x[5] * cls_content, x[6]) for x in c["lines"]]
    sc.texts = [(*x[:5], x[5] * cls_content, *x[6:]) for x in c["texts"]]
    sc.text(CAM_MAP[0], -14.2, TOP_TITLE, 2.4, INK, top, True)
    _panel(sc, CLS, cls, "cls")
    sc.text((CLS[0] + CLS[2]) / 2, CLS[3] + 1.4, "what we just built", 0.95, MUTED, cls, True)
    draw_regression(sc, *reg)
    draw_forecast(sc, *fc)
    draw_clustering(sc, *clu)
    draw_groups(sc, *groups)
    draw_share(sc, *share)
    return sc.state(camera)


DONE = dict(reg=(1, 1, 1, 1), fc=(1, 1, 1, 1), clu=(1, 1, 1), groups=(1, 1), share=(1, 1, 1))
