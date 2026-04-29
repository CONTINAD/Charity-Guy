"""Generate mascot derivative assets for the Just a Charity Guy site."""
from PIL import Image, ImageDraw, ImageFilter
import os

ROOT = "/Users/alexaustin/Desktop/Charity"
SRC  = os.path.join(ROOT, "mascot.png")

src = Image.open(SRC).convert("RGBA")
W, H = src.size
print(f"source: {W}x{H}")

# ---------- helper: remove cream background -> alpha ----------
# The original has an ~#ede1c8 cream backdrop. Knock it out so the dog stands free.
def remove_cream(img: Image.Image, target=(201, 186, 158), tol=22):
    """Knock out the cream backdrop. Uses flood-fill from the corners
    so we only remove background-connected cream, not cream-ish pixels
    inside the dog (e.g. text/highlights)."""
    import numpy as np
    img = img.convert("RGBA")
    arr = np.array(img)
    r, g, b = arr[..., 0].astype(int), arr[..., 1].astype(int), arr[..., 2].astype(int)
    # broad cream mask
    cream_mask = (
        (np.abs(r - target[0]) < tol) &
        (np.abs(g - target[1]) < tol) &
        (np.abs(b - target[2]) < tol)
    )
    # flood from ALL edge pixels through cream pixels only
    h, w = cream_mask.shape
    visited = np.zeros_like(cream_mask, dtype=bool)
    from collections import deque
    q = deque()
    for x in range(w):
        if cream_mask[0, x] and not visited[0, x]: visited[0, x] = True; q.append((0, x))
        if cream_mask[h-1, x] and not visited[h-1, x]: visited[h-1, x] = True; q.append((h-1, x))
    for y in range(h):
        if cream_mask[y, 0] and not visited[y, 0]: visited[y, 0] = True; q.append((y, 0))
        if cream_mask[y, w-1] and not visited[y, w-1]: visited[y, w-1] = True; q.append((y, w-1))
    while q:
        y, x = q.popleft()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ny, nx = y+dy, x+dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx] and cream_mask[ny, nx]:
                visited[ny, nx] = True
                q.append((ny, nx))
    # also convert any STRICTLY cream pixel (smaller tol) anywhere — safe inside the dog
    # since the dog has no near-#ede1c8 fills (body is yellow-tan, much warmer)
    strict = (
        (np.abs(r - target[0]) < 18) &
        (np.abs(g - target[1]) < 18) &
        (np.abs(b - target[2]) < 18)
    )
    bg_mask = visited | strict
    arr[..., 3] = np.where(bg_mask, 0, 255).astype("uint8")
    return Image.fromarray(arr, "RGBA")

cutout = remove_cream(src)
cutout.save(os.path.join(ROOT, "mascot_cutout.png"), optimize=True)
print("✓ mascot_cutout.png")

# ---------- bounding box crop (tight) ----------
bbox = cutout.getbbox()
tight = cutout.crop(bbox)
tight.save(os.path.join(ROOT, "mascot_tight.png"), optimize=True)
print(f"✓ mascot_tight.png ({tight.size})")

# ---------- HEAD crop (tight square around the head) ----------
# Hand-tuned crop coordinates against the ORIGINAL 1619x971 image
# (after cream cutout but BEFORE bbox-tightening)
HEAD_BOX = (470, 20, 1170, 560)   # left, top, right, bottom
head_full = cutout.crop(HEAD_BOX)
# pad to square so badges/coins look balanced
hw, hh = head_full.size
side = max(hw, hh)
head = Image.new("RGBA", (side, side), (0, 0, 0, 0))
head.paste(head_full, ((side - hw)//2, (side - hh)//2), head_full)
head.save(os.path.join(ROOT, "mascot_head.png"), optimize=True)
print(f"✓ mascot_head.png ({head.size})")

# ---------- circular badge (head in a circle, cream background) ----------
def circle_badge(img: Image.Image, size=512, bg=(237, 225, 200), ring=(20, 20, 15), ring_w=18):
    # fit the source into a square canvas
    canvas = Image.new("RGBA", (size, size), bg + (255,))
    # scale source to fit
    s = img.copy()
    s.thumbnail((size - ring_w*2 - 30, size - ring_w*2 - 30), Image.LANCZOS)
    sx = (size - s.width) // 2
    sy = (size - s.height) // 2 + 20  # nudge down so head is centered
    canvas.paste(s, (sx, sy), s)
    # circular mask
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse((0, 0, size, size), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(canvas, (0, 0), mask)
    # draw outline ring
    d = ImageDraw.Draw(out)
    d.ellipse((ring_w//2, ring_w//2, size - ring_w//2, size - ring_w//2),
              outline=ring, width=ring_w)
    return out

badge = circle_badge(head, size=600)
badge.save(os.path.join(ROOT, "mascot_badge.png"), optimize=True)
print("✓ mascot_badge.png")

# small version for favicon / logo
badge_sm = circle_badge(head, size=128, ring_w=8)
badge_sm.save(os.path.join(ROOT, "mascot_logo.png"), optimize=True)
print("✓ mascot_logo.png")

# favicon
fav = circle_badge(head, size=64, ring_w=4)
fav.save(os.path.join(ROOT, "favicon.png"), optimize=True)
print("✓ favicon.png")

# ---------- silhouette / sticker (single-color) ----------
def silhouette(img: Image.Image, color=(45, 90, 61)):
    a = img.split()[-1]
    base = Image.new("RGBA", img.size, color + (0,))
    base.putalpha(a)
    return base

sil_green = silhouette(tight, (45, 90, 61))
sil_green.save(os.path.join(ROOT, "mascot_silhouette_green.png"), optimize=True)
print("✓ mascot_silhouette_green.png")

sil_coral = silhouette(tight, (232, 93, 58))
sil_coral.save(os.path.join(ROOT, "mascot_silhouette_coral.png"), optimize=True)
print("✓ mascot_silhouette_coral.png")

# ---------- sticker version: outlined cutout with halo ----------
def sticker(img: Image.Image, halo=(245, 234, 215), halo_w=14, outline=(20, 20, 15), outline_w=5):
    a = img.split()[-1]
    # dilate alpha to create halo
    halo_mask = a.filter(ImageFilter.MaxFilter(halo_w * 2 + 1))
    # outline mask = halo - original (just the rim) — we use an additional dilate
    out_mask  = a.filter(ImageFilter.MaxFilter(halo_w * 2 + 1 + outline_w * 2))
    canvas_size = img.size
    out = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    # outline (black) layer
    blk = Image.new("RGBA", canvas_size, outline + (0,))
    blk.putalpha(out_mask)
    out = Image.alpha_composite(out, blk)
    # halo (cream) layer
    hlo = Image.new("RGBA", canvas_size, halo + (0,))
    hlo.putalpha(halo_mask)
    out = Image.alpha_composite(out, hlo)
    # original on top
    out = Image.alpha_composite(out, img)
    return out

sticker_img = sticker(tight)
sticker_img.save(os.path.join(ROOT, "mascot_sticker.png"), optimize=True)
print("✓ mascot_sticker.png")

# ---------- pattern tile (small mascot heads tiled, used as repeating bg) ----------
def make_pattern(head_img, tile=240, bg=(45, 90, 61), accent=(74, 157, 95)):
    head_small = head_img.copy()
    head_small.thumbnail((tile - 40, tile - 40), Image.LANCZOS)
    canvas = Image.new("RGBA", (tile * 2, tile * 2), bg + (255,))
    # subtle dotted halftone via accent dots
    d = ImageDraw.Draw(canvas)
    for y in range(0, tile * 2, 18):
        for x in range(0, tile * 2, 18):
            d.ellipse((x, y, x+4, y+4), fill=accent + (160,))
    # paste 4 heads in offset grid
    positions = [
        ((tile - head_small.width)//2,                       (tile - head_small.height)//2),
        (tile + (tile - head_small.width)//2,                 (tile - head_small.height)//2),
        ((tile - head_small.width)//2,                        tile + (tile - head_small.height)//2),
        (tile + (tile - head_small.width)//2,                 tile + (tile - head_small.height)//2),
    ]
    rotations = [-8, 6, 7, -5]
    for (px, py), rot in zip(positions, rotations):
        rotated = head_small.rotate(rot, resample=Image.BICUBIC, expand=True)
        # offset the staggered ones
        canvas.alpha_composite(rotated, (px, py))
    return canvas

pattern = make_pattern(head, tile=280)
pattern.save(os.path.join(ROOT, "pattern_heads.png"), optimize=True)
print("✓ pattern_heads.png")

# ---------- "OG" stamped portrait (square, halftone bg, sticker frame) ----------
def og_card(head_img, size=720,
            bg=(245, 234, 215), accent=(185, 224, 194), frame=(20, 20, 15)):
    canvas = Image.new("RGBA", (size, size), bg + (255,))
    d = ImageDraw.Draw(canvas)
    # halftone dots
    for y in range(0, size, 18):
        for x in range(0, size, 18):
            ox = 9 if (y // 18) % 2 else 0
            d.ellipse((x+ox, y, x+ox+6, y+6), fill=accent + (255,))
    # paste head
    h = head_img.copy()
    h.thumbnail((int(size*0.86), int(size*0.86)), Image.LANCZOS)
    canvas.alpha_composite(h, ((size - h.width)//2, (size - h.height)//2 + 20))
    # frame
    d2 = ImageDraw.Draw(canvas)
    d2.rectangle((6, 6, size-6, size-6), outline=frame, width=8)
    return canvas

og = og_card(tight, size=800)
og.save(os.path.join(ROOT, "mascot_card.png"), optimize=True)
print("✓ mascot_card.png")

# ---------- coin: circular gold-y green coin with mascot head ----------
def coin(head_img, size=600):
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    # outer coin
    d.ellipse((0, 0, size, size), fill=(244, 207, 46, 255), outline=(20, 20, 15), width=10)
    # inner ring
    pad = 36
    d.ellipse((pad, pad, size-pad, size-pad), fill=(74, 157, 95, 255),
              outline=(20, 20, 15), width=6)
    # paste head clipped to inner circle
    inner_size = size - pad*2 - 20
    h = head_img.copy()
    h.thumbnail((inner_size, inner_size), Image.LANCZOS)
    mask = Image.new("L", (inner_size, inner_size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, inner_size, inner_size), fill=255)
    inner_canvas = Image.new("RGBA", (inner_size, inner_size), (185, 224, 194, 255))
    inner_canvas.alpha_composite(h, ((inner_size - h.width)//2, (inner_size - h.height)//2 + 10))
    inner_canvas.putalpha(mask)
    canvas.alpha_composite(inner_canvas, (pad+10, pad+10))
    # add small text marks (top/bottom) — draw small filled wedges as decoration
    return canvas

coin_img = coin(head, size=600)
coin_img.save(os.path.join(ROOT, "coin.png"), optimize=True)
print("✓ coin.png")

print("\nAll assets generated.")
