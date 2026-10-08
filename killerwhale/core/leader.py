"""
KillerWhale — Leader Key Engine (TAB Command Prefix)
Implements tmux/modal style leader-key system where TAB enters command mode
for 1.5s, intercepting default focus navigation and dispatching combos.
"""

import time
from typing import Callable, Optional, Dict
from textual.events import Key


class LeaderKeyManager:
    """
    Manages the TAB leader key state machine.
    
    When TAB is pressed, leader mode is engaged for `timeout` seconds.
    The subsequent keypress is intercepted and mapped to registered actions.
    If no key follows within `timeout` seconds, leader mode automatically expires.
    """

    def __init__(self, timeout: float = 1.5, on_state_change: Optional[Callable[[bool], None]] = None):
        self.timeout = timeout
        self.is_active = False
        self.activated_at: float = 0.0
        self.on_state_change = on_state_change
        self._actions: Dict[str, Callable[[], None]] = {}
        self._digit_action: Optional[Callable[[int], None]] = None

    def register_action(self, key_combo: str, callback: Callable[[], None]) -> None:
        """Registers a callback for a specific key combo after TAB."""
        self._actions[key_combo.lower()] = callback

    def register_digit_action(self, callback: Callable[[int], None]) -> None:
        """Registers a callback for TAB + 0..9."""
        self._digit_action = callback

    def activate(self) -> None:
        """Enters leader mode and resets timeout counter."""
        self.is_active = True
        self.activated_at = time.time()
        if self.on_state_change:
            self.on_state_change(True)

    def deactivate(self) -> None:
        """Exits leader mode."""
        if self.is_active:
            self.is_active = False
            if self.on_state_change:
                self.on_state_change(False)

    def check_timeout(self) -> bool:
        """Checks if current leader mode has timed out."""
        if self.is_active and (time.time() - self.activated_at >= self.timeout):
            self.deactivate()
            return True
        return False

    def handle_key(self, event: Key) -> bool:
        """
        Intercepts keys.
        Returns True if the key was handled (consumed by leader mechanism).
        """
        # 1. TAB key activates leader mode
        if event.key == "tab":
            event.prevent_default()
            event.stop()
            self.activate()
            return True

        # 2. If leader is not active, do not intercept
        if not self.is_active:
            return False

        # 3. Check for timeout before processing
        if self.check_timeout():
            return False

        # 4. Consume this key as the second chord of leader combination
        event.prevent_default()
        event.stop()
        consumed = False

        # Normalize key representation
        key_name = event.key.lower()

        # Handle TAB + 0..9
        if key_name.isdigit() and self._digit_action:
            digit = int(key_name)
            self._digit_action(digit)
            consumed = True

        # Check for registered key combos
        # Note: In terminals, Ctrl+/ is often reported as ctrl+slash or ctrl+_
        elif key_name in self._actions:
            self._actions[key_name]()
            consumed = True
        elif key_name == "ctrl+_" and "ctrl+slash" in self._actions:
            self._actions["ctrl+slash"]()
            consumed = True
        elif (key_name in ("question_mark", "shift+slash", "?")) and "shift+slash" in self._actions:
            self._actions["shift+slash"]()
            consumed = True
        elif (key_name in ("l", "shift+l")) and "shift+l" in self._actions:
            self._actions["shift+l"]()
            consumed = True

        # After processing chord, leader mode is finished
        self.deactivate()
        return True
