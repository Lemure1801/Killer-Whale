"""
Test Etapa 1: Lifecycle and Proof of Life
Verifies that the Textual application mounts, displays widgets, and terminates on 'q'.
"""

import asyncio
from killerwhale.app import KillerWhaleApp


async def test_app_lifecycle():
    app = KillerWhaleApp()
    async with app.run_test() as pilot:
        # Check that app mounted
        assert app.is_running
        assert app.title == "KillerWhale OS"
        # Verify press 'q' exits
        await pilot.press("q")
        # Ensure it transitions to stopped
        await pilot.pause()
        assert not app.is_running
    print("[✓] Etapa 1 PASS: App iniciou, renderizou e encerrou com 'q'.")


if __name__ == "__main__":
    asyncio.run(test_app_lifecycle())
