"""Control how existing GIFs end, without re-rendering: loop forever, or play once and hold.

Two independent switches:

  * Loop block. Looping is controlled by the NETSCAPE2.0 application extension; without it, a GIF
    plays once in browsers, Keynote and PowerPoint.
  * Final hold. Some apps loop every GIF regardless (Google Slides re-processes uploaded GIFs and
    always loops them). For those, the last frame is held for a long time: its delay is set to the
    GIF maximum (655.35 s) and invisible 1x1 frames that repeat the corner pixel extend it further,
    so the animation plays once and then sits on its final image for the whole presentation.

    python set_gif_loop.py                 # every GIF in output/: play once, hold ~60 min
    python set_gif_loop.py --hold 0        # play once, no extra hold
    python set_gif_loop.py --loop          # loop forever, no hold
    python set_gif_loop.py path/to/a.gif   # only the given files
"""

import argparse
import math
from pathlib import Path

from PIL import Image

NETSCAPE = b"\x21\xff\x0bNETSCAPE2.0"
LOOP_FOREVER = NETSCAPE + b"\x03\x01\x00\x00\x00"  # 19-byte block, loop count 0 = forever
MAX_DELAY = 65535  # centiseconds, the largest delay a GIF frame can have (~10.9 min)


def _header_end(data):
    """Offset just after the header, logical screen descriptor and global colour table."""
    end = 13
    if data[10] & 0x80:
        end += 3 * (2 << (data[10] & 7))
    return end


def _skip_sub_blocks(data, pos):
    while data[pos]:
        pos += data[pos] + 1
    return pos + 1


def _blocks(data):
    """Top-level blocks as (kind, start, end): kind is 'ext:<label>' or 'img'; ends at trailer."""
    pos, out = _header_end(data), []
    while data[pos] != 0x3B:
        start = pos
        if data[pos] == 0x21:
            label = data[pos + 1]
            pos = _skip_sub_blocks(data, pos + 2)
            out.append((f"ext:{label:02x}", start, pos))
        elif data[pos] == 0x2C:
            packed = data[pos + 9]
            pos += 10
            if packed & 0x80:
                pos += 3 * (2 << (packed & 7))
            pos = _skip_sub_blocks(data, pos + 1)  # +1: LZW minimum code size
            out.append(("img", start, pos))
        else:
            raise ValueError(f"unexpected GIF block 0x{data[pos]:02x} at {pos}")
    return out, pos


def set_loop(data, loop):
    start = data.find(NETSCAPE)
    if start != -1:  # drop the existing block (header 14 bytes + data sub-blocks)
        data = data[:start] + data[_skip_sub_blocks(data, start + 14):]
    if loop:
        at = _header_end(data)
        data = data[:at] + LOOP_FOREVER + data[at:]
    return data


def _hold_frame(width, height, rgb):
    """GCE (max delay) + a 1x1 frame at the bottom-right corner in that pixel's own colour."""
    gce = b"\x21\xf9\x04\x00" + MAX_DELAY.to_bytes(2, "little") + b"\x00\x00"
    desc = (b"\x2c" + (width - 1).to_bytes(2, "little") + (height - 1).to_bytes(2, "little")
            + b"\x01\x00\x01\x00\x80")  # 1x1, 2-entry local colour table
    lct = bytes(rgb) + b"\x00\x00\x00"
    lzw = b"\x02\x02\x44\x01\x00"  # min code size 2: clear, index 0, end
    return gce + desc + lct + lzw


HOLD_TAG = b"hold:"  # comment extension marking the appended hold; stores the original delay


def _last_gce(blocks):
    return next(b for b in reversed(blocks) if b[0] == "ext:f9")


def _set_delay(data, gce, delay):
    return data[:gce[1] + 4] + delay.to_bytes(2, "little") + data[gce[1] + 6:]


def set_hold(data, path, minutes):
    """Undo any earlier hold, then hold the last frame for about `minutes` minutes."""
    blocks, trailer = _blocks(data)
    for kind, start, _ in blocks:
        n = data[start + 2]
        if kind == "ext:fe" and data[start + 3:start + 3 + len(HOLD_TAG)] == HOLD_TAG:
            old_delay = int(data[start + 3 + len(HOLD_TAG):start + 3 + n])
            data = data[:start] + data[trailer:]  # the marker and every hold frame after it
            blocks, trailer = _blocks(data)
            data = _set_delay(data, _last_gce(blocks), old_delay)
            break
    if minutes <= 0:
        return data
    gce = _last_gce(blocks)
    marker = HOLD_TAG + str(int.from_bytes(data[gce[1] + 4:gce[1] + 6], "little")).encode()
    data = _set_delay(data, gce, MAX_DELAY)
    width, height = int.from_bytes(data[6:8], "little"), int.from_bytes(data[8:10], "little")
    im = Image.open(path)
    im.seek(im.n_frames - 1)
    corner = im.convert("RGB").getpixel((width - 1, height - 1))
    extra = max(0, math.ceil(minutes * 6000 / MAX_DELAY) - 1)
    comment = b"\x21\xfe" + bytes([len(marker)]) + marker + b"\x00"
    return (data[:trailer] + comment + _hold_frame(width, height, corner) * extra
            + data[trailer:])


def finish_gif(path, loop=False, hold_minutes=60):
    path = Path(path)
    data = path.read_bytes()
    if data[:6] not in (b"GIF87a", b"GIF89a"):
        raise ValueError(f"{path} is not a GIF")
    data = set_loop(data, loop)
    data = set_hold(data, path, 0 if loop else hold_minutes)
    path.write_bytes(data)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("gifs", nargs="*", type=Path)
    ap.add_argument("--loop", action="store_true", help="loop forever instead of playing once")
    ap.add_argument("--hold", type=float, default=60,
                    help="minutes to hold the last frame when playing once (default 60)")
    args = ap.parse_args()
    gifs = args.gifs or sorted((Path(__file__).resolve().parent / "output").glob("*.gif"))
    for gif in gifs:
        finish_gif(gif, args.loop, args.hold)
        how = "loops forever" if args.loop else f"plays once, holds last frame ~{args.hold:g} min"
        print(f"{how}  {gif.name}")


if __name__ == "__main__":
    main()
