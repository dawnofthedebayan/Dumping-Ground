"""Animation 24 (continues from the end of anim_23_accuracy): precision. The confusion-matrix
cells it uses light up, its formula appears with the real counts, and its score card slides in.

    python anim_24_precision.py            # 4K GIF -> output/anim_24_precision.gif
    python anim_24_precision.py --preview  # fast 1080p check
"""

import anim_23_accuracy as previous
from common import main
from model_common import METRICS, metric_timeline

TITLE = ("Evaluation  ·  Precision", METRICS[1][1])
timeline, DURATION = metric_timeline(1, previous.TITLE, TITLE)

if __name__ == "__main__":
    main("anim_24_precision", DURATION, timeline)
