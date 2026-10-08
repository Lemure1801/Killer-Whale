"""
Test Etapa 2: Real-time Reactive Dashboard Telemetry
Verifies that psutil provides genuine system telemetry, the dashboard mounts,
and numbers update reactively over time.
"""

import asyncio
import os
from killerwhale.app import KillerWhaleApp
from killerwhale.screens.dashboard import DashboardScreen
from killerwhale.core.system import take_system_snapshot, set_target, get_target


async def test_dashboard_telemetry():
    # 1. Test direct telemetry acquisition
    snap = take_system_snapshot()
    assert snap.memory_total_mb > 0, "RAM total must be > 0"
    assert snap.disk_total_gb > 0, "Disk total must be > 0"
    assert snap.hostname, "Hostname must not be empty"
    assert snap.kernel, "Kernel must not be empty"
    print(f"[✓] Snapshot coletado: Host={snap.hostname}, RAM={snap.memory_used_mb}/{snap.memory_total_mb}MB, CPU={snap.cpu_percent}%")

    # 2. Test target setter & getter
    test_target_ip = "192.168.100.50"
    set_target(test_target_ip)
    assert get_target() == test_target_ip, "Target must match set value"

    # 3. Test App with DashboardScreen
    app = KillerWhaleApp(legacy=True)
    async with app.run_test() as pilot:

        await pilot.pause()
        dash = app.screen
        assert isinstance(dash, DashboardScreen), f"Expected DashboardScreen, got {type(dash)}"
        
        # Verify initial reactive values populated
        assert dash.active_target == test_target_ip
        assert dash.mem_total > 0
        initial_tick = dash.tick_count
        
        # Advance pilot clock to let interval timer trigger
        await pilot.pause(1.2)
        assert dash.tick_count > initial_tick, "Tick count should increment via reactive timer"
        print(f"[✓] Telemetria atualizada automaticamente: ticks={dash.tick_count}, CPU={dash.cpu_val}%")

        # Clean target
        set_target("")
        dash.update_telemetry()
        assert dash.active_target == "NÃO DEFINIDO"

    print("[✓] Etapa 2 PASS: Dashboard com dados reais de psutil funcionando e atualizando reativamente!")


if __name__ == "__main__":
    asyncio.run(test_dashboard_telemetry())
