"""
KillerWhale — Reusable ASCII Image Rendering Widget
Uses Pillow to map image luminance into density characters (. : | █) and
applies the phosphorescent cyan (#00FFD1 / #4DFFEF) theme palette.
"""

import os
from typing import Optional, List, Tuple
from PIL import Image
from rich.text import Text
from textual.widget import Widget
from textual.reactive import reactive


# Luminance character ramp from lowest to highest
ASCII_RAMP = " .:-=+*#%@█"

# Palette colors corresponding to luminance tiers (dark black/cyan -> vibrant glowing cyan/white)
# Exact phosphorescent cyan/seafoam palette tiers
COLOR_TIERS: List[Tuple[int, str, str]] = [
    # (max_lum, char, hex_color)
    (24,  " ", "#000000"),
    (55,  ".", "#002b24"),
    (85,  ":", "#00473b"),
    (115, "-", "#006b59"),
    (145, "+", "#008f77"),
    (175, "=", "#00b398"),
    (205, "|", "#00d9b7"),
    (235, "#", "#00ffd1"),  # Primary phosphorescent cyan
    (255, "█", "#4dffef"),  # Vibrant bright cyan highlight
]


def image_to_ascii_rich(image_path: str, max_width: int, max_height: int) -> Text:
    """
    Loads an image from image_path, scales it preserving aspect ratio with
    character height compensation (~0.5), and returns a colored Rich Text object.
    """
    if not os.path.isfile(image_path):
        err = Text()
        err.append(f"[!] Imagem não encontrada: {image_path}", style="bold #ff3355")
        return err

    try:
        with Image.open(image_path) as img:
            img = img.convert("L")
            orig_w, orig_h = img.size

            if orig_w == 0 or orig_h == 0 or max_width <= 0 or max_height <= 0:
                return Text("")

            # Terminal character aspect ratio correction: characters are roughly twice as tall as wide.
            # Thus, we multiply height by 0.5 to keep 1:1 visual aspect ratio.
            aspect = (orig_h / orig_w) * 0.5
            target_w = max_width
            target_h = int(target_w * aspect)

            # Fit into max_height if needed
            if target_h > max_height:
                target_h = max_height
                target_w = int(target_h / aspect) if aspect > 0 else max_width

            target_w = max(1, target_w)
            target_h = max(1, target_h)

            resized = img.resize((target_w, target_h), Image.Resampling.BILINEAR)

            rich_text = Text()
            for y in range(target_h):
                for x in range(target_w):
                    lum = resized.getpixel((x, y))
                    char = " "
                    color = "#000000"
                    for max_lum, c, col in COLOR_TIERS:
                        if lum <= max_lum:
                            char = c
                            color = col
                            break
                    rich_text.append(char, style=f"bold {color}" if lum > 175 else color)
                if y < target_h - 1:
                    rich_text.append("\n")

            return rich_text

    except Exception as e:
        err = Text()
        err.append(f"[!] Erro ao converter imagem em ASCII: {e}", style="bold #ff3355")
        return err


class AsciiImageWidget(Widget):
    """Textual widget that renders an image as colored phosphorescent cyan ASCII art."""

    DEFAULT_CSS = """
    AsciiImageWidget {
        width: 100%;
        height: 100%;
        content-align: center middle;
        background: #000000;
    }
    """

    image_path = reactive("")

    def __init__(self, image_path: str = "assets/killer_whale_ref.png", **kwargs):
        super().__init__(**kwargs)
        self.image_path = image_path
        self._rendered_text: Optional[Text] = None

    def render(self) -> Text:
        w = max(10, self.size.width - 2)
        h = max(5, self.size.height - 2)
        return image_to_ascii_rich(self.image_path, max_width=w, max_height=h)

    def on_resize(self) -> None:
        self.refresh()
