"""Animation 26 (continues from the end of anim_25_recall): f1 score. The confusion-matrix
cells it uses light up, its formula appears with the real counts, and its score card slides in.
It ends by swapping the formula for the take-away: the model beats the hand-written wind rule.

    python anim_26_f1_score.py            # 4K GIF -> output/anim_26_f1_score.gif
    python anim_26_f1_score.py --preview  # fast 1080p check
"""

import anim_25_recall as previous
from common import main
from model_common import METRICS, metric_timeline

TITLE = ("Evaluation  ·  F1 score", METRICS[3][1])
timeline, DURATION = metric_timeline(3, previous.TITLE, TITLE)

if __name__ == "__main__":
    main("anim_26_f1_score", DURATION, timeline)
