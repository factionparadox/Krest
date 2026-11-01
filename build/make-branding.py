#!/usr/bin/env python3
"""Make Pustota's logo files from branding/pustota-original.png (run after changing the logo):
  branding/pustota-logo.png and -512/-256/-128/-64.png   cropped to the roundel, transparent
  desktop/root/usr/share/pustota/fastfetch-logo.txt      true-colour half blocks, 44 x 22
  desktop/root/usr/share/pustota/pustota-wallpaper.png   the roundel on Pustota's background
  desktop/root/usr/share/pixmaps/pustota.png             256 px icon
Needs Pillow:  python3 build/make-branding.py
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
B, SHARE = ROOT / 'branding', ROOT / 'desktop/root/usr/share'
BACKGROUND = (12, 12, 16)          # '#0c0c10', as in pustota-session and the bar
COLS = 44                          # fastfetch logo width; height is half (cells are 1:2)


def roundel():
    im = Image.open(B / 'pustota-original.png').convert('RGBA')
    box = im.split()[3].point(lambda v: 255 if v > 128 else 0).getbbox()
    crop = im.crop(box)
    side = max(crop.size); pad = int(side * 0.04)
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
    sq = roundel()
    sq.save(B / 'pustota-logo.png', optimize=True)
    for n in (512, 256, 128, 64):
        sq.resize((n, n), Image.LANCZOS).save(B / f'pustota-{n}.png', optimize=True)
    (SHARE / 'pustota').mkdir(parents=True, exist_ok=True)
    (SHARE / 'pixmaps').mkdir(parents=True, exist_ok=True)
    (SHARE / 'pustota/fastfetch-logo.txt').write_text(fastfetch_logo(sq), encoding='utf-8')
    wall = Image.new('RGBA', (2880, 1920), BACKGROUND + (255,))
    logo = sq.resize((880, 880), Image.LANCZOS)
    wall.paste(logo, ((wall.width - 880) // 2, (wall.height - 880) // 2), logo)
    wall.convert('RGB').save(SHARE / 'pustota/pustota-wallpaper.png', optimize=True)
    sq.resize((256, 256), Image.LANCZOS).save(SHARE / 'pixmaps/pustota.png', optimize=True)


if __name__ == '__main__':
    main()
