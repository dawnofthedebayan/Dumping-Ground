"""Shared data, scene layout, renderer and 4K GIF encoder for the aircraft delay animations.

The scene is one table of 100 aircraft laid out as 4 panels of 25 rows. The "sample of 10" view is
the camera framed on the first 10 rows of panel 1 (all other rows hidden); the "sample of 100" view
is the camera pulled back to show every panel. In the same scene coordinates sits a wind-speed
chart: each table row can morph into a dot on the wind-speed axis, a decision boundary can be drawn
across it, and each dot can be marked right or wrong by the rule. Because every animation renders
this one scene, the last frame of each GIF matches the first frame of the next.

Every frame is drawn as vectors at 2x supersampling and downsampled to 3840x2160, so text and
edges stay crisp at every zoom level. Frames are then encoded with ffmpeg's two-pass palette
(palettegen + paletteuse) for a high quality GIF.
"""

import argparse
import math
import os
import random
import shutil
import subprocess
import tempfile
from multiprocessing import Pool
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent

OUT_W, OUT_H = 3840, 2160

# Colours
WHITE = (255, 255, 255)
RED = (229, 72, 77)
GREEN = (38, 162, 105)
RED_TINT = (253, 236, 237)
GREEN_TINT = (232, 246, 238)
RED_DARK = (185, 36, 45)
GREEN_DARK = (20, 115, 72)
HEADER_BG = (240, 242, 245)
HEADER_FG = (31, 41, 55)
INK = (31, 41, 55)
MUTED = (107, 114, 128)
ROW_FG = WHITE

# Table geometry, in scene units (1 unit = one row pitch)
N_ROWS = 100
N_SAMPLE = 10
PANELS = 4
ROWS_PER_PANEL = N_ROWS // PANELS
COLS = [("MSN", 3.3), ("WIND SPEED (KT)", 4.4), ("DELAYED", 3.3)]
PANEL_W = sum(w for _, w in COLS)
PANEL_GAP = 1.1
HEADER_H = 1.15
HEADER_FILL = 0.92
ROW_FILL = 0.84
RADIUS = 0.2
ROW_TEXT = 0.40
HEADER_TEXT = 0.30
ENTER_DROP = 0.35  # rows slide this far (units) while fading in/out
INSET = 0.06

SCENE_W = PANELS * PANEL_W + (PANELS - 1) * PANEL_GAP
SCENE_H = HEADER_H + ROWS_PER_PANEL

# Every column the table can show: key -> (header, width). BASE_COLS are always present; the rest
# are opened by a state's "cols" progress (animation 8). The last two are deliberately irrelevant
# to delays (distractor features).
COLUMNS = {
    "msn": ("MSN", 3.3),
    "model": ("AIRCRAFT MODEL", 3.8),
    "sched": ("SCHED. DEPARTURE", 4.0),
    "day": ("DAY OF WEEK", 3.3),
    "wind": ("WIND SPEED (KT)", 4.4),
    "vis": ("VISIBILITY (KM)", 3.9),
    "bad": ("BAD WEATHER", 3.9),  # engineered from wind + visibility (animation 10)
    "deps": ("DEPARTURES SAME HOUR", 5.1),
    "livery": ("LIVERY COLOR", 3.5),
    "magazine": ("MAGAZINE ISSUE", 3.8),
    "delayed": ("DELAYED", 3.3),
}
COLUMN_ORDER = ["msn", "model", "sched", "day", "wind", "vis", "bad", "deps", "livery",
                "magazine", "delayed"]
BASE_COLS = ("msn", "wind", "delayed")

# Chart geometry (same scene units, framed by the 100-row camera)
AXIS_MAX = 55.0  # kt
AXIS_X0, AXIS_X1 = 3.0, SCENE_W - 3.0
AXIS_Y = 22.0
DOT_D = 0.9
DOT_STEP = DOT_D * 1.08
DOT_GAP = 0.28  # space between the axis and the first dot
THRESHOLD = 25.0  # kt: the decision rule is "wind speed > THRESHOLD -> delayed"
BOUND_TOP = 6.2


# ---------------------------------------------------------------- data

DATA_SEED = 880  # chosen so the 25 kt rule scores exactly 60 / 100 (see make_data)


def make_data(seed=DATA_SEED):
    """100 aircraft; strong wind makes a delay likelier, but only weakly (plenty of other causes).

    With seed 880 the rule "wind > 25 kt -> delayed" is right for exactly 60 of the 100 aircraft;
    no other cut-off does better than 62, and always predicting "on time" scores 57.
    """
    rng = random.Random(seed)
    msns = rng.sample(range(10000, 12000), N_ROWS)
    rows = []
    for msn in msns:
        wind = min(round(rng.gammavariate(4.0, 5.0), 1), AXIS_MAX)
        p_delay = 0.2 + 0.45 / (1 + math.exp(-(wind - THRESHOLD) / 3))
        rows.append((msn, wind, rng.random() < p_delay))
    # Make sure the sample of 10 shows a healthy mix of both colours.
    while not 3 <= sum(d for _, _, d in rows[:N_SAMPLE]) <= 6:
        rng.shuffle(rows)
    return rows


DATA = make_data()
CORRECT = [(wind > THRESHOLD) == delayed for _, wind, delayed in DATA]


DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MODELS = ["A319", "A320", "A320neo", "A321", "A321neo"]
BAD_VIS = 3.0  # km: engineered feature "bad weather = wind > THRESHOLD or visibility < BAD_VIS"


def make_extra_features(seed=17):
    """The extra columns for each aircraft, as display strings.

    Visibility, departure hour, day and airport congestion lean towards the delay label (so a model
    can learn from them); aircraft model is near-neutral; livery color and magazine issue are pure
    noise. Uses its own RNG so the original wind/delay data stays unchanged.
    """
    rng = random.Random(seed)
    hours = list(range(6, 23))
    out = []
    for _, _, delayed in DATA:
        vis = min(10.0, max(0.3, rng.gauss(4.2 if delayed else 7.2, 2.3)))
        peak = [2.2 if (delayed and 16 <= h <= 20) else 1.0 for h in hours]
        day_w = [1.0, 0.9, 0.9, 1.1, 1.7, 1.0, 1.5] if delayed else [1.0] * 7
        deps = max(2, round(rng.gauss(15 if delayed else 9, 4)))
        out.append({
            "vis": f"{vis:.1f}",
            "sched": f"{rng.choices(hours, peak)[0]:02d}:{rng.choice(range(0, 60, 5)):02d}",
            "day": rng.choices(DAYS, day_w)[0],
            "deps": str(deps),
            "model": rng.choice(MODELS),
            "livery": rng.choice(["White", "Navy", "Silver", "Gold", "Teal"]),
            "magazine": f"#{rng.randint(101, 148)}",
        })
    for (_, wind, _), e in zip(DATA, out):
        e["bad"] = "True" if wind > THRESHOLD or float(e["vis"]) < BAD_VIS else "False"
    return out


EXTRA = make_extra_features()


def cell_text(i, key):
    msn, wind, delayed = DATA[i]
    if key == "msn":
        return str(msn)
    if key == "wind":
        return f"{wind:.1f}"
    if key == "delayed":
        return "True" if delayed else "False"
    return EXTRA[i][key]


# Feature encoding (animation 11): new header, the mapping shown above the column, encoded value.
ENCODED_HEADERS = {"model": "MODEL CODE", "sched": "DEPARTURE HOUR", "day": "DAY (MON = 0)"}
ENCODE_NOTES = {
    "model": "A319 = 0  ·  A320 = 1  ·  A320neo = 2  ·  A321 = 3  ·  A321neo = 4",
    "sched": "Time as hours:  hour + minutes / 60   (22:20 = 22.33)",
    "day": "Mon = 0  ·  Tue = 1  ·  Wed = 2  ·  ...  ·  Sun = 6",
    "bad": "True = 1  ·  False = 0",
    "delayed": "Label:  True = 1  ·  False = 0",
}


def encoded_text(i, key):
    v = cell_text(i, key)
    if key == "model":
        return str(MODELS.index(v))
    if key == "sched":
        h, m = map(int, v.split(":"))
        return f"{h + m / 60:.2f}"
    if key == "day":
        return str(DAYS.index(v))
    if key in ("bad", "delayed"):
        return "1" if v == "True" else "0"
    return v


# ---------------------------------------------------------------- layout

def panel_x(p, pw=PANEL_W):
    return p * (pw + PANEL_GAP)


def row_origin(i, pw=PANEL_W):
    """Top-left of row i in scene units."""
    p, r = divmod(i, ROWS_PER_PANEL)
    return panel_x(p, pw), HEADER_H + r


def col_layout(cols):
    """[(key, header, current width, open progress)] for the columns visible under `cols`."""
    out = []
    for key in COLUMN_ORDER:
        p = 1.0 if key in BASE_COLS else cols.get(key, 0.0)
        if p > 0:
            header, w = COLUMNS[key]
            out.append((key, header, w * ease_in_out_cubic(p / 0.5), p))
    return out


def table_width(cols):
    return sum(w for _, _, w, _ in col_layout(cols))


def axis_x(wind):
    return AXIS_X0 + wind / AXIS_MAX * (AXIS_X1 - AXIS_X0)


def _dot_layout():
    """Stack dots above the axis at their wind speed (a dot plot); returns centres and x order."""
    order = sorted(range(N_ROWS), key=lambda i: DATA[i][1])
    placed, pos = [], [None] * N_ROWS
    for i in order:
        x, lvl = axis_x(DATA[i][1]), 0
        while any(l == lvl and abs(px - x) < DOT_STEP for px, l in placed):
            lvl += 1
        placed.append((x, lvl))
        pos[i] = (x, AXIS_Y - DOT_GAP - DOT_D / 2 - lvl * DOT_STEP)
    return pos, order


DOT_POS, X_ORDER = _dot_layout()
BOUND_X = axis_x(THRESHOLD)
SAMPLE_CENTER = (PANEL_W / 2, (HEADER_H + N_SAMPLE) / 2)


def fit_scale(w, h, margin):
    return min(OUT_W * (1 - margin) / w, OUT_H * (1 - margin) / h)


# Cameras: (centre x, centre y, pixels per unit at 3840 wide)
CAM_10 = (*SAMPLE_CENTER, fit_scale(PANEL_W, HEADER_H + N_SAMPLE, 0.16))
CAM_100 = (SCENE_W / 2, SCENE_H / 2, fit_scale(SCENE_W, SCENE_H, 0.07))


def table_camera(cols):
    """Camera on the 10-row sample, easing out as extra columns widen the table."""
    width = table_width(cols)
    return (width / 2, CAM_10[1], min(CAM_10[2], fit_scale(width, HEADER_H + N_SAMPLE, 0.08)))


def sample_table_state(cols, **overrides):
    """State showing only the 10-row sample table with the given extra columns."""
    s = dict(camera=table_camera(cols), header_alpha=[1.0] + [0.0] * (PANELS - 1),
             row_alpha=[1.0 if i < N_SAMPLE else 0.0 for i in range(N_ROWS)], cols=cols)
    s.update(overrides)
    return s


def lerp_camera(a, b, t):
    """Zoom geometrically (constant perceived speed) while panning linearly."""
    return (
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t,
        math.exp(math.log(a[2]) + (math.log(b[2]) - math.log(a[2])) * t),
    )


def wave_order():
    """0..1 distance of every non-sample element from the sample block (0 = nearest).

    Returns (header_dist[PANELS], row_dist[N_ROWS]); sample rows and panel 1's header get 0.
    """
    def dist(x, y):
        return math.hypot(x - SAMPLE_CENTER[0], y - SAMPLE_CENTER[1])

    hd = [dist(panel_x(p) + PANEL_W / 2, HEADER_H / 2) if p else 0.0 for p in range(PANELS)]
    rd = []
    for i in range(N_ROWS):
        x, y = row_origin(i)
        rd.append(dist(x + PANEL_W / 2, y + 0.5) if i >= N_SAMPLE else 0.0)
    m = max(hd + rd)
    return [d / m for d in hd], [d / m for d in rd]


# ---------------------------------------------------------------- easing

def clamp01(x):
    return max(0.0, min(1.0, x))


def ease_out_cubic(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in_out_cubic(x):
    x = clamp01(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out_back(x):
    x = clamp01(x)
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def progress(t, start, dur, ease=ease_out_cubic):
    return ease((t - start) / dur)


def lerp(a, b, t):
    return a + (b - a) * t


# ---------------------------------------------------------------- fonts

def _find_font_files():
    """Montserrat if available (drop the TTFs in ./fonts or install them), else Avenir Next."""
    search = [HERE / "fonts", Path.home() / "Library/Fonts", Path("/Library/Fonts")]
    found = {}
    for d in search:
        for weight in ("Medium", "SemiBold"):
            for ext in ("ttf", "otf"):
                f = d / f"Montserrat-{weight}.{ext}"
                if f.exists() and weight not in found:
                    found[weight] = (str(f), 0)
    if len(found) == 2:
        return found["Medium"], found["SemiBold"], "Montserrat"
    avenir = "/System/Library/Fonts/Avenir Next.ttc"
    if os.path.exists(avenir):
        return (avenir, 5), (avenir, 2), "Avenir Next"  # Medium, Demi Bold
    raise SystemExit("No Montserrat or Avenir Next found - put Montserrat-Medium.ttf and "
                     "Montserrat-SemiBold.ttf in table_animation/fonts/")


FONT_MEDIUM, FONT_BOLD, FONT_NAME = _find_font_files()
_font_cache = {}


def font(spec, size):
    size = max(1.0, round(size * 4) / 4)  # quarter-pixel steps: smooth zoom, bounded cache
    key = (spec, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(spec[0], size, index=spec[1])
    return _font_cache[key]


# ---------------------------------------------------------------- rendering

def mix(c1, c2, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(c1, c2))


def blend(c, a, bg=WHITE):
    """Colour c at opacity a over bg (white by default)."""
    return mix(bg, c, a)


def default_state():
    return dict(
        camera=CAM_100,
        header_alpha=[0.0] * PANELS,
        row_alpha=[0.0] * N_ROWS,
        shrink=[0.0] * N_ROWS,   # 0 = table row, 1 = dot-sized circle
        fly=[0.0] * N_ROWS,      # 0 = at its table position, 1 = at its place on the chart
        verdict=[0.0] * N_ROWS,  # 0..1 reveal of the right/wrong mark from the rule
        axis=0.0, axis_title=0.0, legend=0.0,
        boundary=0.0, rule=0.0, region=0.0, region_label=0.0,
        score=0.0, final=0.0,
        marks=1.0,               # opacity of the verdict ticks/crosses (fade them without a pop)
        cols={},                 # extra column key -> 0..1 (0-0.5 opens its width, then text)
        col_dim={},              # column key -> 0..1 greys out its text
        col_box=[],              # [(column keys, alpha)]: outline drawn around those columns
        notes=[],                # [(text, column keys, alpha)]: dark label above those columns
        encode={},               # column key -> 0..1: cells flip to their numeric encoding
        caption=("", 0.0),       # (text, alpha): label under the 10-row table
        row_text=1.0,            # opacity of all table text (cells and headers)
        tiles=[],                # [(color, x0, y0, x1, y1, radius, alpha)] free rounded tiles
        boxes=[],                # [(x0, y0, x1, y1, radius, alpha, width)] ink outlines
        lines=[],                # [(x0, y0, x1, y1, width, alpha, dashed)] ink lines
        texts=[],                # [(x, y, text, size, color, alpha, bold, anchor)]
        pills=[],                # [(x, y, text, size, alpha)] dark rounded labels
    )


def chart_state(**overrides):
    """State with every row sitting as a dot on the finished axis (end of animation 4)."""
    s = default_state()
    s.update(row_alpha=[1.0] * N_ROWS, shrink=[1.0] * N_ROWS, fly=[1.0] * N_ROWS,
             axis=1.0, axis_title=1.0, legend=1.0)
    s.update(overrides)
    return s


class Canvas:
    def __init__(self, camera, width, height, ss):
        self.W, self.H = width * ss, height * ss
        self.cx, self.cy, s = camera
        self.s = s * width / OUT_W * ss
        self.img = Image.new("RGB", (self.W, self.H), WHITE)
        self.d = ImageDraw.Draw(self.img)

    def X(self, u):
        return self.W / 2 + (u - self.cx) * self.s

    def Y(self, v):
        return self.H / 2 + (v - self.cy) * self.s

    def box(self, x0, y0, x1, y1):
        return (self.X(x0), self.Y(y0), self.X(x1), self.Y(y1))

    def visible(self, x0, y0, x1, y1):
        return x1 > 0 and y1 > 0 and x0 < self.W and y0 < self.H

    def rrect(self, x0, y0, x1, y1, r, fill):
        b = self.box(x0, y0, x1, y1)
        if not (self.visible(*b) and b[2] > b[0] and b[3] > b[1]):
            return
        w, h = b[2] - b[0], b[3] - b[1]
        r = min(r * self.s, w / 2, h / 2)
        if r >= min(w, h) / 2 - 0.5:
            # Full pill / circle: Pillow's rounded_rectangle can leave a 1px seam here.
            d = min(w, h)
            if w >= h:
                self.d.ellipse((b[0], b[1], b[0] + d, b[3]), fill=fill)
                self.d.ellipse((b[2] - d, b[1], b[2], b[3]), fill=fill)
                self.d.rectangle((b[0] + d / 2, b[1], b[2] - d / 2, b[3]), fill=fill)
            else:
                self.d.ellipse((b[0], b[1], b[2], b[1] + d), fill=fill)
                self.d.ellipse((b[0], b[3] - d, b[2], b[3]), fill=fill)
                self.d.rectangle((b[0], b[1] + d / 2, b[2], b[3] - d / 2), fill=fill)
            return
        self.d.rounded_rectangle(b, r, fill=fill)

    def circle(self, x, y, r, fill=None, outline=None, width=0.0):
        self.d.ellipse(self.box(x - r, y - r, x + r, y + r), fill=fill, outline=outline,
                       width=max(1, round(width * self.s)) if outline else 0)

    def line(self, pts, fill, width):
        self.d.line([(self.X(x), self.Y(y)) for x, y in pts], fill=fill,
                    width=max(1, round(width * self.s)), joint="curve")

    def text(self, x, y, s, spec, size, fill, anchor="mm"):
        self.d.text((self.X(x), self.Y(y)), s, font=font(spec, size * self.s), fill=fill,
                    anchor=anchor)

    def text_w(self, s, spec, size):
        """Text width in scene units."""
        return font(spec, size * self.s).getlength(s) / self.s

    def rrect_outline(self, x0, y0, x1, y1, r, color, width):
        self.d.rounded_rectangle(self.box(x0, y0, x1, y1), r * self.s, outline=color,
                                 width=max(1, round(width * self.s)))

    def pill(self, x, y, s, spec, size, fg, bg, a, scale=1.0, pad=0.55, align="m"):
        """Rounded label centred (align m), left-anchored (l) or right-anchored (r) at x."""
        size *= scale
        w = self.text_w(s, spec, size) + 2 * pad * scale
        h = size * 2.1
        x0 = {"m": x - w / 2, "l": x, "r": x - w}[align]
        self.rrect(x0, y - h / 2, x0 + w, y + h / 2, h / 2, blend(bg, a))
        self.text(x0 + w / 2, y, s, spec, size, blend(fg, a, bg=blend(bg, a)))


def _col_text_alpha(p, row=-1):
    """Text opacity of a column at open-progress p; rows reveal top to bottom after the header."""
    if p >= 1:
        return 1.0
    return clamp01((p - 0.42 - 0.035 * (row + 1)) / 0.2)


def _draw_table_headers(c, st, layout, pw):
    for p, a in enumerate(st["header_alpha"]):
        if a <= 0.004:
            continue
        x0, top = panel_x(p, pw), (HEADER_H - HEADER_FILL) / 2 + (1 - a) * ENTER_DROP
        c.rrect(x0 + INSET, top, x0 + pw - INSET, top + HEADER_FILL, RADIUS,
                blend(HEADER_BG, a))
        cxu = x0
        for key, name, w, cp in layout:
            ta = a * _col_text_alpha(cp)
            dim = (1 - 0.7 * st["col_dim"].get(key, 0.0)) * st["row_text"]
            if ta > 0.004:
                _flip_text(c, cxu + w / 2, top + HEADER_FILL / 2 - (1 - ta) * 0.2, name,
                           ENCODED_HEADERS.get(key, name), st["encode"].get(key, 0.0), FONT_BOLD,
                           HEADER_TEXT,
                           lambda k: blend(HEADER_FG, ta * dim * k, blend(HEADER_BG, a)))
            cxu += w


def _flip_text(c, x, y, old, new, e, spec, size, color):
    """Draw `old` rolling up and out while `new` rolls in from below (e: 0 -> 1)."""
    if old == new or e <= 0:
        c.text(x, y, old if e < 0.5 or old == new else new, spec, size, color(1.0))
        return
    if e < 0.5:
        c.text(x, y - e * 0.6, old, spec, size, color(1 - 2 * e))
    else:
        c.text(x, y + (1 - e) * 0.6, new, spec, size, color(2 * e - 1))


def _draw_rows(c, st, layout, pw):
    for i, a in enumerate(st["row_alpha"]):
        if a <= 0.004:
            continue
        msn, wind, delayed = DATA[i]
        s, f = st["shrink"][i], st["fly"][i]
        color = blend(RED if delayed else GREEN, a)
        if s <= 0 and f <= 0:
            x0, y0 = row_origin(i, pw)
            ty = y0 + 0.5 + (1 - a) * ENTER_DROP
            top = ty - ROW_FILL / 2
            if not c.visible(*c.box(x0 + INSET, top, x0 + pw - INSET, top + ROW_FILL)):
                continue
            c.rrect(x0 + INSET, top, x0 + pw - INSET, top + ROW_FILL, RADIUS, color)
            cxu, r = x0, i % ROWS_PER_PANEL
            for key, _, w, cp in layout:
                ta = _col_text_alpha(cp, r)
                dim = (1 - 0.7 * st["col_dim"].get(key, 0.0)) * st["row_text"]
                if ta > 0.004:
                    e = clamp01((st["encode"].get(key, 0.0) - 0.04 * r) / 0.6)
                    _flip_text(c, cxu + w / 2, ty - (1 - ta) * 0.2, cell_text(i, key),
                               encoded_text(i, key), e,
                               FONT_BOLD if key == "delayed" else FONT_MEDIUM, ROW_TEXT,
                               lambda k: mix(color, blend(ROW_FG, a), ta * dim * k))
                cxu += w
            continue

        x0, y0 = row_origin(i)
        tx, ty = x0 + PANEL_W / 2, y0 + 0.5 + (1 - a) * ENTER_DROP  # table-row centre

        # Morphing: the row's pill shrinks to a dot, then arcs over to its place on the chart.
        dx, dy = DOT_POS[i]
        cx = lerp(tx, dx, f)
        cy = lerp(ty, dy, f) - math.sin(math.pi * f) * 2.0
        w = lerp(PANEL_W - 2 * INSET, DOT_D, s)
        h = lerp(ROW_FILL, DOT_D, s)
        v = st["verdict"][i]
        pop = 1 + 0.35 * math.sin(math.pi * v)
        w, h = w * pop, h * pop
        c.rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, h / 2, color)
        text_a = 1 - clamp01(s * 3)
        if text_a > 0.01:
            cxu, scale = x0, lerp(1, 0.4, clamp01(s * 3))
            texts = [str(msn), f"{wind:.1f}", "True" if delayed else "False"]
            for text, (_, cw) in zip(texts, COLS):
                col_x = cx + (cxu + cw / 2 - tx) * (w / (PANEL_W - 2 * INSET))
                c.text(col_x, cy, text, FONT_MEDIUM, ROW_TEXT * scale, mix(color, ROW_FG, text_a))
                cxu += cw
        if v > 0.01 and st["marks"] > 0.004:
            _draw_verdict(c, cx, cy, DOT_D / 2 * pop, CORRECT[i], clamp01(v * 1.6) * st["marks"])


def _draw_verdict(c, x, y, r, correct, a):
    glyph = mix(RED if not correct else GREEN, WHITE, a)
    if correct:
        c.line([(x - 0.42 * r, y + 0.02 * r), (x - 0.12 * r, y + 0.32 * r),
                (x + 0.44 * r, y - 0.30 * r)], glyph, 0.2 * r)
    else:
        k = 0.34 * r
        c.line([(x - k, y - k), (x + k, y + k)], glyph, 0.2 * r)
        c.line([(x - k, y + k), (x + k, y - k)], glyph, 0.2 * r)
        c.circle(x, y, r + 0.13, outline=blend(INK, a), width=0.09)


def _draw_regions(c, st):
    p = st["region"]
    if p <= 0.004:
        return
    left, right = AXIS_X0 - 1.0, AXIS_X1 + 1.0
    c.rrect(lerp(BOUND_X, left, p), BOUND_TOP, BOUND_X, AXIS_Y, 0.25, blend(GREEN_TINT, p))
    c.rrect(BOUND_X, BOUND_TOP, lerp(BOUND_X, right, p), AXIS_Y, 0.25, blend(RED_TINT, p))


def _draw_boundary(c, st):
    p = st["boundary"]
    if p <= 0.004:
        return
    top = lerp(AXIS_Y, BOUND_TOP, p)
    y, dash, gap = AXIS_Y, 0.45, 0.28
    while y > top:
        c.line([(BOUND_X, y), (BOUND_X, max(top, y - dash))], INK, 0.09)
        y -= dash + gap
    c.circle(BOUND_X, top, 0.2, fill=INK)
    c.circle(BOUND_X, AXIS_Y, 0.2, fill=INK)


def _draw_axis(c, st):
    p = st["axis"]
    if p > 0.004:
        x_end = lerp(AXIS_X0 - 0.6, AXIS_X1 + 0.6, p)
        c.line([(AXIS_X0 - 0.6, AXIS_Y), (x_end, AXIS_Y)], INK, 0.07)
        for kt in range(0, int(AXIS_MAX) + 1, 5):
            tx = axis_x(kt)
            a = clamp01((x_end - tx) / 0.6)
            if a <= 0:
                continue
            major = kt % 10 == 0
            c.line([(tx, AXIS_Y), (tx, AXIS_Y + (0.32 if major else 0.2))], blend(INK, a), 0.06)
            if major:
                c.text(tx, AXIS_Y + 0.85, str(kt), FONT_MEDIUM, 0.45, blend(MUTED, a))
    if st["axis_title"] > 0.004:
        a = st["axis_title"]
        c.text((AXIS_X0 + AXIS_X1) / 2, AXIS_Y + 2.0 + (1 - a) * 0.3, "WIND SPEED (KT)",
               FONT_BOLD, 0.42, blend(INK, a))


def _draw_labels(c, st):
    a = st["legend"]
    if a > 0.004:
        y, x = 1.2 - (1 - a) * 0.3, AXIS_X0
        for color, label in [(RED, "Delayed = True"), (GREEN, "Delayed = False")]:
            c.circle(x + DOT_D / 2, y, DOT_D / 2, fill=blend(color, a))
            c.text(x + DOT_D + 0.35, y, label, FONT_MEDIUM, 0.45, blend(INK, a), anchor="lm")
            x += DOT_D + 0.35 + c.text_w(label, FONT_MEDIUM, 0.45) + 1.2

    a = st["rule"]
    if a > 0.004:
        c.pill(BOUND_X, BOUND_TOP - 1.05 - (1 - a) * 0.4,
               f"IF  wind speed > {THRESHOLD:g} kt   THEN  delayed = True",
               FONT_BOLD, 0.44, WHITE, INK, a)

    a = st["region_label"]
    if a > 0.004:
        y = BOUND_TOP + 0.85
        c.text(BOUND_X - 0.7 - (1 - a) * 0.5, y, "PREDICT: FALSE", FONT_BOLD, 0.4,
               blend(GREEN_DARK, a, GREEN_TINT), anchor="rm")
        c.text(BOUND_X + 0.7 + (1 - a) * 0.5, y, "PREDICT: TRUE", FONT_BOLD, 0.4,
               blend(RED_DARK, a, RED_TINT), anchor="lm")

    a = st["score"]
    if a > 0.004:
        checked = [i for i in range(N_ROWS) if st["verdict"][i] >= 0.5]
        right = sum(CORRECT[i] for i in checked)
        wrong = len(checked) - right
        y, x = 1.2 - (1 - a) * 0.3, AXIS_X1
        for label, n, col in [("wrong", wrong, RED_DARK), ("correct", right, GREEN_DARK)]:
            s = f"{n} {label}"
            c.text(x, y, s, FONT_BOLD, 0.5, blend(col, a), anchor="rm")
            x -= c.text_w(s, FONT_BOLD, 0.5) + 1.0

    a = st["final"]
    if a > 0.004:
        n = sum(CORRECT)
        c.pill(BOUND_X, 3.2, f"Rule accuracy:  {n} / {N_ROWS}  =  {100 * n // N_ROWS}%",
               FONT_BOLD, 0.62,
               WHITE, INK, clamp01(a * 1.5), scale=lerp(0.6, 1.0, ease_out_back(a)))


def col_span(layout, keys):
    """(x0, x1) of the visible columns in `keys` (panel 1), or None if none are visible."""
    x, span = 0.0, None
    for key, _, w, _ in layout:
        if key in keys:
            span = (x if span is None else span[0], x + w)
        x += w
    return span


def _draw_table_overlays(c, st, layout, pw):
    for keys, a in st["col_box"]:
        span = col_span(layout, keys)
        if a > 0.004 and span:
            top = (HEADER_H - HEADER_FILL) / 2 - 0.16
            bottom = HEADER_H + N_SAMPLE - (1 - ROW_FILL) / 2 + 0.16
            c.rrect_outline(span[0] - 0.02, top, span[1] + 0.02, bottom, 0.3, blend(INK, a), 0.09)
    for text, keys, a in st["notes"]:
        span = col_span(layout, keys)
        if a > 0.004 and span:
            half = c.text_w(text, FONT_BOLD, 0.34) / 2 + 0.55
            x = min(max((span[0] + span[1]) / 2, half), pw - half)  # keep it over the table
            c.pill(x, -0.95 + (1 - a) * 0.3, text, FONT_BOLD, 0.34, WHITE, INK, a)
    text, a = st["caption"]
    if a > 0.004:
        c.pill(pw / 2, HEADER_H + N_SAMPLE + 1.2 - (1 - a) * 0.3, text, FONT_BOLD, 0.44,
               WHITE, INK, a)


def _draw_free(c, st):
    for color, x0, y0, x1, y1, r, a in st["tiles"]:
        if a > 0.004:
            c.rrect(x0, y0, x1, y1, r, blend(color, a))
    for x0, y0, x1, y1, r, a, w in st["boxes"]:
        if a > 0.004:
            c.rrect_outline(x0, y0, x1, y1, r, blend(INK, a), w)
    for x0, y0, x1, y1, w, a, dashed in st["lines"]:
        if a <= 0.004:
            continue
        if not dashed:
            c.line([(x0, y0), (x1, y1)], blend(INK, a), w)
            continue
        n = max(1, round(math.hypot(x1 - x0, y1 - y0) / 0.45))
        for k in range(n):
            s0, s1 = k / n, (k + 0.6) / n
            c.line([(lerp(x0, x1, s0), lerp(y0, y1, s0)), (lerp(x0, x1, s1), lerp(y0, y1, s1))],
                   blend(INK, a), w)
    for x, y, text, size, color, a, bold, anchor in st["texts"]:
        if a > 0.004:
            c.text(x, y, text, FONT_BOLD if bold else FONT_MEDIUM, size, blend(color, a), anchor)
    for x, y, text, size, a in st["pills"]:
        if a > 0.004:
            c.pill(x, y, text, FONT_BOLD, size, WHITE, INK, a)


def render_frame(state, width=OUT_W, height=OUT_H, ss=2):
    st = default_state()
    st.update(state)
    c = Canvas(st["camera"], width, height, ss)
    _draw_regions(c, st)
    _draw_boundary(c, st)
    _draw_axis(c, st)
    layout = col_layout(st["cols"])
    pw = sum(w for _, _, w, _ in layout)
    _draw_table_headers(c, st, layout, pw)
    _draw_rows(c, st, layout, pw)
    _draw_table_overlays(c, st, layout, pw)
    _draw_free(c, st)
    _draw_labels(c, st)
    img = c.img
    if ss != 1:
        img = img.resize((width, height), Image.LANCZOS)
    return img


def _render_job(job):
    path, state, width, height, ss = job
    render_frame(state, width=width, height=height, ss=ss).save(path, compress_level=1)


# ---------------------------------------------------------------- encoding + CLI

def encode_gif(frames_dir, fps, out_path, loop=False):
    """loop=False plays the GIF once and stops on its last frame (no NETSCAPE loop block)."""
    vf = ("split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];"
          "[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps),
                    "-i", str(Path(frames_dir) / "f_%05d.png"), "-filter_complex", vf,
                    "-loop", "0" if loop else "-1", str(out_path)], check=True)


def main(name, duration, timeline):
    """timeline(t) -> state dict (see default_state) for t in seconds."""
    ap = argparse.ArgumentParser(description=f"Render {name}.gif (3840x2160)")
    ap.add_argument("--fps", type=int, default=25,
                    help="GIF delays are in 1/100 s, so 25 or 50 give exact timing (default 25)")
    ap.add_argument("--ss", type=int, default=2, help="supersampling factor (default 2)")
    ap.add_argument("--preview", action="store_true", help="quick 1920x1080 render, no supersampling")
    ap.add_argument("--out", type=Path, default=HERE / "output")
    ap.add_argument("--workers", type=int, default=max(1, min(6, (os.cpu_count() or 2) - 1)))
    ap.add_argument("--keep-frames", action="store_true", help="keep the PNG frames next to the GIF")
    ap.add_argument("--loop", action="store_true",
                    help="loop forever (default: play once and stay on the last frame)")
    ap.add_argument("--hold", type=float, default=60,
                    help="minutes to hold the last frame, for apps that loop every GIF such as "
                         "Google Slides (default 60, 0 = no hold)")
    args = ap.parse_args()

    width, height, ss = (1920, 1080, 1) if args.preview else (OUT_W, OUT_H, args.ss)
    suffix = "_preview" if args.preview else ""
    args.out.mkdir(parents=True, exist_ok=True)
    out_gif = args.out / f"{name}{suffix}.gif"

    n = round(duration * args.fps)
    frames_dir = Path(tempfile.mkdtemp(prefix=f"{name}_"))
    jobs = [(frames_dir / f"f_{k:05d}.png", timeline(k / args.fps), width, height, ss)
            for k in range(n)]
    print(f"{name}: {n} frames at {width}x{height} (font: {FONT_NAME}, {args.workers} workers)")
    with Pool(args.workers) as pool:
        for k, _ in enumerate(pool.imap(_render_job, jobs), 1):
            print(f"\r  rendered {k}/{n}", end="", flush=True)
    print("\n  encoding GIF ...")
    encode_gif(frames_dir, args.fps, out_gif, loop=args.loop)
    from set_gif_loop import finish_gif
    finish_gif(out_gif, loop=args.loop, hold_minutes=args.hold)

    if args.keep_frames:
        dest = args.out / f"{name}{suffix}_frames"
        shutil.rmtree(dest, ignore_errors=True)
        shutil.move(str(frames_dir), dest)
    else:
        shutil.rmtree(frames_dir)
    print(f"  wrote {out_gif} ({out_gif.stat().st_size / 1e6:.1f} MB)")
    check_macos_decodes(out_gif)


def check_macos_decodes(path):
    """macOS ImageIO rejects some GIFs other decoders accept (e.g. a near-blank 4K first frame)."""
    if shutil.which("sips") is None:
        return
    res = subprocess.run(["sips", "-g", "pixelWidth", str(path)], capture_output=True, text=True)
    if "<nil>" in res.stdout:
        print("  WARNING: macOS cannot decode this GIF (Preview/Keynote will refuse it). "
              "Make sure the first frame has visible content, not a plain background.")
