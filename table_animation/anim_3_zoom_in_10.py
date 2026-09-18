"""Animation 3: the other 90 aircraft ripple out (farthest first) as the camera pushes back in on the 10.

    python anim_3_zoom_in_10.py            # 4K GIF -> output/anim_3_zoom_in_10.gif
    python anim_3_zoom_in_10.py --preview  # fast 1080p check
"""

from common import (CAM_10, CAM_100, N_SAMPLE, ease_in_out_cubic, lerp_camera, main, progress,
                    wave_order)

DURATION = 4.4  # s
HEADER_DIST, ROW_DIST = wave_order()


def fade_out(t, d):
    return 1 - progress(t, 0.4 + 1.1 * (1 - d), 0.45)


def timeline(t):
    camera = lerp_camera(CAM_100, CAM_10, ease_in_out_cubic((t - 0.6) / 2.2))
    headers = [1.0] + [fade_out(t, d) for d in HEADER_DIST[1:]]
    rows = [1.0 if i < N_SAMPLE else fade_out(t, d) for i, d in enumerate(ROW_DIST)]
    return dict(camera=camera, header_alpha=headers, row_alpha=rows)


if __name__ == "__main__":
    main("anim_3_zoom_in_10", DURATION, timeline)
