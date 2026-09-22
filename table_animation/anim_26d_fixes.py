"""Animation 26d (continues from the end of animation 26c): what to do about it.

The chart clears and the two diagnoses stand side by side with the moves that answer them. The two
scores tell you which column you are in: both poor and close together means the model is too simple;
a fine training score with a much worse test score means it memorised. Everything here is a lever
you actually have on a tabular problem - features, capacity, regularisation, rows, early stopping,
and the columns you should never have handed it in the first place.

    python anim_26d_fixes.py            # 4K GIF -> output/anim_26d_fixes.gif
    python anim_26d_fixes.py --preview  # fast 1080p check
"""

import anim_26c_loss_curves as previous
from common import HEADER_BG, INK, MUTED, WHITE, main, mix, progress
from fit_common import FRAME
from model_common import Scene, fade_state
from split_common import CX

DURATION = 13.0  # s
END = previous.timeline(previous.DURATION)

TITLE = ("Fixing it",
         "Which way you move depends on which of the two scores is disappointing you")
COLS = [
    (0.5, 17.5, 2.2, "UNDERFITTING  ·  too simple",
     "Both scores are poor, and close to each other", [
         ("Give it more to work with",
          "Better features beat better algorithms: bad weather, departures in the same hour"),
         ("Let it grow",
          "More trees, deeper trees, more leaves - move right along the dial"),
         ("Ease off the regularisation",
          "Weaker penalties, less pruning, fewer constraints per leaf"),
         ("Train it longer",
          "More rounds, or a larger learning rate to cover ground faster"),
         ("Ask whether the label is learnable",
          "If no column in the table explains delays, no model will invent one"),
     ]),
    (18.5, 35.5, 6.2, "OVERFITTING  ·  memorised",
     "Great on what it saw, far worse on what it did not", [
         ("More rows",
          "The only fix that costs the model nothing - and usually the strongest"),
         ("Stop early",
          "Where the test curve turns up, not where the training curve flattens"),
         ("Make it simpler",
          "Shallower trees, fewer leaves, a minimum number of flights per leaf"),
         ("Turn regularisation up",
          "Lower the learning rate, subsample rows and columns, add an L1 / L2 penalty"),
         ("Drop the columns that identify a row",
          "MSN, serial numbers, exact timestamps: perfect memory, zero prediction"),
     ]),
]
NOTE_1 = "The two scores are the diagnosis.  The column you are in decides the treatment."
NOTE_2 = ("Judge every fix by cross-validation, not one lucky split.  And never tune on "
          "the test set: once you do, it stops being one")
ROW0, ROW_STEP = 5.75, 1.42


def column(sc, j, a, items_t):
    x0, x1, _, name, tell, items = COLS[j]
    sc.tile(HEADER_BG, (x0, 2.3, x1, 4.75), a, 0.3)
    sc.text(x0 + 0.65, 3.0, name, 0.46, INK, a, True, "lm")
    sc.text(x0 + 0.65, 3.78, "HOW YOU KNOW", 0.24, MUTED, a, True, "lm")
    sc.text(x0 + 0.65, 4.32, tell, 0.32, INK, a, False, "lm")
    for k, (head, detail) in enumerate(items):
        ia = items_t[k]
        if ia <= 0.004:
            continue
        y = ROW0 + k * ROW_STEP
        dx = (1 - ia) * 0.6
        sc.tile(INK, (x0 + 0.15 + dx, y - 0.4, x0 + 0.95 + dx, y + 0.4), ia, 0.16)
        sc.text(x0 + 0.55 + dx, y + 0.02, str(k + 1), 0.4, WHITE, ia, True)
        sc.text(x0 + 1.3 + dx, y - 0.14, head, 0.36, INK, ia, True, "lm")
        sc.text(x0 + 1.3 + dx, y + 0.46, detail, 0.275, MUTED, ia, False, "lm")


def timeline(t):
    sc = Scene()
    sc.title(*TITLE, progress(t, 0.5, 0.5))
    for j, (_, _, start, *_rest) in enumerate(COLS):
        column(sc, j, progress(t, 1.0 + 0.25 * j, 0.5),
               [progress(t, start + k * 0.75, 0.45) for k in range(5)])
    sc.line(18.0, 2.3, 18.0, 12.6, progress(t, 1.5, 0.6) * 0.5, 0.04, True, FRAME)
    sc.pill(CX, 13.6, NOTE_1, 0.36, progress(t, 2.6, 0.5) * (1 - progress(t, 10.4, 0.4)))
    sc.pill(CX, 13.6, NOTE_2, 0.36, progress(t, 10.7, 0.5))
    st = sc.state()
    old = fade_state(END, 1 - progress(t, 0.15, 0.45))
    for key in ("tiles", "boxes", "lines", "texts", "pills"):
        st[key] = old[key] + st[key]
    return st


if __name__ == "__main__":
    main("anim_26d_fixes", DURATION, timeline)
