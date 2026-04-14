"""
Run once to generate icons/icon-192.png and icons/icon-512.png.
Requires: pip install Pillow
"""
import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs('icons', exist_ok=True)

def make_icon(size):
    img = Image.new('RGBA', (size, size), (22, 27, 34, 255))   # #161b22 bg
    d = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    pad = int(size * 0.08)

    # Outer road circle
    r_out = cx - pad
    d.ellipse([cx - r_out, cy - r_out, cx + r_out, cy + r_out],
              outline=(48, 54, 61, 255), width=max(2, size // 64))

    # Road cross (dark asphalt)
    road_w = int(size * 0.22)
    road_color = (33, 38, 45, 255)   # #21262d
    d.rectangle([cx - road_w, pad, cx + road_w, size - pad], fill=road_color)
    d.rectangle([pad, cy - road_w, size - pad, cy + road_w], fill=road_color)

    # Centre box
    centre = int(size * 0.13)
    d.rectangle([cx - centre, cy - centre, cx + centre, cy + centre],
                fill=road_color)

    # Traffic signals — 4 corners, each a tiny 3-dot column
    dot_r = max(3, size // 40)
    signal_offset = int(size * 0.30)
    signal_colors_by_dir = [
        # (x, y), top-dot-color, mid-dot-color, bot-dot-color
        ((cx - signal_offset, cy - signal_offset), (63,185,80,255),  (210,153,34,80), (248,81,73,80)),  # NW green
        ((cx + signal_offset, cy - signal_offset), (63,185,80,80),   (210,153,34,80), (248,81,73,255)), # NE red
        ((cx - signal_offset, cy + signal_offset), (63,185,80,80),   (210,153,34,255),(248,81,73,80)),  # SW yellow
        ((cx + signal_offset, cy + signal_offset), (63,185,80,255),  (210,153,34,80), (248,81,73,80)),  # SE green
    ]
    gap = dot_r * 3
    for (sx, sy), ct, cm, cb in signal_colors_by_dir:
        # housing
        hw = dot_r * 2
        ht = dot_r * 7
        d.rounded_rectangle([sx - hw, sy - ht, sx + hw, sy + ht],
                             radius=dot_r, fill=(13,17,23,255))
        d.ellipse([sx-dot_r, sy-ht+dot_r, sx+dot_r, sy-ht+dot_r*3], fill=ct)
        d.ellipse([sx-dot_r, sy-dot_r,    sx+dot_r, sy+dot_r],       fill=cm)
        d.ellipse([sx-dot_r, sy+ht-dot_r*3, sx+dot_r, sy+ht-dot_r],  fill=cb)

    # Centre label "NTCIP" — small text for 512, skip for 192
    if size >= 512:
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', size // 14)
        except Exception:
            font = ImageFont.load_default()
        text = 'NTCIP'
        bbox = d.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text((cx - tw // 2, cy - th // 2), text, fill=(88, 166, 255, 255), font=font)

    img.save(f'icons/icon-{size}.png', 'PNG')
    print(f'icons/icon-{size}.png created')

make_icon(192)
make_icon(512)
print('Done.')
