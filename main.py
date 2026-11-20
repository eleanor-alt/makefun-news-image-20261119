#!/usr/bin/env python3
"""news-image-20261119: one image summing up the world news of
Thursday 19 November 2026. Dependency-free: own 5x7 bitmap font,
own PNG writer, deterministic output. Writes entry.png to
$MAKEFUN_OUTPUT_DIR (default /output)."""

import os
import struct
import zlib

# ---------------------------------------------------------------- colours
NAVY = (18, 38, 63)
CREAM = (247, 243, 234)
INK = (24, 24, 24)
RED = (200, 16, 46)
GOLD = (212, 160, 32)
GREY = (180, 172, 158)
SKY = (70, 120, 170)

W, H = 1024, 1024

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 cells, '#' = on, '.' = off. Written for this entry.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '&': (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '*': (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
}


def text_width(s, scale):
    return len(s) * 6 * scale


def draw_text(img, x, y, s, scale, color):
    """Draw uppercase text; unknown chars render as space."""
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '#':
                    fill_rect(img, cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += 6 * scale
    return cx


def wrap(text, max_chars):
    """Greedy word wrap into lines of at most max_chars characters."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
def new_canvas():
    return bytearray(CREAM[0:1] * 0) if False else [[CREAM] * W for _ in range(H)]


def fill_rect(img, x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        row = img[yy]
        for xx in range(x0, x1):
            row[xx] = color


def draw_line(img, x0, y0, x1, y1, color, thick=1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        fill_rect(img, x, y, thick, thick, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def draw_circle(img, cx, cy, r, color, filled=True):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d2 = (xx - cx) ** 2 + (yy - cy) ** 2
            if filled:
                if d2 <= r * r:
                    img[yy][xx] = color
            else:
                if abs(d2 - r * r) <= r * 2:
                    img[yy][xx] = color


def draw_triangle(img, pts, color):
    (x0, y0), (x1, y1), (x2, y2) = pts
    ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
    for yy in range(ymin, ymax + 1):
        xs = []
        for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                   ((x1, y1), (x2, y2)),
                                   ((x2, y2), (x0, y0))):
            if ay == by:
                continue
            if min(ay, by) <= yy <= max(ay, by):
                xs.append(ax + (bx - ax) * (yy - ay) / (by - ay))
        if len(xs) >= 2:
            a, b = int(min(xs)), int(max(xs))
            fill_rect(img, a, yy, b - a + 1, 1, color)


# ---------------------------------------------------------------- pictograms
def icon_summit(img, x, y):
    # Three flagpoles: three leaders meeting.
    for i, c in enumerate((NAVY, RED, GOLD)):
        px = x + 12 + i * 20
        draw_line(img, px, y + 8, px, y + 58, NAVY, 3)
        draw_triangle(img, [(px + 2, y + 8), (px + 18, y + 14),
                            (px + 2, y + 20)], c)
    draw_line(img, x + 6, y + 58, x + 64, y + 58, NAVY, 3)


def icon_scales(img, x, y):
    # Scales of justice.
    draw_line(img, x + 35, y + 6, x + 35, y + 52, NAVY, 3)
    draw_line(img, x + 12, y + 12, x + 58, y + 12, NAVY, 3)
    for px in (x + 12, x + 58):
        draw_line(img, px, y + 12, px + 6, y + 30, NAVY, 2)
        draw_line(img, px + 12, y + 12, px + 6, y + 30, NAVY, 2)
        draw_triangle(img, [(px - 2, y + 30), (px + 14, y + 30),
                            (px + 6, y + 40)], GOLD)
    fill_rect(img, x + 24, y + 52, 22, 5, NAVY)


def icon_chart(img, x, y):
    # Rising bars and an arrow: a record IPO.
    for i, h in enumerate((18, 30, 44)):
        fill_rect(img, x + 10 + i * 16, y + 56 - h, 11, h, SKY)
    draw_line(img, x + 8, y + 14, x + 26, y + 30, RED, 3)
    draw_line(img, x + 26, y + 30, x + 46, y + 12, RED, 3)
    draw_triangle(img, [(x + 46, y + 12), (x + 56, y + 10),
                        (x + 50, y + 20)], RED)


def icon_controller(img, x, y):
    # Game controller.
    fill_rect(img, x + 8, y + 20, 54, 26, NAVY)
    fill_rect(img, x + 8, y + 38, 12, 14, NAVY)
    fill_rect(img, x + 50, y + 38, 12, 14, NAVY)
    fill_rect(img, x + 14, y + 28, 4, 12, CREAM)
    fill_rect(img, x + 11, y + 31, 10, 4, CREAM)
    draw_circle(img, x + 46, y + 30, 3, RED)
    draw_circle(img, x + 54, y + 36, 3, GOLD)


def icon_tank(img, x, y):
    # Tank silhouette.
    fill_rect(img, x + 12, y + 30, 40, 14, NAVY)
    fill_rect(img, x + 22, y + 20, 18, 10, NAVY)
    draw_line(img, x + 40, y + 24, x + 62, y + 24, NAVY, 4)
    for wx in (18, 30, 42):
        draw_circle(img, x + wx, y + 48, 5, NAVY)
    draw_line(img, x + 8, y + 56, x + 58, y + 56, RED, 3)


def icon_voyager(img, x, y):
    # Dish antenna reaching for a distant star.
    for sx, sy in ((10, 10), (58, 8), (52, 46), (14, 48)):
        draw_circle(img, x + sx, y + sy, 2, GOLD)
    draw_line(img, x + 14, y + 52, x + 34, y + 30, NAVY, 3)
    draw_triangle(img, [(x + 28, y + 16), (x + 52, y + 16),
                        (x + 40, y + 34)], SKY)
    draw_circle(img, x + 40, y + 12, 3, RED)


ICONS = {
    'summit': icon_summit,
    'scales': icon_scales,
    'chart': icon_chart,
    'controller': icon_controller,
    'tank': icon_tank,
    'voyager': icon_voyager,
}

# ---------------------------------------------------------------- stories
# Headlines verified 20 Nov 2026 against AP, BBC and Reuters roundups
# (plus Just Security's Early Edition) of Thursday 19 November 2026.
STORIES = [
    ("DIPLOMACY", "summit",
     "TRUMP, XI AND PUTIN HOLD FIRST THREE-WAY SUMMIT IN SHENZHEN "
     "AND ISSUE A 'PEACE DECLARATION'"),
    ("JUSTICE", "scales",
     "UN COURT RULES MYANMAR COMMITTED GENOCIDE AGAINST THE ROHINGYA, "
     "THE FIRST STATE EVER FOUND GUILTY"),
    ("MARKETS", "chart",
     "ANTHROPIC IPO IS THE BIGGEST EVER: $83 A SHARE, ABOUT $81BN RAISED"),
    ("CULTURE", "controller",
     "GTA VI LAUNCHES AFTER 13 YEARS, WITH $1BN IN PRESALES"),
    ("MIDDLE EAST", "tank",
     "ISRAEL LAUNCHES GROUND OPERATION IN CENTRAL GAZA, BEYOND THE "
     "YELLOW LINE"),
    ("SPACE", "voyager",
     "NASA'S VOYAGER 1 PHONES HOME FROM ONE LIGHT-DAY AWAY"),
]


def render():
    img = new_canvas()

    # Banner.
    fill_rect(img, 0, 0, W, 150, NAVY)
    t1 = "THE WORLD IN ONE DAY"
    draw_text(img, (W - text_width(t1, 5)) // 2, 24, t1, 5, CREAM)
    date = "19 NOVEMBER 2026"
    day = "THURSDAY"
    total = text_width(date, 6) + text_width("  " + day, 6)
    x = (W - total) // 2
    draw_text(img, x, 82, date, 6, CREAM)
    draw_text(img, x + text_width(date + "  ", 6), 82, day, 6, RED)
    fill_rect(img, 0, 150, W, 6, RED)

    # Story grid: 2 columns x 3 rows.
    col_w, row_h = 476, 258
    gx, gy = 24, 166
    for i, (kicker, icon, headline) in enumerate(STORIES):
        cx = gx + (i % 2) * (col_w + 24)
        cy = gy + (i // 2) * (row_h + 14)
        fill_rect(img, cx, cy, col_w, 2, GREY)
        draw_text(img, cx + 10, cy + 12, kicker, 2, RED)
        lines = wrap(headline, 25)
        ly = cy + 44
        for line in lines:
            draw_text(img, cx + 10, ly, line, 3, INK)
            ly += 27
        ICONS[icon](img, cx + col_w - 78, cy + row_h - 78)

    # Footer.
    fill_rect(img, 0, 972, W, 4, RED)
    foot = "THURSDAY 19 NOVEMBER 2026 - ONE IMAGE, ONE DAY"
    draw_text(img, (W - text_width(foot, 2)) // 2, 988, foot, 2, INK)
    return img


# ---------------------------------------------------------------- PNG writer
def write_png(img, path):
    raw = bytearray()
    for row in img:
        raw.append(0)  # filter: none
        for (r, g, b) in row:
            raw.extend((r, g, b))
    data = zlib.compress(bytes(raw), 9)

    def chunk(tag, payload):
        c = struct.pack(">I", len(payload)) + tag + payload
        return c + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", data)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    write_png(render(), os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
