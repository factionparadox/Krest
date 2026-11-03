#!/usr/bin/env python3
"""Make Krest's logo files (run after changing the design below):
  branding/krest-logo.png and -512/-256/-128/-64.png   the mark, transparent
  desktop/root/usr/share/krest/fastfetch-logo.txt      fastfetch's logo: true-colour half
                                                         blocks, 44 x 22
  desktop/root/usr/share/krest/krest-wallpaper.png   the mark and the name on the background
  desktop/root/usr/share/pixmaps/krest.png             256 px icon
The mark: Крест is the cross, and CRUX is the Southern Cross: its four bright stars (Acrux at the
foot, Gacrux at the head, Mimosa and Delta Crucis on the arms) and the small Epsilon, as red
five-pointed stars, the brightest the largest. Drawn here, from shapes:
no source image. Needs Pillow:  python3 build/make-branding.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
B, SHARE = ROOT / 'branding', ROOT / 'desktop/root/usr/share'
BACKGROUND = (12, 12, 16)          # '#0c0c10', as in krest-session and the bar
RED, WHITE, BLUE, GREY = (213, 43, 30), (242, 242, 242), (0, 57, 166), (200, 200, 200)
COLS = 44                          # fastfetch logo width; height is half (cells are 1:2)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def star(d, cx, cy, r, fill):
    """A five-pointed star, point up, centred on (cx, cy), outer radius r."""
    import math
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.40
        pts.append((cx + rr * math.cos(a), cy - rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def mark(size=1200):
    """The Southern Cross, on a transparent square."""
    s = size / 1200
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x, y, r in ((600, 1010, 175),    # Acrux, the foot
                    (600, 190, 150),     # Gacrux, the head
                    (250, 520, 145),     # Mimosa, the left arm
                    (930, 440, 115),     # Delta Crucis, the right arm
                    (760, 720, 65)):     # Epsilon Crucis
        star(d, x * s, y * s, r * s, RED)
    box = im.split()[3].point(lambda v: 255 if v > 128 else 0).getbbox()
    crop = im.crop(box)
    side = max(crop.size); pad = int(side * 0.06)
    sq = Image.new('RGBA', (side + 2 * pad,) * 2, (0, 0, 0, 0))
    sq.paste(crop, ((sq.width - crop.width) // 2, (sq.height - crop.height) // 2), crop)
    return sq


def fastfetch_logo(sq):
    rows = COLS // 2
    px = sq.resize((COLS, rows * 2), Image.LANCZOS).load()
    solid = lambda p: p[3] >= 110
    lines = []
    for r in range(rows):
        line = ''
        for c in range(COLS):
            top, bot = px[c, 2 * r], px[c, 2 * r + 1]
            if solid(top) and solid(bot):
                line += f'\x1b[38;2;{top[0]};{top[1]};{top[2]}m\x1b[48;2;{bot[0]};{bot[1]};{bot[2]}m▀'
            elif solid(top):
                line += f'\x1b[49m\x1b[38;2;{top[0]};{top[1]};{top[2]}m▀'
            elif solid(bot):
                line += f'\x1b[49m\x1b[38;2;{bot[0]};{bot[1]};{bot[2]}m▄'
            else:
                line += '\x1b[0m '
        lines.append(line + '\x1b[0m')
    return '\n'.join(lines) + '\n'


def main():
    sq = mark(2400).resize((1200, 1200), Image.LANCZOS)
    sq.save(B / 'krest-logo.png', optimize=True)
    for n in (512, 256, 128, 64):
        sq.resize((n, n), Image.LANCZOS).save(B / f'krest-{n}.png', optimize=True)
    (SHARE / 'krest').mkdir(parents=True, exist_ok=True)
    (SHARE / 'pixmaps').mkdir(parents=True, exist_ok=True)
    (SHARE / 'krest/fastfetch-logo.txt').write_text(fastfetch_logo(sq), encoding='utf-8')
    wall = Image.new('RGBA', (2880, 1920), BACKGROUND + (255,))
    logo = sq.resize((760, 760), Image.LANCZOS)
    wall.paste(logo, ((wall.width - 760) // 2, 420), logo)
    d = ImageDraw.Draw(wall)
    font = ImageFont.truetype(FONT, 120)
    word = ' '.join('КРЕСТ')                                    # spaced out, poster style
    w = d.textlength(word, font=font)
    d.text(((wall.width - w) / 2, 1260), word, font=font, fill=GREY)
    wall.convert('RGB').save(SHARE / 'krest/krest-wallpaper.png', optimize=True)
    sq.resize((256, 256), Image.LANCZOS).save(SHARE / 'pixmaps/krest.png', optimize=True)


if __name__ == '__main__':
    main()
