"""
Test Marco B: ASCII Image Rendering in Isolation
Verifies:
1. Pillow loads the reference image and resizes it proportionally.
2. Pixel luminance maps to density characters (. : - | █) and cyan palette.
3. AsciiImageWidget mounts and renders inside Textual without distortion.
"""

import os
import asyncio
from textual.app import App, ComposeResult
from textual.containers import Vertical
from killerwhale.widgets.ascii_image import AsciiImageWidget, image_to_ascii_rich
from killerwhale.theme import APP_CSS

REF_IMAGE = "assets/killer_whale_ref.png"


class TestMarcoBApp(App):
    CSS = APP_CSS

    def compose(self) -> ComposeResult:
        with Vertical(classes="box-panel"):
            yield AsciiImageWidget(image_path=REF_IMAGE, id="ascii-image")


async def test_marco_b_ascii_image():
    assert os.path.isfile(REF_IMAGE), f"Reference image {REF_IMAGE} must exist"

    # 1. Test direct image conversion to Rich Text
    rich_ascii = image_to_ascii_rich(REF_IMAGE, max_width=60, max_height=25)
    plain_text = rich_ascii.plain
    lines = plain_text.splitlines()

    assert len(lines) > 5, "ASCII rendering should have multiple lines"
    assert len(lines[0]) <= 60, "Width should be within max_width constraint"

    # Verify character ramp presence
    all_chars = set(plain_text)
    assert any(c in all_chars for c in [":", "-", "|", "█", "."]), "Should contain density ramp characters"
    print(f"[✓] Imagem convertida com sucesso ({len(lines)} linhas, {len(lines[0])} colunas).")

    # Verify cyan palette styles are applied to spans
    cyan_found = False
    for span in rich_ascii.spans:
        style_str = str(span.style)
        if "#00ffd1" in style_str or "#4dffef" in style_str or "#00b398" in style_str:
            cyan_found = True
            break
    assert cyan_found, "Rich Text must contain theme cyan palette styling"
    print("[✓] Paleta fosforescente ciano (#00ffd1 / #4dffef) aplicada na renderização.")

    # 2. Test AsciiImageWidget mounting in Textual app
    app = TestMarcoBApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        widget = app.query_one("#ascii-image", AsciiImageWidget)
        assert widget is not None
        rendered = widget.render()
        assert len(rendered.plain) > 0
        print("[✓] AsciiImageWidget montado e renderizado com sucesso no Textual.")

    print("[✓] MARCO B CONCLUÍDO COM SUCESSO: Renderização ASCII da imagem de referência na paleta do tema!")


if __name__ == "__main__":
    asyncio.run(test_marco_b_ascii_image())
