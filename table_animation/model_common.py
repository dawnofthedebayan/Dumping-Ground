"""Shared models, layout and scene pieces for the training and evaluation animations (18-26).

Both models are really trained on the 80 training flights of the chronological split (animation 16),
so the weights and trees on screen are real:

  * logistic regression, fitted by plain gradient descent on standardised features so the weight
    bars can replay the actual training path (it lands on the same weights as scikit-learn's
    LogisticRegression(C=1));
  * gradient-boosted trees (scikit-learn's GradientBoostingClassifier, the same idea as XGBoost,
    without needing xgboost installed).

The test-set probabilities in animations 21-26 are STAGED for the workshop story (a clearly strong
model): see `_staged_probabilities`. They keep the real model's ranking of the flights but are set so
the confusion matrix is TP 6, FN 1, FP 1, TN 12 (90% accuracy), and every metric is computed from
those counts, so the numbers stay mathematically consistent.

Scene layout (same scene units and camera as the split animations):
    left    training data grid (80 tiles) and hidden test grid (20 tiles)
    middle  the model box
    right   the output panel (probability of delay per test flight)
"""

import math

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier

from common import (CORRECT, GREEN, HEADER_BG, INK, MUTED, N_ROWS, RED, RED_DARK, encoded_text,
                    lerp, progress)
from split_common import CAMERA, CHRONO, CX, LABELS, color

# ---------------------------------------------------------------- data

FEATURES = [("model", "Model code"), ("sched", "Departure hour"), ("day", "Day of week"),
            ("wind", "Wind speed"), ("vis", "Visibility"), ("bad", "Bad weather"),
            ("deps", "Departures same hour")]
KEYS = [k for k, _ in FEATURES]
SHORT = {"model": "Model code", "sched": "Dep. hour", "day": "Day", "wind": "Wind",
         "vis": "Visibility", "bad": "Bad weather", "deps": "Departures/hour"}
DECIMALS = {"sched": 2, "wind": 1, "vis": 1}

X = np.array([[float(encoded_text(i, k)) for k in KEYS] for i in range(N_ROWS)])
Y = np.array(LABELS, dtype=float)
TRAIN, TEST = CHRONO.train_ids, CHRONO.test_ids

# ---------------------------------------------------------------- logistic regression

_MU, _SD = X[TRAIN].mean(0), X[TRAIN].std(0)
_Z = (X - _MU) / _SD
LR_STEPS = 600


def _fit_logreg(lr=0.5):
    """Gradient descent on mean log-loss + L2 (same objective as sklearn's C=1); every step kept."""
    zt, yt, n = _Z[TRAIN], Y[TRAIN], len(TRAIN)
    w, b, history = np.zeros(len(KEYS)), 0.0, []
    for _ in range(LR_STEPS + 1):
        p = 1 / (1 + np.exp(-(zt @ w + b)))
        loss = float(np.mean(-(yt * np.log(p) + (1 - yt) * np.log(1 - p))))
        history.append((w.copy(), loss))
        g = p - yt
        w = w - lr * (zt.T @ g / n + w / n)
        b -= lr * g.mean()
    return history


LR_HISTORY = _fit_logreg()
LR_MAX_W = max(abs(w) for w in LR_HISTORY[-1][0])

# ---------------------------------------------------------------- boosted trees

N_TREES = 50
GB = GradientBoostingClassifier(n_estimators=N_TREES, max_depth=2, learning_rate=0.1,
                                random_state=0).fit(X[TRAIN], Y[TRAIN])
REAL_P_TEST = GB.predict_proba(X[TEST])[:, 1]  # honest result: 75% accuracy (TP 4 FN 3 FP 2 TN 11)
TRUTH = [bool(Y[i]) for i in TEST]
MISSED_DELAYS, FALSE_ALARMS = 1, 1  # staged errors (7 delayed, 13 on time in the test set)


def _staged_probabilities():
    """Illustrative probabilities: ranked like the real model, errors limited to the counts above."""
    order = sorted(range(len(TEST)), key=lambda k: REAL_P_TEST[k])
    delayed = [k for k in order if TRUTH[k]]
    on_time = [k for k in order if not TRUTH[k]]
    p = [0.0] * len(TEST)
    missed, caught = delayed[:MISSED_DELAYS], delayed[MISSED_DELAYS:]
    alarms, quiet = on_time[len(on_time) - FALSE_ALARMS:], on_time[:len(on_time) - FALSE_ALARMS]
    for j, k in enumerate(caught):
        p[k] = lerp(0.66, 0.97, j / max(1, len(caught) - 1))
    for j, k in enumerate(quiet):
        p[k] = lerp(0.02, 0.31, j / max(1, len(quiet) - 1))
    for j, k in enumerate(missed):
        p[k] = 0.38 - 0.05 * j
    for j, k in enumerate(alarms):
        p[k] = 0.61 + 0.05 * j
    return p


P_TEST = _staged_probabilities()
PRED = [bool(p >= 0.5) for p in P_TEST]


def _condition(f, threshold):
    """Readable split: the largest real feature value on the 'yes' side, e.g. 'Visibility ≤ 5.1'."""
    vals = sorted(v for v in set(X[:, f]) if v <= threshold)
    d = DECIMALS.get(KEYS[f], 0)
    return f"{SHORT[KEYS[f]]}  ≤  {vals[-1]:.{d}f}"


def _tree(k):
    t = GB.estimators_[k, 0].tree_

    def node(n):
        if t.children_left[n] == -1:
            return ("leaf", float(t.value[n].ravel()[0]))
        return ("split", _condition(t.feature[n], t.threshold[n]),
                node(t.children_left[n]), node(t.children_right[n]))
    return node(0)


def _signature(k):
    t = GB.estimators_[k, 0].tree_
    return tuple(zip(t.feature, np.round(t.threshold, 3)))


TREE_IDS = [0, next(k for k in range(1, N_TREES) if _signature(k) != _signature(0))]
TREES = [_tree(k) for k in TREE_IDS]

# ---------------------------------------------------------------- metrics

TP = sum(p and y for p, y in zip(PRED, TRUTH))
FP = sum(p and not y for p, y in zip(PRED, TRUTH))
FN = sum(not p and y for p, y in zip(PRED, TRUTH))
TN = sum(not p and not y for p, y in zip(PRED, TRUTH))
N_TEST = len(TEST)
ACCURACY = (TP + TN) / N_TEST
PRECISION = TP / (TP + FP)
RECALL = TP / (TP + FN)
F1 = 2 * PRECISION * RECALL / (PRECISION + RECALL)
# The hand-written rule from animations 5-6, scored the way animation 6 scored it on screen:
# over all 100 flights (60 / 100). It was never trained on anything, so there is no held-out
# set to keep back from it, and quoting the same 60% here keeps the whole deck consistent.
WIND_RULE_ACC = sum(CORRECT) / N_ROWS


def pct(v):
    return f"{round(100 * v, 1):g}%"


# ---------------------------------------------------------------- layout

GRID_COLS, GRID_PITCH, GRID_TILE = 10, 0.62, 0.5
TRAIN_GRID0 = (0.6, 3.4)
TEST_GRID0 = (0.6, 9.55)
BOX = (9.6, 2.5, 25.4, 12.1)  # model box
OUT_X0, OUT_X1 = 27.6, 35.6
ROW0, ROW_STEP = 3.85, 0.4
BAR_X0, BAR_X1 = 28.4, 34.0
TITLE = dict(y=0.2, sub=1.35)


def grid_rect(k, origin, size=GRID_TILE):
    col, row = k % GRID_COLS, k // GRID_COLS
    x = origin[0] + col * GRID_PITCH + (GRID_PITCH - size) / 2
    y = origin[1] + row * GRID_PITCH + (GRID_PITCH - size) / 2
    return (x, y, x + size, y + size)


TRAIN_RECT = {i: grid_rect(k, TRAIN_GRID0) for k, i in enumerate(TRAIN)}
TEST_RECT = {i: grid_rect(k, TEST_GRID0) for k, i in enumerate(TEST)}
GRID_RECT = {**TRAIN_RECT, **TEST_RECT}


def out_row_y(k):
    return ROW0 + k * ROW_STEP


# ---------------------------------------------------------------- scene builder

class Scene:
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

    def arrow(self, x0, y, x1, a):
        self.line(x0, y, x1, y, a, 0.08)
        self.line(x1 - 0.35, y - 0.25, x1, y, a, 0.08)
        self.line(x1 - 0.35, y + 0.25, x1, y, a, 0.08)

    def title(self, title, subtitle, a):
        self.text(CX, TITLE["y"], title, 0.62, INK, a, True)
        self.text(CX, TITLE["sub"], subtitle, 0.38, MUTED, a)

    def state(self, camera=CAMERA):
        return dict(camera=camera, header_alpha=[0.0] * 4, row_alpha=[0.0] * N_ROWS,
                    tiles=self.tiles, boxes=self.boxes, lines=self.lines, texts=self.texts,
                    pills=self.pills)


def draw_data_panel(sc, a, test_a=None, skip_test=()):
    """Training grid, test grid and their labels (tiles in the grid, fully settled)."""
    test_a = a if test_a is None else test_a
    sc.text(TRAIN_GRID0[0] + 3.1, TRAIN_GRID0[1] - 0.55, "TRAINING DATA  ·  80", 0.32, INK, a, True)
    sc.text(TEST_GRID0[0] + 3.1, TEST_GRID0[1] - 0.5, "TEST DATA  ·  20  (hidden)", 0.32, INK,
            test_a, True)
    for i in TRAIN:
        sc.tile(color(i), TRAIN_RECT[i], a)
    for i in TEST:
        if i not in skip_test:
            sc.tile(color(i), TEST_RECT[i], test_a)


def draw_frame(sc, a, header="MODEL", header_a=None):
    """Model box, arrows and output label."""
    sc.box(BOX, a)
    sc.text((BOX[0] + BOX[2]) / 2, BOX[1] + 0.55, header, 0.34, INK,
            a if header_a is None else header_a, True)
    sc.arrow(7.3, 6.0, BOX[0] - 0.3, a)
    sc.arrow(BOX[2] + 0.3, 6.0, OUT_X0 - 0.2, a)
    sc.text((OUT_X0 + OUT_X1) / 2, BOX[1] + 0.55, "OUTPUT", 0.34, INK, a, True)


def draw_output_hint(sc, a):
    mid = (OUT_X0 + OUT_X1) / 2
    sc.text(mid, 6.6, "P(delay)", 0.55, INK, a, True)
    sc.text(mid, 7.45, "a probability from 0 to 1", 0.3, MUTED, a)


def draw_stream(sc, t, start, end, a=1.0):
    """Training tiles flowing from the data grid into the model box (two passes)."""
    if t < start or t > end + 1.2:
        return
    entry = (BOX[0] + 0.2, 6.0)
    for k, i in enumerate(TRAIN):
        for launch in (start + k * 0.025, start + 2.0 + k * 0.025):
            u = (t - launch) / 1.0
            if 0 <= u <= 1 and launch <= end:
                x0, y0, x1, y1 = TRAIN_RECT[i]
                cx = lerp((x0 + x1) / 2, entry[0], u)
                cy = lerp((y0 + y1) / 2, entry[1], u) - math.sin(math.pi * u) * 0.8
                s = 0.18
                sc.tile(color(i), (cx - s, cy - s, cx + s, cy + s), a * min(1, 4 * (1 - u)))


# ---- logistic regression contents

LR_ZERO_X, LR_SCALE = 19.4, 4.6 / LR_MAX_W
LR_ROW0, LR_ROW_STEP = 4.55, 0.74


def draw_logreg(sc, a, step, header=True):
    w, loss = LR_HISTORY[step]
    x0 = BOX[0] + 0.5
    sc.text(x0, 3.75, "LEARNED WEIGHTS", 0.28, MUTED, a, True, "lm")
    sc.text(LR_ZERO_X - 0.3, 3.75, "lowers delay risk", 0.26, MUTED, a, False, "rm")
    sc.text(LR_ZERO_X + 0.3, 3.75, "raises delay risk", 0.26, MUTED, a, False, "lm")
    sc.line(LR_ZERO_X, 4.1, LR_ZERO_X, LR_ROW0 + 6.4 * LR_ROW_STEP, a, 0.05)
    for k, (_, name) in enumerate(FEATURES):
        y = LR_ROW0 + k * LR_ROW_STEP
        sc.text(x0, y, name, 0.32, INK, a, False, "lm")
        length = w[k] * LR_SCALE
        rect = (min(LR_ZERO_X, LR_ZERO_X + length), y - 0.2, max(LR_ZERO_X, LR_ZERO_X + length),
                y + 0.2)
        sc.tile(RED if w[k] > 0 else GREEN, rect, a)
        side = 1 if w[k] >= 0 else -1
        sc.text(LR_ZERO_X + length + side * 0.2, y, f"{w[k]:+.2f}".replace("-", "−"), 0.26,
                MUTED, a, False, "lm" if side > 0 else "rm")
    sc.text((BOX[0] + BOX[2]) / 2, 10.35, "P(delay)  =  σ( Σ  weight × feature  +  bias )",
            0.36, INK, a, True)
    sc.text((BOX[0] + BOX[2]) / 2, 11.2,
            f"training step {step} / {LR_STEPS}     ·     error (log-loss) {loss:.3f}", 0.28,
            MUTED, a)


# ---- boosted-tree contents

TREE_Y = [4.0, 7.35]
LEVEL = [0.0, 1.1, 2.1]


def draw_trees(sc, a, grow):
    """grow[k] in 0..1 reveals tree k: root, then its branches, then its leaves."""
    mid = (BOX[0] + BOX[2]) / 2
    for k, (tree, y0) in enumerate(zip(TREES, TREE_Y)):
        g = grow[k]
        if g <= 0:
            continue
        sc.text(BOX[0] + 0.5, y0, f"TREE {TREE_IDS[k] + 1}", 0.28, MUTED, a * min(1, g * 3), True,
                "lm")
        _draw_node(sc, tree, mid, y0, 0, 3.7, a, g)
    sc.text(mid, 10.85, f"P(delay)  =  σ( sum of leaf scores from all {N_TREES} trees )", 0.34,
            INK, a * min(1, max(0, grow[-1] * 2 - 1)), True)


def _draw_node(sc, node, x, y, depth, spread, a, g):
    reveal = min(1, max(0, g * 3 - depth))  # depth 0 first, then 1, then 2
    if reveal <= 0:
        return
    if node[0] == "leaf":
        value = node[1]
        r = 0.27
        sc.tile(RED if value > 0 else GREEN, (x - r, y - r, x + r, y + r), a * reveal, r)
        sc.text(x, y + 0.55, f"{value:+.2f}".replace("-", "−"), 0.24, MUTED, a * reveal)
        return
    _, cond, yes, no = node
    for child, side, word in [(yes, -1, "yes"), (no, 1, "no")]:
        cx, cy = x + side * spread, y + LEVEL[depth + 1] - LEVEL[depth]
        ca = a * min(1, max(0, g * 3 - depth - 1))
        sc.line(x, y, cx, cy, ca, 0.05)
        sc.text(x + 0.62 * (cx - x) + side * 0.3, y + 0.62 * (cy - y) - 0.1, word, 0.22, MUTED,
                ca)
        _draw_node(sc, child, cx, cy, depth + 1, spread * 0.42, a, g)
    sc.pill(x, y, cond, 0.27 * (0.85 + 0.15 * reveal), a * reveal)


# ---- output rows

def draw_output_row(sc, k, i, fill, a, text_a=None):
    y = out_row_y(k)
    sc.tile(HEADER_BG, (BAR_X0, y - 0.15, BAR_X1, y + 0.15), a, 0.15)
    p = P_TEST[k]
    col = RED if PRED[k] else GREEN
    if fill > 0:
        sc.tile(col, (BAR_X0, y - 0.15, BAR_X0 + (BAR_X1 - BAR_X0) * p * fill, y + 0.15), a, 0.15)
    ta = a * fill if text_a is None else text_a
    sc.text(OUT_X1, y, f"{round(100 * p * fill)}%", 0.28, RED_DARK if PRED[k] else INK, ta, True,
            "rm")


def output_tile_rect(k):
    y = out_row_y(k)
    return (OUT_X0 + 0.05, y - 0.17, OUT_X0 + 0.39, y + 0.17)


def draw_threshold(sc, a):
    x = (BAR_X0 + BAR_X1) / 2
    sc.line(x, ROW0 - 0.35, x, out_row_y(N_TEST - 1) + 0.3, a, 0.05, dashed=True)
    sc.text(x, out_row_y(N_TEST - 1) + 0.6, "50%", 0.26, MUTED, a, True)


# ---------------------------------------------------------------- confusion matrix + metrics

CELL_W, CELL_H, CELL_GAP = 6.0, 3.4, 0.2
MX0, MY0 = 4.9, 3.7
CELLS = {  # (actual delayed, predicted delayed) -> (row, col, short, long name)
    (True, True): (0, 0, "TP", "TRUE POSITIVE"),
    (True, False): (0, 1, "FN", "FALSE NEGATIVE  ·  missed delay"),
    (False, True): (1, 0, "FP", "FALSE POSITIVE  ·  false alarm"),
    (False, False): (1, 1, "TN", "TRUE NEGATIVE"),
}
COUNTS = {"TP": TP, "FN": FN, "FP": FP, "TN": TN}


def cell_rect(row, col):
    x = MX0 + col * (CELL_W + CELL_GAP)
    y = MY0 + row * (CELL_H + CELL_GAP)
    return (x, y, x + CELL_W, y + CELL_H)


def _cell_slots():
    """Tile rect inside its confusion cell for each test position k (in arrival order)."""
    filled, slots = {}, {}
    for k in range(N_TEST):
        key = (TRUTH[k], PRED[k])
        n = filled.get(key, 0)
        filled[key] = n + 1
        row, col, _, _ = CELLS[key]
        x0, y0, _, _ = cell_rect(row, col)
        c, r = n % 6, n // 6
        slots[k] = (x0 + 0.4 + c * 0.62, y0 + 0.95 + r * 0.62, x0 + 0.4 + c * 0.62 + 0.5,
                    y0 + 0.95 + r * 0.62 + 0.5)
    return slots


CELL_SLOT = _cell_slots()


def draw_matrix(sc, a, counts_upto=None, focus=None, focus_a=0.0):
    """Grid, labels and counts. counts_upto: how many test tiles have landed (None = all).
    focus: cell shorts to outline; the other cells dim by focus_a."""
    for (actual, predicted), (row, col, short, name) in CELLS.items():
        rect = cell_rect(row, col)
        dim = 1 - 0.6 * focus_a if focus and short not in focus else 1.0
        sc.tile(HEADER_BG, rect, a * dim, 0.3)
        sc.text(rect[0] + 0.4, rect[1] + 0.45, name, 0.26, MUTED, a * dim, True, "lm")
        landed = sum(1 for k in range(N_TEST) if (TRUTH[k], PRED[k]) == (actual, predicted)
                     and (counts_upto is None or k < counts_upto))
        sc.text(rect[2] - 0.45, rect[1] + 2.45, str(landed), 1.1, INK, a * dim, True, "rm")
        sc.text(rect[2] - 0.45, rect[1] + 0.45, short, 0.34, INK, a * dim, True, "rm")
        if focus and short in focus:
            sc.box((rect[0] - 0.1, rect[1] - 0.1, rect[2] + 0.1, rect[3] + 0.1), a * focus_a,
                   0.38, 0.1)
    for col, label in enumerate(["PREDICTED DELAYED", "PREDICTED ON TIME"]):
        x0, y0, x1, _ = cell_rect(0, col)
        sc.text((x0 + x1) / 2, y0 - 0.5, label, 0.3, INK, a, True)
    for row, label in enumerate(["ACTUALLY DELAYED", "ACTUALLY ON TIME"]):
        x0, y0, _, y1 = cell_rect(row, 0)
        sc.text(x0 - 0.35, (y0 + y1) / 2, label, 0.3, INK, a, True, "rm")


def matrix_tiles(sc, a, focus=None, focus_a=0.0):
    for k, i in enumerate(TEST):
        short = CELLS[(TRUTH[k], PRED[k])][2]
        dim = 1 - 0.6 * focus_a if focus and short not in focus else 1.0
        sc.tile(color(i), CELL_SLOT[k], a * dim)


METRICS = [
    ("ACCURACY", "How often is the model right?", ACCURACY,
     f"Accuracy  =  (TP + TN) / all  =  ({TP} + {TN}) / {N_TEST}  =  {pct(ACCURACY)}",
     ("TP", "TN")),
    ("PRECISION", "When it predicts a delay, how often is it right?", PRECISION,
     f"Precision  =  TP / (TP + FP)  =  {TP} / ({TP} + {FP})  =  {pct(PRECISION)}", ("TP", "FP")),
    ("RECALL", "Of the flights really delayed, how many did it catch?", RECALL,
     f"Recall  =  TP / (TP + FN)  =  {TP} / ({TP} + {FN})  =  {pct(RECALL)}", ("TP", "FN")),
    ("F1 SCORE", "One number balancing precision and recall", F1,
     f"F1  =  2 × P × R / (P + R)  =  2 × {PRECISION:.2f} × {RECALL:.2f} / "
     f"({PRECISION:.2f} + {RECALL:.2f})  =  {pct(F1)}", ("TP", "FP", "FN")),
]
CARD_X0, CARD_X1, CARD_Y0, CARD_H, CARD_GAP = 19.4, 35.6, 3.2, 1.85, 0.22
FORMULA_Y = 11.85


def draw_card(sc, k, a, count=1.0, slide=1.0, note=None):
    name, question, value, _, _ = METRICS[k]
    y0 = CARD_Y0 + k * (CARD_H + CARD_GAP)
    dx = (1 - slide) * 1.2
    rect = (CARD_X0 + dx, y0, CARD_X1 + dx, y0 + CARD_H)
    sc.tile(HEADER_BG, rect, a, 0.3)
    sc.text(rect[0] + 0.45, y0 + 0.62, name, 0.34, INK, a, True, "lm")
    sc.text(rect[0] + 0.45, y0 + 1.25, note or question, 0.27, MUTED, a, False, "lm")
    sc.text(rect[2] - 0.45, y0 + CARD_H / 2, pct(value * count), 0.8, INK, a, True, "rm")


MATRIX_NOTE = "Rows: what really happened   ·   Columns: what the model predicted"
FINAL_NOTE = (f"{pct(ACCURACY)} accurate vs {pct(WIND_RULE_ACC)} for the wind-speed rule: "
              "the model learned far better rules than we wrote by hand")


def metric_timeline(k, prev_title, title):
    """(timeline, duration) for metric k: its cells light up, the formula appears, its card slides
    in and counts up. Starts from the end of the previous evaluation animation."""
    _, _, _, formula, focus = METRICS[k]
    prev_focus = METRICS[k - 1][4] if k else None
    prev_note = METRICS[k - 1][3] if k else MATRIX_NOTE
    last = k == len(METRICS) - 1
    final_t = 6.2
    duration = 10.0 if last else 6.5

    def timeline(t):
        sc = Scene()
        sc.title(*prev_title, 1 - progress(t, 0.1, 0.4))
        sc.title(*title, progress(t, 0.45, 0.5))
        old_a = (1 - progress(t, 0.2, 0.4)) if prev_focus else 0.0
        new_a = progress(t, 0.8, 0.5) * (1 - (progress(t, final_t, 0.5) if last else 0))
        cells, fa = (prev_focus, old_a) if old_a > new_a else (focus, new_a)
        draw_matrix(sc, 1.0, None, cells, fa)
        matrix_tiles(sc, 1.0, cells, fa)
        for j in range(k):
            draw_card(sc, j, 1.0, note=CARD_NOTES.get(j))
        slide = progress(t, 2.0, 0.6)
        draw_card(sc, k, slide, count=progress(t, 2.3, 1.2), slide=slide, note=CARD_NOTES.get(k))
        sc.pill(CX, FORMULA_Y, prev_note, 0.36, 1 - progress(t, 0.2, 0.4))
        fin = progress(t, final_t + 0.4, 0.5) if last else 0.0
        sc.pill(CX, FORMULA_Y, formula, 0.36, progress(t, 1.3, 0.5) * (1 - (
            progress(t, final_t, 0.4) if last else 0)))
        sc.pill(CX, FORMULA_Y, FINAL_NOTE, 0.36, fin)
        return sc.state()

    return timeline, duration


CARD_NOTES = {0: f"How often is it right?   (wind-speed rule: {pct(WIND_RULE_ACC)})"}


def fade_state(st, a):
    """A copy of a finished animation's state with every free element at opacity a."""
    s = dict(st)
    s["tiles"] = [(*x[:6], x[6] * a) for x in st.get("tiles", [])]
    s["boxes"] = [(*x[:5], x[5] * a, *x[6:]) for x in st.get("boxes", [])]
    s["lines"] = [(*x[:5], x[5] * a, *x[6:]) for x in st.get("lines", [])]
    s["texts"] = [(*x[:5], x[5] * a, *x[6:]) for x in st.get("texts", [])]
    s["pills"] = [(*x[:4], x[4] * a, *x[5:]) for x in st.get("pills", [])]
    return s
