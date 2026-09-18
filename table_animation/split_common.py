"""Shared layout and timeline builder for the train/test split animations (12-17).

After animation 12 every flight is one tile in a horizontal bar (red = delayed, green = on time).
A split animation (see `split_timeline`) runs through these phases:

    merge    the previous split's train/test bars slide back into one bar
    reorder  tiles slide to a new order (shuffle, group by class, sort by date)
    pick     the tiles going to test lift up while the rest dim; dividers and labels show the cut
    split    tiles glide into a TRAIN bar (left) and a TEST bar (right)
    result   labels, delayed share of each set and a take-away note appear

All positions are in the same scene units as the encoded 10-row table, so the camera never moves.
"""

import datetime as dt
import math
import random

from anim_10_new_feature import FEATURE_COLS
from common import (DAYS, DATA, EXTRA, GREEN, INK, MUTED, N_ROWS, RED, RED_DARK,
                    ease_in_out_cubic, lerp, progress, table_camera)

CAMERA = table_camera(FEATURE_COLS)
CX = CAMERA[0]

PITCH, TILE_W, TILE_R = 0.33, 0.25, 0.06
BAR_TOP, BAR_BOT = 4.6, 8.4
FULL_X0 = CX - N_ROWS * PITCH / 2
GAP = 1.6  # between the TRAIN and TEST bars
SPLIT_X0 = CX - (N_ROWS * PITCH + GAP) / 2
TITLE_Y, SUB_Y, LABEL_Y = 0.2, 1.35, BAR_TOP - 0.7
SPAN_Y = BAR_TOP - 1.35  # pick-phase labels sit above the lifted test tiles
STAT_Y, COUNT_Y, NOTE_Y = BAR_BOT + 0.8, BAR_BOT + 1.45, BAR_BOT + 3.0
N_TEST = 20

LABELS = [d for _, _, d in DATA]
N_DELAYED = sum(LABELS)


def color(i):
    return RED if LABELS[i] else GREEN


def pct(n, total):
    return f"{round(100 * n / total, 1):g}%"


# ---------------------------------------------------------------- orders

def _dates(seed=5):
    """A 2025 departure date per flight whose weekday matches its DAY OF WEEK column."""
    rng = random.Random(seed)
    first_monday = dt.date(2025, 1, 6)
    return [first_monday + dt.timedelta(days=7 * rng.randrange(51) + DAYS.index(e["day"]))
            for e in EXTRA]


DATES = _dates()
INDEX_ORDER = list(range(N_ROWS))
RANDOM_ORDER = INDEX_ORDER[:]
random.Random(66).shuffle(RANDOM_ORDER)  # seed 66: the last 20 hold only 4 delayed flights
CHRONO_ORDER = sorted(INDEX_ORDER, key=lambda i: (DATES[i], EXTRA[i]["sched"]))


def slot_x(slot, x0=FULL_X0):
    return x0 + slot * PITCH


def tile_rect(x):
    x0 = x + (PITCH - TILE_W) / 2
    return (x0, BAR_TOP, x0 + TILE_W, BAR_BOT)


def lerp_rect(a, b, t):
    return tuple(lerp(p, q, t) for p, q in zip(a, b))


# ---------------------------------------------------------------- views

class BarView:
    """All 100 flights in one bar, in `order`, with a title and optional overlays."""

    split_rect = None

    def __init__(self, order, title, subtitle):
        self.order = list(order)
        self.slot = {i: k for k, i in enumerate(self.order)}
        self.title, self.subtitle = title, subtitle

    def full_rect(self, i):
        return tile_rect(slot_x(self.slot[i]))

    def overlays(self, a):
        """(texts, pills, lines) shown when this view is complete, at opacity a."""
        n = N_DELAYED
        return [(CX, STAT_Y, f"{n} delayed   ·   {N_ROWS - n} on time", 0.4, INK, a, True, "mm")], [], []


class Split(BarView):
    def __init__(self, order, test, title, subtitle, note, spans, stats=True):
        super().__init__(order, title, subtitle)
        self.test = set(test)
        self.train_ids = [i for i in self.order if i not in self.test]
        self.test_ids = [i for i in self.order if i in self.test]
        self.split_rect = {}
        for k, i in enumerate(self.train_ids):
            self.split_rect[i] = tile_rect(slot_x(k, SPLIT_X0))
        test_x0 = SPLIT_X0 + len(self.train_ids) * PITCH + GAP
        for k, i in enumerate(self.test_ids):
            self.split_rect[i] = tile_rect(slot_x(k, test_x0))
        self.train_cx = SPLIT_X0 + len(self.train_ids) * PITCH / 2
        self.test_cx = test_x0 + len(self.test_ids) * PITCH / 2
        self.note, self.spans, self.stats = note, spans, stats

    def overlays(self, a):
        texts = []
        for name, ids, x in [("TRAIN", self.train_ids, self.train_cx),
                             ("TEST", self.test_ids, self.test_cx)]:
            texts.append((x, LABEL_Y, f"{name}  ·  {len(ids)} flights", 0.42, INK, a, True, "mm"))
            if self.stats:
                n = sum(LABELS[i] for i in ids)
                texts.append((x, STAT_Y, f"{pct(n, len(ids))} delayed", 0.44, RED_DARK, a, True,
                               "mm"))
                texts.append((x, COUNT_Y, f"{n} of {len(ids)} flights", 0.32, MUTED, a, False,
                               "mm"))
        return texts, [(CX, NOTE_Y, self.note, 0.4, a)], []

    def span_overlays(self, a):
        """Dividers and labels on the single bar marking what goes to test (pick phase)."""
        texts, lines = [], []
        for s0, s1, label in self.spans:
            texts.append(((slot_x(s0) + slot_x(s1)) / 2, SPAN_Y, label, 0.36, INK, a, True, "mm"))
            if s0 > 0:
                x = slot_x(s0)
                lines.append((x, SPAN_Y - 0.25, x, BAR_BOT + 0.35, 0.06, a, True))
        return texts, lines


def title_items(view, a):
    return [(CX, TITLE_Y, view.title, 0.62, INK, a, True, "mm"),
            (CX, SUB_Y, view.subtitle, 0.38, MUTED, a, False, "mm")]


def fade_between(prev, cur, t):
    """Previous view's title and results fade out, then the new title fades in."""
    out = 1 - progress(t, 0.1, 0.4)
    texts = title_items(prev, out) + title_items(cur, progress(t, 0.45, 0.5))
    ptexts, ppills, plines = prev.overlays(out)
    return texts + ptexts, ppills, plines


def bar_state(tiles, texts, pills=(), lines=()):
    return dict(camera=CAMERA, header_alpha=[0.0] * 4, row_alpha=[0.0] * N_ROWS,
                tiles=tiles, texts=list(texts), pills=list(pills), lines=list(lines))


# ---------------------------------------------------------------- split timeline

def regroup_rect(i, t, prev, cur, times):
    """Tile i's rect (and arc offset) while merging back from `prev` and reordering into `cur`."""
    r = prev.full_rect(i)
    if "merge" in times:
        p = progress(t, times["merge"] + 0.004 * prev.slot[i], 1.0, ease_in_out_cubic)
        r = lerp_rect(prev.split_rect[i], r, p)
    dy = 0.0
    if "reorder" in times:
        p = progress(t, times["reorder"] + 0.006 * cur.slot[i], 1.4, ease_in_out_cubic)
        r = lerp_rect(r, cur.full_rect(i), p)
        dy = math.sin(math.pi * p) * 1.1 * (1 if i % 2 else -1)
    return r, dy


def split_timeline(cur, prev, reorder=True, extras=None, extras_time=0.0):
    """Build (timeline, duration) for moving from `prev` (a view) to the split `cur`.

    extras(t, phase_times) -> (texts, lines) lets an animation add its own overlays (the date
    axis); extras_time adds that much pause after the reorder to show them.
    """
    t0, times = 0.3, {}
    if prev.split_rect:
        times["merge"] = t0
        t0 += 1.4
    if reorder:
        times["reorder"] = t0
        t0 += 2.0 + extras_time
    times["pick"] = t0
    times["split"] = t0 + 1.4
    times["result"] = t0 + 3.0
    duration = times["result"] + 3.2

    def timeline(t):
        pick = progress(t, times["pick"], 0.6)
        tiles = []
        for i in INDEX_ORDER:
            r, dy = regroup_rect(i, t, prev, cur, times)
            p = progress(t, times["split"] + 0.004 * cur.slot[i], 1.1, ease_in_out_cubic)
            r = lerp_rect(r, cur.split_rect[i], p)
            lift = -0.7 * pick * (1 - p) if i in cur.test else 0.0
            alpha = 1 - (0 if i in cur.test else 0.55 * pick * (1 - p))
            tiles.append((color(i), r[0], r[1] + dy + lift, r[2], r[3] + dy + lift,
                          TILE_R, alpha))

        texts, pills, lines = fade_between(prev, cur, t)
        span_a = pick * (1 - progress(t, times["split"], 0.4))
        stexts, slines = cur.span_overlays(span_a)
        rtexts, rpills, rlines = cur.overlays(progress(t, times["result"], 0.5))
        rpills = [(x, y, s, size, a * progress(t, times["result"] + 0.5, 0.5))
                  for x, y, s, size, a in rpills]
        texts += stexts + rtexts
        lines += slines + rlines
        pills += rpills
        if extras:
            etexts, elines = extras(t, times)
            texts += etexts
            lines += elines
        return bar_state(tiles, texts, pills, lines)

    return timeline, duration


# ---------------------------------------------------------------- the views, in story order

DATASET = BarView(INDEX_ORDER, "Our dataset: 100 flights",
                  "Each tile is one flight   ·   red = delayed (1)   ·   green = on time (0)")

SIMPLE = Split(
    INDEX_ORDER, INDEX_ORDER[-N_TEST:],
    "Train / test split  ·  80 : 20",
    "The model learns from 80% of the flights; 20% stay hidden to check it on unseen data",
    "The model never sees the test flights while it learns",
    [(0, 80, "80%  ·  TRAIN"), (80, 100, "20%  ·  TEST")], stats=False)

RANDOM = Split(
    RANDOM_ORDER, RANDOM_ORDER[-N_TEST:],
    "Random split",
    "Shuffle the flights, then cut: every flight has the same chance of landing in test",
    f"Unlucky draw: test has {pct(sum(LABELS[i] for i in RANDOM_ORDER[-N_TEST:]), N_TEST)} "
    f"delayed flights, reality has {pct(N_DELAYED, N_ROWS)}",
    [(0, 80, "TRAIN"), (80, 100, "TEST")])


def _stratified():
    delayed = [i for i in RANDOM_ORDER if LABELS[i]]
    on_time = [i for i in RANDOM_ORDER if not LABELS[i]]
    nd, no = round(len(delayed) * 0.2), round(len(on_time) * 0.2)
    test = delayed[-nd:] + on_time[-no:]
    a, b = len(delayed) - nd, len(delayed)
    c = b + len(on_time) - no
    spans = [(0, a, "80% of delayed"), (a, b, "20%"), (b, c, "80% of on time"), (c, N_ROWS, "20%")]
    return Split(
        delayed + on_time, test,
        "Stratified split  (class-aware)",
        "Split each class on its own, so train and test keep the real delayed / on-time mix",
        f"Both sets keep ~{pct(N_DELAYED, N_ROWS)} delayed: vital when one class is rare "
        "(e.g. only 5% delayed)",
        spans)


STRATIFIED = _stratified()

_cut = DATES[CHRONO_ORDER[N_ROWS - N_TEST]]
CHRONO = Split(
    CHRONO_ORDER, CHRONO_ORDER[-N_TEST:],
    "Chronological split",
    "Sort by departure date: train on the past, test on the most recent flights",
    "Closest to reality: once deployed, the model only ever predicts future flights",
    [(0, 80, "PAST  ·  TRAIN"), (80, 100, f"FUTURE  ·  from {_cut:%-d %b}")])
