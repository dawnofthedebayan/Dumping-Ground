"""Animation 26b (continues from the end of animation 26a): underfitting and overfitting, seen.

The grids and cards clear and the same 80 training flights are plotted three times - wind speed
across, visibility up - and the same model is asked what it would predict everywhere on that map.
One dial is turned between the three panels: how many trees it is allowed to use. Too few and it
paints the whole map one pale colour; too many and it draws a little box around every single
flight. Underneath each map, the score on the 80 it trained on and on the 20 it never saw.

Two features only, so the model's thinking fits on a screen; the models and the scores are real.

    python anim_26b_underfit_overfit.py            # 4K GIF -> output/anim_26b_underfit_overfit.gif
    python anim_26b_underfit_overfit.py --preview  # fast 1080p check
"""

import anim_26a_two_scores as previous
from common import main, progress
from fit_common import (PANEL_RECTS, SNAP_K, draw_panel, draw_panel_header, draw_scores,
                        stacked_notes)
from model_common import Scene, fade_state
from split_common import CX

DURATION = 12.0  # s
END = previous.timeline(previous.DURATION)

TITLE = ("Underfitting and overfitting",
         "The same model, the same 80 flights - one dial turned: how many trees it may use")
STARTS = (2.7, 4.9, 7.1)
NOTES = [
    (2.0, "It is the same data, same algorithm, but we modified how much complexity the model had"),
    (9.6, "The score on what it has seen (training data) only ever goes up.  The score on what it "
          "has not seen (test data) peaks in the middle and then falls."),
]


def timeline(t):
    sc = Scene()
    sc.title(*TITLE, progress(t, 0.5, 0.5))
    frames = progress(t, 1.0, 0.6)
    dots = progress(t, 1.5, 0.6)
    for j, (rect, k) in enumerate(zip(PANEL_RECTS, SNAP_K)):
        start = STARTS[j]
        draw_panel(sc, rect, k, frames, regions=progress(t, start, 0.3), dots=dots,
                   axes=progress(t, 1.9, 0.5), reveal=progress(t, start, 0.9))
        draw_panel_header(sc, rect, k, progress(t, start - 0.5, 0.5))
        draw_scores(sc, rect, k, progress(t, start + 0.5, 0.4), progress(t, start + 0.6, 0.9))
    stacked_notes(sc, CX, NOTES, t, y0=13.8)
    st = sc.state()
    old = fade_state(END, 1 - progress(t, 0.15, 0.45))
    for key in ("tiles", "boxes", "lines", "texts", "pills"):
        st[key] = old[key] + st[key]
    return st


if __name__ == "__main__":
    main("anim_26b_underfit_overfit", DURATION, timeline)
