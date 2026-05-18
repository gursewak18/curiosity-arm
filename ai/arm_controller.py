"""Autonomous AI-style controller for Curiosity Arm.

This module is intentionally camera-free for now. It simulates the output of an
AI perception system, then drives the same arm API that real hand tracking,
object detection, or voice commands will use later.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, sin, tau

from simulation.arm import RoboticArm


@dataclass(frozen=True)
class WorkCellTarget:
    name: str
    position: tuple[float, float]
    action: str


@dataclass(frozen=True)
class ControllerStatus:
    mode: str
    target_name: str
    action: str
    confidence: float


class IndustrialAIArmController:
    """Small autonomous controller that behaves like an AI planning layer."""

    def __init__(self, arm: RoboticArm) -> None:
        self.arm = arm
        base_x, base_y = arm.base
        self.targets = [
            WorkCellTarget("scan point", (base_x + 40, base_y - 240), "inspect"),
            WorkCellTarget("part A", (base_x + 235, base_y - 90), "pick"),
            WorkCellTarget("quality zone", (base_x + 110, base_y - 285), "verify"),
            WorkCellTarget("output bin", (base_x - 215, base_y - 115), "place"),
            WorkCellTarget("home", (base_x + 220, base_y + 20), "standby"),
        ]
        self.enabled = False
        self.elapsed = 0.0
        self.target_index = 0
        self.status = ControllerStatus("manual", "none", "idle", 0.0)

    def toggle(self) -> None:
        self.enabled = not self.enabled
        if not self.enabled:
            self.status = ControllerStatus("manual", "none", "idle", 0.0)

    def set_enabled(self, enabled: bool) -> None:
        if self.enabled != enabled:
            self.toggle()

    def next_target(self) -> None:
        self.target_index = (self.target_index + 1) % len(self.targets)
        self._publish_current_target()

    def update(self, dt: float) -> None:
        if not self.enabled:
            return

        self.elapsed += dt
        if self.elapsed >= 2.6:
            self.elapsed = 0.0
            self.target_index = (self.target_index + 1) % len(self.targets)

        self._publish_current_target()

    def _publish_current_target(self) -> None:
        target = self.targets[self.target_index]
        drift = self._inspection_drift() if target.action == "inspect" else (0.0, 0.0)
        position = (target.position[0] + drift[0], target.position[1] + drift[1])
        result = self.arm.solve_target(position)
        confidence = 0.94 if result.reachable else 0.41

        self.arm.set_target(position)
        self.status = ControllerStatus(
            mode="AI autonomous",
            target_name=target.name,
            action=target.action,
            confidence=confidence,
        )

    def _inspection_drift(self) -> tuple[float, float]:
        phase = self.elapsed / 2.6 * tau
        return cos(phase) * 24, sin(phase) * 14

