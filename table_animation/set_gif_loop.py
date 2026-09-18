"""Switch existing GIFs between playing once and looping forever, without re-rendering.

Looping is controlled only by the NETSCAPE2.0 application extension block; removing it makes a
GIF play once and stay on its last frame. Frames and timing are untouched.

    python set_gif_loop.py                 # every GIF in output/ plays once
    python set_gif_loop.py --loop          # every GIF in output/ loops forever
    python set_gif_loop.py path/to/a.gif   # only the given files
"""

import argparse
from pathlib import Path

NETSCAPE = b"\x21\xff\x0bNETSCAPE2.0"
LOOP_FOREVER = NETSCAPE + b"\x03\x01\x00\x00\x00"  # 19-byte block, loop count 0 = forever


def _header_end(data):
    """Offset just after the header, logical screen descriptor and global colour table."""
    end = 13
    if data[10] & 0x80:
        end += 3 * (2 << (data[10] & 7))
    return end


def set_loop(path, loop):
    data = Path(path).read_bytes()
    if data[:6] not in (b"GIF87a", b"GIF89a"):
        raise ValueError(f"{path} is not a GIF")
    start = data.find(NETSCAPE)
    if start != -1:  # drop the existing block (header 14 bytes + data sub-blocks)
        end = start + 14
        while data[end]:
            end += data[end] + 1
        data = data[:start] + data[end + 1:]
    if loop:
        at = _header_end(data)
        data = data[:at] + LOOP_FOREVER + data[at:]
    Path(path).write_bytes(data)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("gifs", nargs="*", type=Path)
    ap.add_argument("--loop", action="store_true", help="loop forever instead of playing once")
    args = ap.parse_args()
    gifs = args.gifs or sorted((Path(__file__).resolve().parent / "output").glob("*.gif"))
    for gif in gifs:
        set_loop(gif, args.loop)
        print(f"{'loops forever' if args.loop else 'plays once   '}  {gif.name}")


if __name__ == "__main__":
    main()
