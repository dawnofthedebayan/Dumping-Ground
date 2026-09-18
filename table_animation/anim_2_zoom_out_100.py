"""Animation 2: the camera pulls back from the sample of 10 while the other 90 aircraft ripple in.

    python anim_2_zoom_out_100.py            # 4K GIF -> output/anim_2_zoom_out_100.gif
    python anim_2_zoom_out_100.py --preview  # fast 1080p check
"""

from common import (CAM_10, CAM_100, N_SAMPLE, ease_in_out_cubic, lerp_camera, main, progress,
                    wave_order)

DURATION = 5.0  # s
HEADER_DIST, ROW_DIST = wave_order()


def timeline(t):
    camera = lerp_camera(CAM_10, CAM_100, ease_in_out_cubic((t - 0.4) / 2.2))
    headers = [1.0] + [progress(t, 0.7 + 1.6 * d, 0.6) for d in HEADER_DIST[1:]]
    rows = [1.0 if i < N_SAMPLE else progress(t, 0.7 + 1.6 * d, 0.6)
            for i, d in enumerate(ROW_DIST)]
    return dict(camera=camera, header_alpha=headers, row_alpha=rows)


if __name__ == "__main__":
    main("anim_2_zoom_out_100", DURATION, timeline)
