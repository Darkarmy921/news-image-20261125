"""Render the 25 November 2026 world-news front page as a 1024x1024 PNG.

Deterministic: fixed fonts, fixed geometry, fixed colours, no clock, no
randomness, no network. Data comes only from stories.json beside this file.
"""
import json
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
NAVY = (15, 42, 74)
NAVY2 = (23, 62, 104)
PAPER = (250, 248, 243)
INK = (20, 20, 20)
GREY = (90, 90, 90)
LINE = (205, 200, 190)
WHITE = (255, 255, 255)
RED = (169, 50, 38)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, width, fill, max_lines, lh):
    lines = wrap(draw, text, fnt, width)[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def tag(draw, x, y, text, colour, fnt):
    w = draw.textlength(text, font=fnt) + 14
    draw.rounded_rectangle([x, y, x + w, y + 22], radius=4, fill=colour)
    draw.text((x + 7, y + 3), text, font=fnt, fill=WHITE)
    return w


def draw_tanker_scene(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(18, 62, 96))
    draw.rectangle([x0, y0, x1, y0 + 34], fill=(38, 92, 130))
    draw.text((x0 + 12, y0 + 8), "STRAIT OF HORMUZ", font=font(BOLD, 15),
              fill=(255, 214, 120))
    # sea lanes
    for yy in (y0 + 62, y0 + 118):
        for xx in range(x0 + 10, x1 - 10, 26):
            draw.line([xx, yy, xx + 14, yy], fill=(120, 180, 215), width=3)
    # two tankers
    for tx, ty in ((x0 + 22, y0 + 78), (x0 + 150, y0 + 128)):
        draw.rectangle([tx, ty, tx + 120, ty + 26], fill=(200, 60, 40))
        draw.rectangle([tx + 96, ty - 16, tx + 112, ty], fill=(230, 230, 230))
        draw.rectangle([tx + 8, ty + 26, tx + 112, ty + 32], fill=(40, 40, 40))
    # mines: spiked circles
    for mx, my in ((x0 + 210, y0 + 62), (x0 + 60, y0 + 150)):
        draw.ellipse([mx - 9, my - 9, mx + 9, my + 9], fill=(255, 214, 120),
                     outline=(120, 60, 0), width=2)
        for dx, dy in ((-12, 0), (12, 0), (0, -12), (0, 12)):
            draw.line([mx, my, mx + dx, my + dy], fill=(255, 214, 120), width=2)
    # smoke
    for sx, sy, r in ((x0 + 96, y0 + 66, 10), (x0 + 112, y0 + 56, 13),
                      (x0 + 250, y0 + 116, 10)):
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(220, 220, 220))


def render(data, out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    date = data["date"]
    # Header: top row left/right, date centred on its own row below
    d.rectangle([0, 0, W, 84], fill=NAVY)
    d.text((18, 10), "WORLD IN ONE DAY", font=font(BOLD, 19), fill=(255, 214, 120))
    d.text((W - 168, 10), "25 NOV 2026", font=font(BOLD, 19), fill=WHITE)
    dt = font(BOLD, 30)
    tw = d.textlength(date.upper(), font=dt)
    d.text(((W - tw) / 2, 40), date.upper(), font=dt, fill=WHITE)
    # Lead panel: 196 high, extras are headline-only so nothing overflows
    ly = 84
    d.rectangle([0, ly, W, ly + 196], fill=WHITE)
    d.rectangle([0, ly, W, ly + 196], outline=LINE, width=2)
    d.text((18, ly + 8), "LEAD STORY", font=font(BOLD, 16), fill=RED)
    d.text((150, ly + 8), "MIDDLE EAST  •  WAR / SECURITY",
           font=font(BOLD, 15), fill=GREY)
    d.text((W - 210, ly + 8), "25 NOV 2026", font=font(BOLD, 15), fill=RED)
    draw_tanker_scene(d, 18, ly + 36, 330, ly + 188)
    lead = data["lead"]
    x = 350
    y = draw_wrapped(d, x, ly + 36, lead["headline"], font(BOLD, 26),
                     W - x - 18, INK, 2, 31)
    y = draw_wrapped(d, x, y + 4, lead["summary"], font(REG, 16),
                     W - x - 18, (50, 50, 50), 2, 20)
    y += 10
    for extra in data["lead_extra"]:
        tag(d, x, y, extra["region"], (90, 90, 90), font(BOLD, 12))
        draw_wrapped(d, x + 118, y + 1, extra["headline"], font(BOLD, 15),
                     W - x - 136, INK, 1, 19)
        y += 25
    # Grid: 2 cols x 3 rows, 176 high each; headlines get 2 lines, summary 1
    gy = 280
    gw, gh = 500, 176
    for i, panel in enumerate(data["grid"]):
        col, row = i % 2, i // 2
        px = 8 + col * 508
        py = gy + row * 176
        d.rectangle([px, py, px + gw, py + gh - 6], fill=WHITE,
                    outline=LINE, width=1)
        d.rectangle([px, py, px + gw, py + 30], fill=panel["color"])
        d.text((px + 10, py + 6), panel["panel"], font=font(BOLD, 16), fill=WHITE)
        sy = py + 38
        for st in panel["stories"]:
            tag(d, px + 10, sy, st["region"], panel["color"], font(BOLD, 11))
            draw_wrapped(d, px + 10, sy + 25, st["headline"], font(BOLD, 16),
                         gw - 20, INK, 2, 19)
            sy += 66
            if st is not panel["stories"][-1]:
                d.line([px + 10, sy - 6, px + gw - 10, sy - 6], fill=LINE, width=1)
    # More today: 2 rows x 4 cols, headlines get 2 lines
    my = 808
    d.rectangle([0, my, W, my + 122], fill=(238, 234, 226))
    d.text((18, my + 6), "MORE FROM 25 NOVEMBER 2026",
           font=font(BOLD, 16), fill=NAVY)
    cw = 244
    for i, st in enumerate(data["more"]):
        col, row = i % 4, i // 4
        px = 12 + col * 252
        py = my + 28 + row * 48
        d.text((px, py), st["region"], font=font(BOLD, 12), fill=RED)
        draw_wrapped(d, px, py + 14, st["headline"], font(BOLD, 14),
                     cw, INK, 2, 16)
    # Strip: 6 short items
    sy = 930
    d.rectangle([0, sy, W, sy + 54], fill=NAVY2)
    for i, st in enumerate(data["strip"]):
        px = 18 + i * 168
        d.text((px, sy + 4), st["region"], font=font(BOLD, 11),
               fill=(255, 214, 120))
        draw_wrapped(d, px, sy + 18, st["headline"], font(BOLD, 14),
                     156, WHITE, 2, 16)
    # Footer
    fy = 984
    d.rectangle([0, fy, W, H], fill=NAVY)
    d.text((18, fy + 11),
           "Wednesday 25 November 2026  •  Events that happened or were first reported on 25 Nov 2026",
           font=font(BOLD, 15), fill=WHITE)
    d.text((18, fy + 11), "", font=font(REG, 14), fill=WHITE)
    img.save(out_path, format="PNG", optimize=True)
    return out_path


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    render(data, os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
