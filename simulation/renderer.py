"""Pygame rendering and application loop."""

from __future__ import annotations

import math

import config
from ai.arm_controller import IndustrialAIArmController
from controls.keyboard import handle_keyboard
from simulation.arm import RoboticArm


class PygameRenderer:
    def __init__(
        self,
        arm: RoboticArm,
        ai_controller: IndustrialAIArmController | None = None,
        start_ai: bool = False,
    ) -> None:
        self.arm = arm
        self.ai_controller = ai_controller or IndustrialAIArmController(arm)
        self.ai_controller.set_enabled(start_ai)

    def run(self, max_frames: int | None = None) -> None:
        try:
            import pygame
        except ImportError as exc:
            raise SystemExit(
                "pygame is required to run the simulator. Install it with: pip install pygame"
            ) from exc

        pygame.init()
        pygame.display.set_caption("Curiosity Arm - Robotics Simulator")
        screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Segoe UI", 18)
        small_font = pygame.font.SysFont("Segoe UI", 14)

        running = True
        frame_count = 0
        while running:
            dt = clock.get_time() / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.arm.reset()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.ai_controller.toggle()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                    self.ai_controller.next_target()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.arm.set_target(event.pos)
                    self.ai_controller.set_enabled(False)

            keys = pygame.key.get_pressed()
            handle_keyboard(keys, self.arm, pygame)
            self.ai_controller.update(dt)
            self.arm.update()

            self._draw(screen, font, small_font, pygame)
            pygame.display.flip()
            clock.tick(config.FPS)
            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                running = False

        pygame.quit()

    def _draw(self, screen, font, small_font, pygame) -> None:
        screen.fill(config.BACKGROUND_COLOR)
        self._draw_grid(screen, pygame)
        self._draw_reach_circle(screen, pygame)
        self._draw_target(screen, pygame)
        self._draw_arm(screen, pygame)
        self._draw_hud(screen, font, small_font, pygame)

    def _draw_grid(self, screen, pygame) -> None:
        for x in range(0, config.SCREEN_WIDTH, 40):
            pygame.draw.line(screen, config.GRID_COLOR, (x, 0), (x, config.SCREEN_HEIGHT), 1)
        for y in range(0, config.SCREEN_HEIGHT, 40):
            pygame.draw.line(screen, config.GRID_COLOR, (0, y), (config.SCREEN_WIDTH, y), 1)

    def _draw_reach_circle(self, screen, pygame) -> None:
        pygame.draw.circle(
            screen,
            (31, 62, 66),
            self.arm.base,
            round(self.arm.max_reach),
            1,
        )

    def _draw_target(self, screen, pygame) -> None:
        if self.arm.target is None:
            return

        color = config.TARGET_COLOR
        if self.arm.last_ik_result and not self.arm.last_ik_result.reachable:
            color = config.UNREACHABLE_COLOR

        x, y = round(self.arm.target[0]), round(self.arm.target[1])
        pygame.draw.line(screen, color, (x - 12, y), (x + 12, y), 2)
        pygame.draw.line(screen, color, (x, y - 12), (x, y + 12), 2)
        pygame.draw.circle(screen, color, (x, y), 16, 1)

    def _draw_arm(self, screen, pygame) -> None:
        pose = self.arm.pose
        base = pose.base.as_int_tuple()
        elbow = pose.elbow.as_int_tuple()
        end = pose.end_effector.as_int_tuple()

        pygame.draw.line(screen, config.ARM_SHADOW_COLOR, base, elbow, 18)
        pygame.draw.line(screen, config.ARM_SHADOW_COLOR, elbow, end, 18)
        pygame.draw.line(screen, config.ARM_COLOR, base, elbow, 10)
        pygame.draw.line(screen, config.ARM_COLOR, elbow, end, 10)

        pygame.draw.circle(screen, config.JOINT_COLOR, base, 18)
        pygame.draw.circle(screen, config.BACKGROUND_COLOR, base, 8)
        pygame.draw.circle(screen, config.JOINT_COLOR, elbow, 15)
        pygame.draw.circle(screen, config.BACKGROUND_COLOR, elbow, 6)
        pygame.draw.circle(screen, config.END_EFFECTOR_COLOR, end, 13)
        pygame.draw.circle(screen, config.BACKGROUND_COLOR, end, 5)

    def _draw_hud(self, screen, font, small_font, pygame) -> None:
        pose = self.arm.pose
        status = self.ai_controller.status
        lines = [
            "Curiosity Arm AI Controller - 2D Digital Twin",
            f"Mode:     {status.mode}",
            f"AI task:  {status.action} / {status.target_name}",
            f"Confidence: {status.confidence:.2f}",
            f"Shoulder: {self.arm.shoulder.angle_degrees:7.2f} deg",
            f"Elbow:    {self.arm.elbow.angle_degrees:7.2f} deg",
            f"End:      ({pose.end_effector.x:7.1f}, {pose.end_effector.y:7.1f})",
            "SPACE AI on/off  TAB next AI task  Click manual target  Q/W A/S manual  R reset",
        ]

        if self.arm.last_ik_result:
            reach_text = "reachable" if self.arm.last_ik_result.reachable else "out of reach"
            lines.insert(4, f"Target:   {reach_text}, {self.arm.last_ik_result.distance:7.1f}px")

        x, y = 24, 22
        for index, line in enumerate(lines):
            active_font = font if index == 0 else small_font
            color = config.TEXT_COLOR if index == 0 else config.MUTED_TEXT_COLOR
            surface = active_font.render(line, True, color)
            screen.blit(surface, (x, y))
            y += 28 if index == 0 else 22

        self._draw_angle_arcs(screen, small_font, pygame)

    def _draw_angle_arcs(self, screen, small_font, pygame) -> None:
        center = self.arm.base
        radius = 54
        angle = math.radians(self.arm.shoulder.angle_degrees)
        end = (
            round(center[0] + radius * math.cos(angle)),
            round(center[1] + radius * math.sin(angle)),
        )
        pygame.draw.line(screen, config.JOINT_COLOR, center, end, 2)
        surface = small_font.render("base", True, config.MUTED_TEXT_COLOR)
        screen.blit(surface, (center[0] - 16, center[1] + 26))
