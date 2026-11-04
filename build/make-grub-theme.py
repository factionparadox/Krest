#!/usr/bin/env python3
"""Make Krest's GRUB theme (run after changing the design below):
  desktop/root/usr/share/krest/grub-theme/   background.png, theme.txt, the menu's highlight
                                              pieces and its fonts (.pf2, with Cyrillic)
The installer copies it to /boot/grub/themes/krest.

The screen: Паша (branding/pasha.png) on the left in a red glow against a starry night,
КРЕСТ and the menu on the right. Drawn for the 13 Pro's 3:2 panel
(2880 x 1920); GRUB crops it to other shapes.
Needs Pillow and grub-mkfont (grub's tools):  python3 build/make-grub-theme.py
"""
import math, random, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'desktop/root/usr/share/krest/grub-theme'
W, H = 2880, 1920
BG = (12, 12, 16)
RED, DARKRED, GREY, WHITE = (213, 43, 30), (70, 8, 10), (150, 150, 158), (236, 236, 240)
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def star(d, cx, cy, r, fill, points=5, inner=0.42):
    pts = []
    for i in range(points * 2):
        a = -math.pi / 2 + i * math.pi / points
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def background():
    img = Image.new('RGB', (W, H), BG)
    # a deep red glow behind Pasha, fading to the background
    glow = Image.new('L', (W, H), 0)
    gd = ImageDraw.Draw(glow)
    cx, cy = 860, 1010
    for r in range(1100, 0, -20):
        gd.ellipse((cx - r, cy - r * 0.9, cx + r, cy + r * 0.9), fill=int(255 * (1 - r / 1100) ** 1.6))
    img = Image.composite(Image.new('RGB', (W, H), DARKRED), img, glow.filter(ImageFilter.GaussianBlur(60)))
    # the night sky: a scatter of faint stars, and the Southern Cross itself, large and dim
    d = ImageDraw.Draw(img)
    rnd = random.Random(1999)
    for _ in range(420):
        x, y = rnd.randrange(W), rnd.randrange(H)
        v = rnd.randrange(40, 95)
        s = rnd.choice((1, 1, 1, 2, 2, 3))
        d.ellipse((x, y, x + s, y + s), fill=(v, v, v + 6))
    # Pasha, his black backdrop made see-through
    pasha = Image.open(ROOT / 'branding/pasha.png').convert('RGB')
    pasha = pasha.crop((380, 20, 1160, 1000))
    scale = 1180 / pasha.height
    pasha = pasha.resize((int(pasha.width * scale), 1180), Image.LANCZOS)
    mask = pasha.convert('L').point(lambda v: 0 if v < 10 else min(255, (v - 10) * 12))
    img.paste(pasha, (cx - pasha.width // 2, cy - pasha.height // 2 + 20), mask.filter(ImageFilter.GaussianBlur(1)))
    # КРЕСТ, the name, and a red rule under them
    d = ImageDraw.Draw(img)
    title = ImageFont.truetype(BOLD, 230)
    x0, y0 = 1560, 250
    x = x0
    for ch in 'КРЕСТ':
        d.text((x, y0), ch, font=title, fill=RED)
        x += d.textlength(ch, font=title) + 34
    sub = ImageFont.truetype(SANS, 64)
    d.text((x0 + 6, y0 + 290), 'Krest  ·  built on CRUX', font=sub, fill=GREY)
    d.rectangle((x0 + 6, y0 + 400, x0 + 1180, y0 + 406), fill=RED)
    return img


def highlight():
    # the selected menu line: a translucent red band with a solid red bar at its left edge
    Image.new('RGBA', (8, 8), (213, 43, 30, 70)).save(OUT / 'select_c.png')
    Image.new('RGBA', (12, 8), (213, 43, 30, 255)).save(OUT / 'select_w.png')
    Image.new('RGBA', (8, 8), (213, 43, 30, 70)).save(OUT / 'select_e.png')


def fonts():
    ranges = '0x20-0x7e,0xa0-0x17f,0x400-0x4ff,0x2010-0x2027,0x2190-0x21ff,0x25b2-0x25bc'
    for path, size, name in ((SANS, 44, 'menu'), (SANS, 32, 'hint'), (BOLD, 44, 'menu-bold')):
        subprocess.run(['grub-mkfont', '-s', str(size), '-r', ranges, '-o', str(OUT / f'{name}.pf2'), path],
                       check=True)


THEME = '''# Krest's GRUB theme (made by build/make-grub-theme.py)
title-text: ""
desktop-image: "background.png"
desktop-image-scale-method: "crop"
desktop-color: "#0c0c10"
terminal-font: "DejaVu Sans Regular 32"

+ boot_menu {
	left = 54%
	top = 44%
	width = 40%
	height = 40%
	item_font = "DejaVu Sans Regular 44"
	selected_item_font = "DejaVu Sans Bold 44"
	item_color = "#9696a0"
	selected_item_color = "#ececf0"
	item_height = 76
	item_padding = 28
	item_spacing = 14
	icon_width = 0
	icon_height = 0
	selected_item_pixmap_style = "select_*.png"
	scrollbar = false
}

+ label {
	left = 54%
	top = 88%
	width = 40%
	align = "left"
	id = "__timeout__"
	text = "Starting in %d s  ·  ↑ ↓ choose  ·  Enter starts  ·  e edits"
	color = "#9696a0"
	font = "DejaVu Sans Regular 32"
}
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    background().save(OUT / 'background.png', optimize=True)
    highlight()
    fonts()
    (OUT / 'theme.txt').write_text(THEME)
    for f in sorted(OUT.iterdir()):
        print(f'{f.stat().st_size:>9}  {f.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
