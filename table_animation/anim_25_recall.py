"""Animation 25 (continues from the end of anim_24_precision): recall. The confusion-matrix
cells it uses light up, its formula appears with the real counts, and its score card slides in.

    python anim_25_recall.py            # 4K GIF -> output/anim_25_recall.gif
    python anim_25_recall.py --preview  # fast 1080p check
"""

import anim_24_precision as previous
from common import main
from model_common import METRICS, metric_timeline

TITLE = ("Evaluation  ·  Recall", METRICS[2][1])
timeline, DURATION = metric_timeline(2, previous.TITLE, TITLE)

if __name__ == "__main__":
    main("anim_25_recall", DURATION, timeline)
