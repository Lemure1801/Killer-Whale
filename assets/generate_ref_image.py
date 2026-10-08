"""
Generates the official KillerWhale reference image for ASCII rendering.
Creates a high-contrast geometric cyber-orca emblem with gradient depths.
"""

import math
from PIL import Image, ImageDraw


def generate_reference_image(path: str = "assets/killer_whale_ref.png") -> str:
    width, height = 400, 240
    img = Image.new("L", (width, height), color=0)
    draw = ImageDraw.Draw(img)

    cx, cy = width // 2, height // 2

    # Draw gradient circular radar background
    for r in range(110, 10, -8):
        lum = int(25 * (1 - r / 110))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=lum, width=1)

    # Draw cyber grid lines
    for x in range(20, width, 40):
        draw.line([(x, 20), (x, height - 20)], fill=18, width=1)
    for y in range(20, height, 40):
        draw.line([(20, y), (width - 20, y)], fill=18, width=1)

    # Draw Orca Body Silhouette (Curved organic aerodynamic whale shape)
    # Dorsal fin, body curve, rostrum, tail fluke
    body_points = [
        (cx - 150, cy + 20),   # Snout / rostrum
        (cx - 100, cy - 35),   # Forehead / melon
        (cx - 40, cy - 45),    # Back before dorsal
        (cx - 10, cy - 100),   # Dorsal fin tip
        (cx + 25, cy - 40),    # Dorsal fin trailing edge
        (cx + 100, cy - 20),   # Tail stock upper
        (cx + 140, cy - 50),   # Upper fluke tip
        (cx + 125, cy),        # Fluke notch
        (cx + 145, cy + 45),   # Lower fluke tip
        (cx + 90, cy + 15),    # Tail stock lower
        (cx + 10, cy + 40),    # Belly / keel
        (cx - 30, cy + 70),    # Pectoral fin tip
        (cx - 60, cy + 35),    # Pectoral fin base
        (cx - 110, cy + 30),   # Lower jaw
    ]

    # Fill body with bright base
    draw.polygon(body_points, fill=220)

    # Eye patch (white patch characteristic of orcas)
    draw.ellipse([cx - 95, cy - 18, cx - 65, cy - 3], fill=255)

    # Saddle patch behind dorsal fin
    draw.polygon([(cx + 20, cy - 30), (cx + 55, cy - 15), (cx + 35, cy - 5)], fill=175)

    # Ventral white contour (chin to belly)
    draw.polygon([
        (cx - 130, cy + 22),
        (cx - 70, cy + 20),
        (cx - 10, cy + 30),
        (cx + 60, cy + 12),
        (cx + 30, cy + 28),
        (cx - 50, cy + 33),
    ], fill=255)

    # Cybernetic targeting reticle / crosshairs
    draw.ellipse([cx - 80, cy - 10, cx - 80 + 20, cy - 10 + 20], outline=240, width=2)
    draw.line([(cx - 70, cy - 15), (cx - 70, cy + 15)], fill=240, width=1)
    draw.line([(cx - 85, cy), (cx - 55, cy)], fill=240, width=1)

    # Outer border
    draw.rectangle([5, 5, width - 6, height - 6], outline=120, width=2)

    img.save(path)
    return path


if __name__ == "__main__":
    p = generate_reference_image()
    print("Reference image generated:", p)
