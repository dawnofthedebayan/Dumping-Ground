"""Animation 1: a sample of 10 aircraft cascade in under the header, then hold.

The header is visible from the very first frame on purpose: macOS (Preview/Finder/Keynote) cannot
decode a 4K GIF whose first frame is an almost blank white canvas.

    python anim_1_sample_10.py            # 4K GIF -> output/anim_1_sample_10.gif
    python anim_1_sample_10.py --preview  # fast 1080p check
"""

from common import CAM_10, N_ROWS, N_SAMPLE, PANELS, main, progress

DURATION = 4.0  # s


def timeline(t):
    headers = [1.0] + [0.0] * (PANELS - 1)
    rows = [progress(t, 0.4 + i * 0.13, 0.55) if i < N_SAMPLE else 0.0 for i in range(N_ROWS)]
    return dict(camera=CAM_10, header_alpha=headers, row_alpha=rows)


if __name__ == "__main__":
    main("anim_1_sample_10", DURATION, timeline)
