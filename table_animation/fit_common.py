"""Shared model, layout and scene pieces for the fit animations (26a-26d).

Everything on screen comes from one real model: scikit-learn's GradientBoostingClassifier trained
on the 80 training flights of the chronological split, using two features only - wind speed and
visibility - so that what the model thinks fits on a screen as a map. Adding trees is the one dial
we turn; the three snapshots are the same model at 1, BEST and N_TREES trees.

    tree   1  train 55.0%  test 65.0%   nothing learned yet   (underfitting)
    tree  17  train 92.5%  test 75.0%   the test loss bottoms out here
    tree 100  train 100%   test 70.0%   every training flight memorised (overfitting)

The loss curves are the real staged log loss of that model on the training and the test rows, so
the U-turn on screen is the one in the data, not a drawing.
"""

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import log_loss

from common import GREEN, HEADER_BG, INK, MUTED, RED, WHITE, clamp01, lerp, mix
from model_common import ACCURACY, GB, KEYS, TEST, TRAIN, X, Y, Scene, pct
from split_common import color

# ---------------------------------------------------------------- the model

IW, IV = KEYS.index("wind"), KEYS.index("vis")
X2 = X[:, [IW, IV]]
DEPTH, RATE, N_TREES = 3, 0.05, 100

_G = GradientBoostingClassifier(n_estimators=N_TREES, max_depth=DEPTH, learning_rate=RATE,
                                random_state=0).fit(X2[TRAIN], Y[TRAIN])
_PTR = [p[:, 1] for p in _G.staged_predict_proba(X2[TRAIN])]
_PTE = [p[:, 1] for p in _G.staged_predict_proba(X2[TEST])]

TRAIN_LOSS = np.array([log_loss(Y[TRAIN], p, labels=[0, 1]) for p in _PTR])
TEST_LOSS = np.array([log_loss(Y[TEST], p, labels=[0, 1]) for p in _PTE])
TRAIN_ACC = np.array([((p >= 0.5) == Y[TRAIN]).mean() for p in _PTR])
TEST_ACC = np.array([((p >= 0.5) == Y[TEST]).mean() for p in _PTE])

BEST = int(TEST_LOSS.argmin()) + 1                      # 17 trees
_near = TEST_LOSS <= TEST_LOSS.min() * 1.05
BAND_A = int(np.argmax(_near))                          # last underfitting tree count
BAND_B = len(_near) - int(np.argmax(_near[::-1]))       # last "just right" tree count

# The numbers the deck already showed for the real seven-feature model (animations 21-26).
DECK_TRAIN_ACC = float(GB.score(X[TRAIN], Y[TRAIN]))
DECK_TEST_ACC = ACCURACY

SNAPS = [  # trees, name, how many trees, what the picture shows
    (1, "TOO SIMPLE", "1 tree", "One flat guess for the whole map"),
    (BEST, "JUST RIGHT", f"{BEST} trees", "A few broad, sensible regions"),
    (N_TREES, "TOO COMPLEX", f"{N_TREES} trees", "Sharp edges carved around single flights"),
]
SNAP_K = [k for k, *_ in SNAPS]

# ---------------------------------------------------------------- what the model thinks, as a map

WIND_LO, WIND_HI = 0.0, 50.0
VIS_LO, VIS_HI = 0.0, 10.5
GW, GH = 92, 64          # cells across, cells down (visibility high at the top)
LEVELS = 24              # probability steps, so flat areas merge into one tile
SAT = 0.34               # colour of a fully confident cell

_xs = (np.arange(GW) + 0.5) / GW * (WIND_HI - WIND_LO) + WIND_LO
_ys = VIS_HI - (np.arange(GH) + 0.5) / GH * (VIS_HI - VIS_LO)
_XX, _YY = np.meshgrid(_xs, _ys)
_GRID = np.c_[_XX.ravel(), _YY.ravel()]
_STAGES = [p[:, 1] for p in _G.staged_predict_proba(_GRID)]
PROB = {k: np.round(_STAGES[k - 1].reshape(GH, GW) * LEVELS).astype(int) for k in SNAP_K}

_COLOR = [mix(WHITE, GREEN, (0.5 - q / LEVELS) * 2 * SAT) if q < LEVELS / 2
          else mix(WHITE, RED, (q / LEVELS - 0.5) * 2 * SAT) for q in range(LEVELS + 1)]
FRAME = mix(WHITE, INK, 0.3)


def dot_xy(rect, i):
    x0, y0, x1, y1 = rect
    fx = (X2[i, 0] - WIND_LO) / (WIND_HI - WIND_LO)
    fy = 1 - (X2[i, 1] - VIS_LO) / (VIS_HI - VIS_LO)
    return x0 + fx * (x1 - x0), y0 + fy * (y1 - y0)


def draw_regions(sc, rect, k, a, reveal=1.0):
    """The model's prediction everywhere, as a colour wash. reveal sweeps it in left to right."""
    if a <= 0.004 or reveal <= 0:
        return
    x0, y0, x1, y1 = rect
    cw, ch = (x1 - x0) / GW, (y1 - y0) / GH
    upto = max(1, round(reveal * GW))
    P = PROB[k]
    for r in range(GH):
        row, c = P[r], 0
        while c < upto:
            q, c2 = row[c], c + 1
            while c2 < upto and row[c2] == q:
                c2 += 1
            sc.tile(_COLOR[q], (x0 + c * cw, y0 + r * ch, x0 + c2 * cw, y0 + (r + 1) * ch), a, 0.0)
            c = c2


def draw_dots(sc, rect, a, ids=TRAIN, ring=False):
    if a <= 0.004:
        return
    s = 0.0165 * (rect[2] - rect[0])
    for i in ids:
        x, y = dot_xy(rect, i)
        if ring:
            sc.tile(WHITE, (x - s * 1.7, y - s * 1.7, x + s * 1.7, y + s * 1.7), a, s * 1.7)
        sc.tile(color(i), (x - s, y - s, x + s, y + s), a, s * 0.45)


def draw_panel(sc, rect, k, a, regions=1.0, dots=1.0, axes=1.0, reveal=1.0, test_dots=0.0):
    """One map of the model: frame, colour wash, the flights it was trained on."""
    draw_regions(sc, rect, k, a * regions, reveal)
    sc.box(rect, a, 0.12, 0.05, FRAME)
    draw_dots(sc, rect, a * dots)
    if test_dots > 0:
        draw_dots(sc, rect, a * test_dots, TEST, ring=True)
    if axes > 0.004:
        w = rect[2] - rect[0]
        sc.text((rect[0] + rect[2]) / 2, rect[3] + 0.42, "WIND SPEED  (KT)  →", 0.026 * w,
                MUTED, a * axes, True)
        sc.text(rect[0], rect[1] - 0.32, "VISIBILITY (KM)  ↑", 0.026 * w, MUTED, a * axes,
                True, "lm")


def draw_panel_header(sc, rect, k, a, name_a=None):
    idx = SNAP_K.index(k)
    _, name, trees, caption = SNAPS[idx]
    cx = (rect[0] + rect[2]) / 2
    sc.text(cx, rect[1] - 1.72, f"{name}  ·  {trees}", 0.44, INK,
            a if name_a is None else name_a, True)
    sc.text(cx, rect[1] - 1.05, caption, 0.30, MUTED, a if name_a is None else name_a)


# ---------------------------------------------------------------- score rows

def score_row(sc, x0, x1, y, label, value, a, fill=INK, count=1.0, bar_x=None):
    """A labelled score with a bar, so three panels can be compared at a glance."""
    if a <= 0.004:
        return
    bar_x = bar_x if bar_x is not None else x1 - 2.55
    sc.text(x0, y, label, 0.28, MUTED, a, True, "lm")
    sc.text(x1, y + 0.02, pct(value * count), 0.5, INK, a, True, "rm")
    sc.tile(HEADER_BG, (x0, y + 0.42, bar_x, y + 0.6), a, 0.09)
    sc.tile(fill, (x0, y + 0.42, x0 + (bar_x - x0) * value * count, y + 0.6), a, 0.09)


def draw_scores(sc, rect, k, a, count=1.0):
    x0, x1 = rect[0] + 0.1, rect[2] - 0.1
    score_row(sc, x0, x1, rect[3] + 1.25, "ON THE 80 IT TRAINED ON", TRAIN_ACC[k - 1], a,
              mix(WHITE, INK, 0.38), count)
    score_row(sc, x0, x1, rect[3] + 2.35, "ON THE 20 IT NEVER SAW", TEST_ACC[k - 1], a, INK, count)


# ---------------------------------------------------------------- the loss chart

CHART = (3.2, 6.35, 34.2, 12.05)
LOSS_HI = 0.85
TRAIN_COL = mix(WHITE, INK, 0.42)
TEST_COL = INK
BANDS = [("TOO SIMPLE", 1, BAND_A), ("JUST RIGHT", BAND_A + 1, BAND_B),
         ("TOO COMPLEX", BAND_B + 1, N_TREES)]


def chart_x(tree):
    return lerp(CHART[0], CHART[2], (tree - 1) / (N_TREES - 1))


def chart_y(loss):
    return lerp(CHART[3], CHART[1], clamp01(loss / LOSS_HI))


def draw_axes(sc, a, ticks=1.0):
    x0, y0, x1, y1 = CHART
    sc.line(x0, y1, x1, y1, a, 0.055, color=FRAME)
    sc.line(x0, y0, x0, y1, a, 0.055, color=FRAME)
    sc.text((x0 + x1) / 2, y1 + 1.0, "TREES ADDED  →   (the model gets more complex)", 0.30,
            MUTED, a * ticks, True)
    sc.text(x0 - 0.35, (y0 + y1) / 2, "LOSS", 0.30, MUTED, a * ticks, True, "rm")
    sc.text(x0 - 0.35, (y0 + y1) / 2 + 0.6, "how wrong", 0.24, MUTED, a * ticks, False, "rm")
    for t in (1, 20, 40, 60, 80, 100):
        sc.text(chart_x(t), y1 + 0.42, str(t), 0.26, MUTED, a * ticks)


def draw_bands(sc, a):
    x0, y0, x1, y1 = CHART
    for j, (name, lo, hi) in enumerate(BANDS):
        bx0, bx1 = chart_x(lo) - (0.06 if lo == 1 else 0), chart_x(hi)
        tint = mix(WHITE, INK, 0.09) if j == 1 else mix(WHITE, INK, 0.03)
        sc.tile(tint, (bx0, y0, bx1, y1), a, 0.0)
        if j:
            sc.line(bx0, y0, bx0, y1, a * 0.7, 0.04, True, FRAME)
        sc.text((bx0 + bx1) / 2, y1 - 0.38, name, 0.30, MUTED, a, True)


def draw_curve(sc, values, upto, a, col, width=0.075):
    n = max(2, min(len(values), int(round(upto))))
    for k in range(n - 1):
        sc.line(chart_x(k + 1), chart_y(values[k]), chart_x(k + 2), chart_y(values[k + 1]), a,
                width, color=col)


def draw_gap(sc, upto, a):
    """The space between the two curves: what the model keeps for itself."""
    if a <= 0.004:
        return
    n = max(2, min(N_TREES, int(round(upto))))
    for k in range(n - 1):
        yt, yv = chart_y(TRAIN_LOSS[k]), chart_y(TEST_LOSS[k])
        sc.tile(mix(WHITE, RED, 0.15), (chart_x(k + 1), min(yt, yv), chart_x(k + 2) + 0.02,
                                       max(yt, yv)), a, 0.0)


def curve_label(sc, tree, values, text, a, col, dy=-0.55, anchor="lm"):
    if a > 0.004:
        sc.text(chart_x(tree) + (0.3 if anchor == "lm" else -0.3), chart_y(values[tree - 1]) + dy,
                text, 0.34, col, a, True, anchor)


# ---------------------------------------------------------------- panel placement

PANEL_Y0, PANEL_Y1 = 3.9, 9.9
PANEL_CX = (5.9, 18.1, 30.3)
PANEL_RECTS = [(cx - 5.5, PANEL_Y0, cx + 5.5, PANEL_Y1) for cx in PANEL_CX]
THUMB_RECTS = [(cx - 2.45, 2.15, cx + 2.45, 4.95) for cx in PANEL_CX]
