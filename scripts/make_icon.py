"""Generate the CS2 Climate Calculator app icon.

Design: rounded square with a blue->violet diagonal gradient (matching the
in-app titlebar mark), a warm sun peeking from the upper left, a white cloud,
and three rain streaks below it.

Outputs (relative to the repo root):
  icon.ico        multi-size Windows icon (16..256 px)
  docs/icon.png   256 px preview used in the README

Requires: pip install pillow
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

S = 512  # master size, downscaled for all ico entries
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def make_master():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    # --- gradient background on a rounded square ---
    grad = Image.new("RGBA", (S, S))
    c1, c2 = (57, 135, 229, 255), (144, 133, 233, 255)  # #3987e5 -> #9085e9
    px = grad.load()
    for y in range(S):
        for x in range(S):
            t = (x + y) / (2 * S - 2)
            px[x, y] = lerp(c1, c2, t)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([8, 8, S - 8, S - 8], radius=112, fill=255)
    img.paste(grad, (0, 0), mask)

    # subtle top-left light wash for depth
    wash = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(wash).ellipse([-S * 0.35, -S * 0.45, S * 0.85, S * 0.55], fill=(255, 255, 255, 46))
    wash = wash.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, Image.composite(wash, Image.new("RGBA", (S, S), (0, 0, 0, 0)), mask))

    d = ImageDraw.Draw(img)

    # --- sun (upper left, behind cloud) ---
    sun_c = (255, 209, 102, 255)  # #ffd166
    ray_c = (255, 209, 102, 230)
    cx, cy, r = int(S * 0.38), int(S * 0.34), int(S * 0.13)
    for k in range(8):
        ang = math.pi * 2 * k / 8 + math.pi / 8
        x1 = cx + math.cos(ang) * (r + S * 0.035)
        y1 = cy + math.sin(ang) * (r + S * 0.035)
        x2 = cx + math.cos(ang) * (r + S * 0.095)
        y2 = cy + math.sin(ang) * (r + S * 0.095)
        d.line([x1, y1, x2, y2], fill=ray_c, width=int(S * 0.028))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=sun_c)

    # --- cloud (center-right), soft shadow first ---
    cloud = (255, 255, 255, 255)
    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)

    def cloud_shapes(dd, dx=0, dy=0, col=(0, 0, 0, 70)):
        dd.ellipse([S * 0.30 + dx, S * 0.42 + dy, S * 0.55 + dx, S * 0.66 + dy], fill=col)
        dd.ellipse([S * 0.42 + dx, S * 0.33 + dy, S * 0.72 + dx, S * 0.62 + dy], fill=col)
        dd.ellipse([S * 0.58 + dx, S * 0.43 + dy, S * 0.80 + dx, S * 0.65 + dy], fill=col)
        dd.rounded_rectangle([S * 0.33 + dx, S * 0.52 + dy, S * 0.77 + dx, S * 0.66 + dy], radius=int(S * 0.07), fill=col)

    cloud_shapes(sd, dx=S * 0.012, dy=S * 0.022)
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img, shadow)
    d = ImageDraw.Draw(img)
    cloud_shapes(d, col=cloud)

    # --- rain streaks under the cloud ---
    rain = (205, 226, 251, 255)  # light blue #cde2fb
    w = int(S * 0.045)
    for bx in (0.40, 0.53, 0.66):
        x1 = S * bx
        y1 = S * 0.70
        d.line([x1, y1, x1 - S * 0.045, y1 + S * 0.115], fill=rain, width=w)

    return img


def main():
    master = make_master()
    icon256 = master.resize((256, 256), Image.LANCZOS)
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    icon256.save(os.path.join(ROOT, "docs", "icon.png"))
    icon256.save(
        os.path.join(ROOT, "icon.ico"),
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print("written icon.ico and docs/icon.png")


if __name__ == "__main__":
    main()
