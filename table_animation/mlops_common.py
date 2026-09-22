"""Shared scene for the deployment and monitoring animations (33-35), 1080p only.

    left    live flights stream through the deployed model; the MLOps loop below it
    right   a monitoring dashboard: live F1, data drift, concept drift

    33  mlops monitoring     deploy, weeks tick by, both drifts creep in, F1 falls below the
                             threshold and the ALERT fires: the animation stops there
    34  data drift           time is paused at the alert; the data-drift chart is highlighted
                             and the left side explains it (fog days replacing clear days);
                             ends holding the explanation
    35  concept drift        the data-drift highlight clears, the concept-drift chart is
                             highlighted and the left side animates the cause (a runway closes,
                             13 departure slots become 8, the 9th flight of a busy hour has no
                             slot); ends holding the explanation
    36  constant monitoring  the highlight clears, "MLOps requires constant monitoring" appears
                             and the live stream keeps running while the Monitor stage pulses
    37  retrain & redeploy   the loop moves through check hypothesis, new data, retrain, evaluate
                             and deploy; MODEL v2 goes live, F1 recovers, the drift charts line
                             up again, and the loop carries on (v2, v3, v4, ...)

Each GIF knows its start time on a global clock, so the flight stream stays continuous between
GIFs. All numbers are illustrative.
"""

import math

from common import (GREEN, GREEN_DARK, HEADER_BG, INK, MUTED, RED, RED_TINT, WHITE, clamp01,
                    ease_in_out_cubic, fit_scale, lerp, mix, progress)
from map_common import SHARE_RED

CAM_OPS = (50.0, 18.2, fit_scale(104.0, 59.0, 0.02))
MODEL_BOX = (14.0, -2.0, 30.0, 8.0)
TITLE = ("Deployment: MLOps begins", "A model in production has to be watched, constantly")
FINAL_NOTE = "MLOps requires constant monitoring"
NOTE_Y = 46.0

# ---------------------------------------------------------------- global clock

FPS = 25
DURATIONS = {"monitor": 20.5, "data": 14.0, "concept": 19.0, "constant": 38.0,
             "retrain": 21.0}  # keep each under Google Slides' 1000-frame limit


def last_frame_time(duration):
    """Time of a GIF's last rendered frame (main() renders round(duration * FPS) frames)."""
    return (round(duration * FPS) - 1) / FPS


T0 = {"monitor": 0.0}  # the next GIF's t = 0 is the previous GIF's last frame
T0["data"] = T0["monitor"] + last_frame_time(DURATIONS["monitor"])
T0["concept"] = T0["data"] + last_frame_time(DURATIONS["data"])
T0["constant"] = T0["concept"] + last_frame_time(DURATIONS["concept"])
T0["retrain"] = T0["constant"] + last_frame_time(DURATIONS["constant"])
DONE = 100.0  # an explainer clock value at which every step has finished
STREAM_START = 4.0  # global seconds

# ---------------------------------------------------------------- the world, week by week

AXIS_WEEKS, ALERT_WEEK, PAUSE_WEEK = 30.0, 24.0, 24.2  # the story pauses at the alert
DEPLOY_WEEK = 31.0  # model v2 goes live (animation 37)
EXAMPLE_DEPS = 9
DATA_WHY = (10.0, "Why: winter fog, far more low-visibility days than in the training data")
CONCEPT_WHY = (17.0, "Why: runway 2 closed for works, the airport now jams at 8 departures "
                     "an hour instead of 13")
LOOP = ["Monitor", "Check hypothesis", "Collect new data", "Retrain", "Evaluate", "Deploy"]
STAGES = [  # (name, first week active, caption)
    ("Monitor", -1.0, "Watch live performance and the data, every day"),
    ("Check hypothesis", 24.5, "Is the problem still the same? What changed?"),
    ("Collect new data", 25.8, "Label recent flights that show fog and the closed runway"),
    ("Retrain", 27.1, "Fit the model again on fresh data"),
    ("Evaluate", 29.1, "Test v2 on held-out recent flights before release"),
    ("Deploy", 30.5, "Ship model v2, keep v1 as a fallback"),
    ("Monitor", 32.0, "Back to watching: the loop never ends"),
]


def piecewise(knots, t):
    """Linear interpolation through (t, value) knots, clamped at both ends."""
    if t <= knots[0][0]:
        return knots[0][1]
    for (t0, v0), (t1, v1) in zip(knots, knots[1:]):
        if t <= t1:
            return lerp(v0, v1, clamp01((t - t0) / (t1 - t0)))
    return knots[-1][1]


def smooth(x):
    return ease_in_out_cubic(clamp01(x))


def f1_at(w):
    noise = 1.0 * math.sin(w * 1.7) + 0.6 * math.sin(w * 3.1 + 1)
    v1 = 87 + noise - 0.7 * clamp01((w - 12) / 6) * 6 - 1.35 * max(w - 18, 0)
    return lerp(v1, 87 + noise, smooth((w - DEPLOY_WEEK) / 1.5))  # v2 recovers


def live_visibility(w):
    return 7.2 - 2.8 * smooth((w - 10) / 12)


TRAIN_VISIBILITY = 7.2


def train_visibility(w):  # v2's training data includes the foggy weeks
    return lerp(TRAIN_VISIBILITY, live_visibility(w), smooth((w - 27.5) / 3.5))


def real_centre(w):  # departures per hour at which delays become likely, in reality
    return 13 - 5 * smooth((w - 17) / 7)


MODEL_CENTRE = 13.0


def model_centre(w):  # v2 has learned the new rule
    return lerp(MODEL_CENTRE, real_centre(w), smooth((w - 29) / 2))


def axis_weeks(w):  # the F1 chart's time axis stretches once the story runs past week 27
    return max(AXIS_WEEKS, w + 3)


def stage_at(w):
    current = STAGES[0]
    for st in STAGES:
        if w >= st[1]:
            current = st
    return current


def monitor_pulse(t):
    """Ring pulse around the Monitor stage (animation 36's clock)."""
    return progress(t, 2.4, 0.8) * (0.55 + 0.45 * math.sin(2 * math.pi * (t - 2.4) / 1.6))


def p_delay(deps, centre):
    return 1 / (1 + math.exp(-(deps - centre) * 0.55))


# ---------------------------------------------------------------- left side

def draw_pipeline(sc, T, a, w, model_box=True):
    x0, y0, x1, y1 = MODEL_BOX
    if model_box:
        sc.box(MODEL_BOX, a, 0.6, 0.14)
    version = "v2" if w >= DEPLOY_WEEK else "v1"
    sc.text((x0 + x1) / 2, 1.9, f"MODEL {version}", 1.8, INK, a, True)
    sc.text((x0 + x1) / 2, 4.3, "in production", 0.95, MUTED, a)
    training = a * clamp01((w - 27.1) * 2) * (1 - clamp01((w - DEPLOY_WEEK) * 2))
    sc.text((x0 + x1) / 2, 6.4, "v2 being trained...", 0.9, SHARE_RED, training, True)
    flash = a * math.sin(math.pi * clamp01((w - DEPLOY_WEEK) / 1.2))
    sc.box((x0 - 0.4, y0 - 0.4, x1 + 0.4, y1 + 0.4), flash, 0.9, 0.3, SHARE_RED)
    sc.text(6.0, -1.6, "LIVE FLIGHTS", 1.05, INK, a, True)
    sc.text(6.0, 7.9, "a test set that never stops", 0.85, MUTED, a)
    sc.text(38.5, -1.6, "PREDICTIONS", 1.05, INK, a, True)
    sc.text(38.5, 7.9, "delayed or on time", 0.85, MUTED, a)
    if T < STREAM_START:
        return
    k_max = int((T - STREAM_START) / 0.13)
    for k in range(max(0, k_max - 30), k_max + 1):
        s = STREAM_START + k * 0.13
        lane = 3.0 + ((k * 7) % 3 - 1) * 1.5
        half = 0.42
        u = (T - s) / 1.4
        if 0 <= u <= 1:
            x = lerp(-1.0, x0 - 0.6, u)
            sc.tile(MUTED, (x - half, lane - half, x + half, lane + half),
                    a * min(1, u * 5, (1 - u) * 8))
        v = (T - s - 1.65) / 1.3
        if 0 <= v <= 1:
            delayed = (k * 2654435761 % 100) < (38 if w < 18 else 52)
            x = lerp(x1 + 0.6, 46.5, v)
            sc.tile(RED if delayed else GREEN, (x - half, lane - half, x + half, lane + half),
                    a * min(1, v * 8, (1 - v) * 3))


def draw_loop(sc, a, w):
    cx, cy, rx, ry = 23.0, 28.6, 17.0, 9.5
    active = stage_at(w)[0] if w >= 0 else "Deploy"
    angles = [-90 + 60 * k for k in range(len(LOOP))]
    for k in range(len(LOOP)):  # arcs with arrowheads, clockwise
        a0, a1 = math.radians(angles[k] + 20), math.radians(angles[k] + 40)
        pts = [(cx + rx * math.cos(lerp(a0, a1, j / 8)), cy + ry * math.sin(lerp(a0, a1, j / 8)))
               for j in range(9)]
        for p, q in zip(pts, pts[1:]):
            sc.line(*p, *q, a, 0.12)
        (px, py), (qx, qy) = pts[-2], pts[-1]
        d = math.hypot(qx - px, qy - py)
        ux, uy = (qx - px) / d, (qy - py) / d
        for side in (1, -1):
            sc.line(qx, qy, qx - 0.8 * ux + side * 0.55 * uy, qy - 0.8 * uy - side * 0.55 * ux,
                    a, 0.12)
    for k, name in enumerate(LOOP):
        ang = math.radians(angles[k])
        h = 1.0 if name == active else 0.0
        sc.pill(cx + rx * math.cos(ang), cy + ry * math.sin(ang), name, 1.0, a,
                mix(HEADER_BG, SHARE_RED, h), mix(INK, WHITE, h))
    caption = stage_at(w)[2] if w >= 0 else "Model v1 goes live"
    sc.text(cx, cy - 0.7, "MLOPS LOOP", 1.1, MUTED, a, True)
    sc.text(cx, cy + 0.9, caption, 0.85, INK, a)


# ---------------------------------------------------------------- dashboard

CHART_RECTS = {"f1": (51.8, -3.6, 99.8, 10.8), "data": (51.8, 12.9, 99.8, 27.3),
               "concept": (51.8, 29.0, 99.8, 42.9)}


def _plot_frame(sc, a, top, title, note=None):
    sc.text(52.5, top, title, 1.05, INK, a, True, "lm")
    if note:
        sc.text(99.0, top, note[0], 0.9, note[1], a, True, "rm")


def _why(sc, a, w, y, why):
    start, text = why
    sc.text(52.5, y, text, 0.85, SHARE_RED, a * clamp01((w - start) / 1.5), True, "lm")


def draw_f1_chart(sc, a, w):
    x0, x1, y0, y1 = 55.0, 98.5, -0.2, 9.4
    f1 = f1_at(max(w, 0))
    low = w >= 0 and f1 < 75
    _plot_frame(sc, a, -2.4, "LIVE F1 SCORE  ·  true outcomes arrive after each flight",
                (f"F1  {f1:.0f}%", SHARE_RED if low else GREEN_DARK) if w >= 0 else None)
    px = lambda wk: lerp(x0, x1, wk / axis_weeks(w))
    py = lambda v: lerp(y1, y0, (v - 50) / 50)
    sc.line(x0, y1, x1, y1, a, 0.08)
    sc.line(x0, y0, x0, y1, a, 0.08)
    for v in (50, 75, 100):
        sc.text(x0 - 0.4, py(v), f"{v}%", 0.75, MUTED, a, False, "rm")
    sc.line(x0, py(75), x1, py(75), a * 0.8, 0.07, dashed=True)
    sc.text(x1, py(75) + 0.7, "alert threshold", 0.75, SHARE_RED, a, False, "rm")
    for wk, label in [(0, "v1 live"), (DEPLOY_WEEK, "v2 live")]:
        if w >= wk:
            sc.line(px(wk), y0, px(wk), y1, a * 0.7, 0.06, dashed=True)
            sc.text(px(wk) + 0.3, y0 + 0.2, label, 0.75, MUTED, a, True, "lm")
    if w > 0:
        steps = max(2, int(w * 3))
        pts = [(px(w * j / steps), py(f1_at(w * j / steps))) for j in range(steps + 1)]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            sc.line(ax, ay, bx, by, a, 0.16)
    sc.pill(x1 - 9.0, 7.2, "ALERT: F1 dropped below 75%", 0.95,
            a * clamp01((w - ALERT_WEEK) * 5) * (1 - clamp01((w - DEPLOY_WEEK - 0.8) * 2)),
            SHARE_RED, WHITE)


def draw_data_chart(sc, a, w):
    x0, x1, y0, y1 = 55.0, 98.5, 16.3, 25.6
    gap = abs(live_visibility(w) - train_visibility(w)) if w >= 0 else 0
    status = ("no drift", GREEN_DARK) if gap < 0.7 else (
        ("drifting", SHARE_RED) if gap < 1.8 else ("DRIFT: HIGH", SHARE_RED))
    _plot_frame(sc, a, 14.1, "DATA DRIFT  ·  visibility (km) of the flights", status)
    _why(sc, a, w, 15.35, DATA_WHY)
    sc.line(x0, y1, x1, y1, a, 0.08)
    px = lambda v: lerp(x0, x1, v / 11)
    for v in (0, 5, 10):
        sc.text(px(v), y1 + 0.8, str(v), 0.75, MUTED, a)
    for mu, col, fill in [(train_visibility(max(w, 0)), INK, True),
                          (live_visibility(max(w, 0)), SHARE_RED, False)]:
        dens = lambda v: math.exp(-0.5 * ((v - mu) / 1.9) ** 2)
        xs = [11 * j / 60 for j in range(61)]
        if fill:
            for xa, xb in zip(xs, xs[1:]):
                top = lerp(y1, y0 + 0.6, dens((xa + xb) / 2))
                sc.tile(HEADER_BG, (px(xa), top, px(xb) + 0.03, y1), a, 0.0)
        for xa, xb in zip(xs, xs[1:]):
            sc.line(px(xa), lerp(y1, y0 + 0.6, dens(xa)), px(xb), lerp(y1, y0 + 0.6, dens(xb)),
                    a, 0.14, color=col)
    sc.text(x0 + 0.6, y0 + 0.6, "filled: training data", 0.75, INK, a, False, "lm")
    sc.text(x0 + 0.6, y0 + 1.8, "red: live data this week", 0.75, SHARE_RED, a, True, "lm")


def draw_concept_chart(sc, a, w, marker=0.0):
    x0, x1, y0, y1 = 55.0, 98.5, 32.4, 41.6
    cgap = abs(real_centre(w) - model_centre(w)) if w >= 0 else 0
    status = ("stable", GREEN_DARK) if cgap < 1 else ("CONCEPT DRIFT", SHARE_RED)
    _plot_frame(sc, a, 30.2, "CONCEPT DRIFT  ·  P(delay) vs departures per hour", status)
    _why(sc, a, w, 31.45, CONCEPT_WHY)
    sc.line(x0, y1, x1, y1, a, 0.08)
    sc.line(x0, y0, x0, y1, a, 0.08)
    px = lambda v: lerp(x0, x1, v / 25)
    py = lambda p: lerp(y1, y0 + 0.4, p)
    for v in (0, 10, 20):
        sc.text(px(v), y1 + 0.8, str(v), 0.75, MUTED, a)
    for centre, col, label, dy in [(model_centre(max(w, 0)), INK, "what the model believes", 0),
                                   (real_centre(max(w, 0)), SHARE_RED, "what really happens", 1)]:
        xs = [25 * j / 50 for j in range(51)]
        for xa, xb in zip(xs, xs[1:]):
            sc.line(px(xa), py(p_delay(xa, centre)), px(xb), py(p_delay(xb, centre)), a, 0.14,
                    color=col)
        sc.text(x0 + 0.6, y0 + 0.7 + dy * 1.2, label, 0.75, col, a, dy == 1, "lm")
    if marker > 0:  # the example: an hour with 9 departures
        mx = px(EXAMPLE_DEPS)
        sc.line(mx, y0 - 0.2, mx, y1, a * marker, 0.07, dashed=True)
        sc.text(mx, y1 + 0.8, f"{EXAMPLE_DEPS}", 0.8, SHARE_RED, a * marker, True)
        for centre, col in [(MODEL_CENTRE, INK), (real_centre(max(w, 0)), SHARE_RED)]:
            y = py(p_delay(EXAMPLE_DEPS, centre))
            sc.tile(col, (mx - 0.35, y - 0.35, mx + 0.35, y + 0.35), a * marker, 0.35)


def draw_ops(sc, T, w, left_a=1.0, f1_a=1.0, data_a=1.0, concept_a=1.0, marker=0.0,
             highlights=(), panels_a=1.0, title_a=1.0, model_box=True, pulse=0.0):
    """Everything on the monitoring slide. highlights: [(chart name, outline opacity)];
    pulse: opacity of a ring around the Monitor stage of the loop."""
    draw_pipeline(sc, T, left_a * panels_a, w, model_box)
    draw_loop(sc, left_a * panels_a, w)
    sc.box((51.0, -4.4, 100.6, 43.4), panels_a, 0.8, 0.12)
    draw_f1_chart(sc, f1_a * panels_a, w)
    draw_data_chart(sc, data_a * panels_a, w)
    draw_concept_chart(sc, concept_a * panels_a, w, marker)
    for name, a in highlights:
        sc.box(CHART_RECTS[name], a, 0.6, 0.3, SHARE_RED)
    sc.box((19.9, 17.7, 26.1, 20.5), pulse * left_a * panels_a, 1.4, 0.22, SHARE_RED)
    sc.text(50.0, -9.0, TITLE[0], 2.2, INK, title_a, True)
    sc.text(50.0, -6.6, TITLE[1], 1.15, MUTED, title_a)
    if w >= 0:
        sc.text(100.5, -9.0, f"WEEK {int(w) + 1} IN PRODUCTION", 1.2, INK, panels_a, True, "rm")


def highlight_in(t, t_in):
    """(explainer, dim) opacities as a highlight comes in: the other charts dim and the left side
    hands over to the explainer."""
    return progress(t, t_in + 0.6, 0.6), progress(t, t_in, 0.6)


def highlight_out(t, t_out):
    """(explainer, dim) opacities as a highlight clears: the explainer fades, then the left side
    and the other charts come back."""
    return 1 - progress(t, t_out, 0.5), 1 - progress(t, t_out + 0.5, 0.6)


# ---------------------------------------------------------------- explainers (left side)

CLEAR, FOG = (147, 197, 253), (156, 163, 175)
TRAIN_FOG = {3, 11, 16}
WINTER_FOG = [1, 5, 7, 8, 9, 13, 14, 17, 18, 19]  # flip to fog one by one (13 of 20 in total)


def _day_row(sc, y, fog_amounts, a):
    for k in range(20):
        x = 1.5 + k * 2.15
        f = fog_amounts[k]
        squash = 1 - 0.8 * math.sin(math.pi * f) if 0 < f < 1 else 1  # a little flip
        sc.tile(mix(CLEAR, FOG, f), (x, y + 1.0 - squash, x + 1.8, y + 1.0 + squash), a, 0.3)


def draw_data_explainer(sc, t, a):
    """t is the explainer's own clock (0 when it starts); a is its overall opacity."""
    sc.text(1.5, -2.2, "DATA DRIFT: THE INPUTS CHANGED", 1.45, SHARE_RED, a, True, "lm")
    sc.text(1.5, -0.3, "Example: winter fog", 1.0, MUTED, a * progress(t, 0.2, 0.5), False, "lm")
    row1 = a * progress(t, 0.8, 0.5)
    sc.text(1.5, 2.0, "LAST YEAR  ·  training data", 0.95, INK, row1, True, "lm")
    sc.text(44.5, 2.0, "3 of 20 days foggy  ·  avg 7.2 km", 0.95, INK, row1, True, "rm")
    _day_row(sc, 3.0, [1.0 if k in TRAIN_FOG else 0.0 for k in range(20)], row1)
    sc.text(1.5, 5.9, "one tile = one day     light blue: clear     grey: fog, low visibility",
            0.78, MUTED, row1, False, "lm")
    row2 = a * progress(t, 1.8, 0.5)
    flips = [progress(t, 2.8 + 0.4 * j, 0.35, clamp01) for j in range(len(WINTER_FOG))]
    fog = [1.0 if k in TRAIN_FOG else 0.0 for k in range(20)]
    for j, k in enumerate(WINTER_FOG):
        fog[k] = flips[j]
    n_fog = len(TRAIN_FOG) + sum(1 for f in flips if f >= 0.5)
    vis = lerp(7.2, 4.4, sum(flips) / len(flips))
    sc.text(1.5, 8.3, "THIS WINTER  ·  live flights", 0.95, SHARE_RED, row2, True, "lm")
    sc.text(44.5, 8.3, f"{n_fog} of 20 days foggy  ·  avg {vis:.1f} km", 0.95, SHARE_RED, row2,
            True, "rm")
    _day_row(sc, 9.3, fog, row2)
    points = ["It learned mostly from clear-weather flights",
              "Now most flights look unlike what it was trained on",
              "Its predictions get less reliable: F1 slips"]
    sc.text(1.5, 14.4, "WHAT THIS DOES TO THE MODEL", 0.95, INK, a * progress(t, 7.3, 0.5),
            True, "lm")
    for j, line in enumerate(points):
        sc.text(1.5, 16.2 + j * 1.6, f"•  {line}", 1.0, INK, a * progress(t, 7.8 + 0.6 * j, 0.5),
                False, "lm")
    sc.pill(23.0, 22.4, "The rules didn't change, the inputs did", 1.1,
            a * progress(t, 9.8, 0.6), SHARE_RED, WHITE)


SLOTS, OPEN_SLOTS = 13, 8
SLOT_W, SLOT_PITCH, SLOT_Y = 2.6, 3.3, 3.4


def _slot_rect(k):
    x = 1.6 + k * SLOT_PITCH
    return (x, SLOT_Y, x + SLOT_W, SLOT_Y + 2.8)


def draw_concept_explainer(sc, t, a):
    """t is the explainer's own clock (0 when it starts); a is its overall opacity."""
    sc.text(1.5, -2.2, "CONCEPT DRIFT: THE RULE CHANGED", 1.45, SHARE_RED, a, True, "lm")
    sc.text(1.5, -0.3, "Example: a runway closes for works", 1.0, MUTED,
            a * progress(t, 0.2, 0.5), False, "lm")
    sc.text(1.5, 2.1, "AIRPORT CAPACITY  ·  departure slots per hour", 0.95, INK,
            a * progress(t, 0.8, 0.4), True, "lm")
    closing = [progress(t, 2.8 + 0.25 * j, 0.3) for j in range(SLOTS - OPEN_SLOTS)]
    for k in range(SLOTS):
        r = _slot_rect(k)
        closed = closing[k - OPEN_SLOTS] if k >= OPEN_SLOTS else 0.0
        sc.tile(mix(HEADER_BG, RED_TINT, closed), r, a * progress(t, 0.8 + 0.05 * k, 0.3), 0.3)
        if closed > 0:
            sc.line(r[0] + 0.5, r[1] + 0.5, r[2] - 0.5, r[3] - 0.5, a * closed, 0.12,
                    color=SHARE_RED)
            sc.line(r[0] + 0.5, r[3] - 0.5, r[2] - 0.5, r[1] + 0.5, a * closed, 0.12,
                    color=SHARE_RED)
    sc.text(1.5, 7.3, "Before: 2 runways, room for 13 departures an hour", 1.0, INK,
            a * progress(t, 1.6, 0.4) * (1 - progress(t, 2.6, 0.3)), False, "lm")
    sc.text(1.5, 7.3, "Now: runway 2 closed for works, room for only 8", 1.0, SHARE_RED,
            a * progress(t, 4.3, 0.4), True, "lm")
    # a busy hour with 9 departures fills the slots; the 9th lands on a closed one
    sc.text(1.5, 9.4, f"A BUSY HOUR WITH {EXAMPLE_DEPS} DEPARTURES", 0.95, INK,
            a * progress(t, 5.2, 0.4), True, "lm")
    for k in range(EXAMPLE_DEPS):
        land = progress(t, 5.6 + 0.35 * k, 0.4, ease_in_out_cubic)
        if land <= 0:
            continue
        x0, y0, x1, y1 = _slot_rect(k)
        cx, cy = (x0 + x1) / 2, lerp(-3.0, (y0 + y1) / 2, land)
        last = k == EXAMPLE_DEPS - 1
        late = progress(t, 5.6 + 0.35 * EXAMPLE_DEPS + 0.3, 0.4) if last else 0.0
        sc.tile(mix(GREEN, RED, late), (cx - 0.8, cy - 0.8, cx + 0.8, cy + 0.8),
                a * min(1, land * 3), 0.25)
    sc.text(1.5, 11.0, f"Before: {EXAMPLE_DEPS} departures fit easily.   Now: the "
            f"{EXAMPLE_DEPS}th has no slot, so it waits: delayed", 0.9, INK,
            a * progress(t, 9.4, 0.5), False, "lm")
    cards = a * progress(t, 10.4, 0.5)
    pm = 100 * p_delay(EXAMPLE_DEPS, MODEL_CENTRE)
    pr = 100 * p_delay(EXAMPLE_DEPS, real_centre(PAUSE_WEEK))
    for k, (head, big, small, bg, hc) in enumerate([
            ("SAME INPUT", f"{EXAMPLE_DEPS} departures/hour", "looks just like training",
             HEADER_BG, MUTED),
            ("MODEL BELIEVES", f"{pm:.0f}% delay risk", "learned before the closure",
             HEADER_BG, MUTED),
            ("REALITY NOW", f"{pr:.0f}% delay risk", "runway 2 closed", RED_TINT, SHARE_RED)]):
        x0 = 1.5 + k * 14.6
        sc.tile(bg, (x0, 12.6, x0 + 13.8, 17.8), cards, 0.5)
        sc.text(x0 + 6.9, 13.6, head, 0.75, hc, cards, True)
        sc.text(x0 + 6.9, 15.15, big, 1.15, INK, cards, True)
        sc.text(x0 + 6.9, 16.6, small, 0.78, MUTED, cards)
    sc.pill(23.0, 20.2, "Same inputs, different outcome: the model is confidently wrong", 1.0,
            a * progress(t, 12.0, 0.6), SHARE_RED, WHITE)
