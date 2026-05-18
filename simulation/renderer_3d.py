"""Pygame-based 3D digital twin renderer.

This is a lightweight isometric 3D viewer. It shares the same arm model and AI
controller as the 2D simulator, so behavior can be tested in both views.
"""

from __future__ import annotations

from math import cos, radians, sin

import config
from ai.arm_controller import IndustrialAIArmController
from controls.keyboard import handle_keyboard
from simulation.arm import RoboticArm


class Pygame3DRenderer:
    def __init__(self, arm: RoboticArm, ai_controller: IndustrialAIArmController) -> None:
        self.arm = arm
        self.ai_controller = ai_controller
        self.yaw_degrees = -35.0

    def run(self, max_frames: int | None = None) -> None:
        try:
            import pygame
        except ImportError as exc:
            raise SystemExit(
                "pygame is required to run the 3D simulator. Install it with: pip install pygame"
            ) from exc

        pygame.init()
        pygame.display.set_caption("Curiosity Arm - 3D Digital Twin")
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
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.ai_controller.toggle()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                    self.ai_controller.next_target()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.arm.reset()

            keys = pygame.key.get_pressed()
            handle_keyboard(keys, self.arm, pygame)
            if keys[pygame.K_LEFT]:
                self.yaw_degrees -= 1.2
            if keys[pygame.K_RIGHT]:
                self.yaw_degrees += 1.2

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
        screen.fill((13, 18, 20))
        self._draw_floor(screen, pygame)
        self._draw_workcell_targets(screen, pygame)
        self._draw_arm(screen, pygame)
        self._draw_hud(screen, font, small_font, pygame)

    def _draw_floor(self, screen, pygame) -> None:
        for x in range(-360, 401, 80):
            start = self._project((x, -260, 0))
            end = self._project((x, 260, 0))
            pygame.draw.line(screen, (32, 43, 47), start, end, 1)
        for y in range(-280, 281, 80):
            start = self._project((-360, y, 0))
            end = self._project((400, y, 0))
            pygame.draw.line(screen, (32, 43, 47), start, end, 1)

        origin = self._project((0, 0, 0))
        pygame.draw.line(screen, (245, 101, 101), origin, self._project((150, 0, 0)), 3)
        pygame.draw.line(screen, (72, 187, 120), origin, self._project((0, 150, 0)), 3)
        pygame.draw.line(screen, (96, 165, 250), origin, self._project((0, 0, 150)), 3)

    def _draw_workcell_targets(self, screen, pygame) -> None:
        for target in self.ai_controller.targets:
            world = self._screen_target_to_world(target.position)
            point = self._project(world)
            pygame.draw.circle(screen, (93, 124, 133), point, 7, 1)

        if self.arm.target is not None:
            point = self._project(self._screen_target_to_world(self.arm.target))
            pygame.draw.circle(screen, config.TARGET_COLOR, point, 12, 2)
            pygame.draw.line(screen, config.TARGET_COLOR, (point[0] - 10, point[1]), (point[0] + 10, point[1]), 2)
            pygame.draw.line(screen, config.TARGET_COLOR, (point[0], point[1] - 10), (point[0], point[1] + 10), 2)

    def _draw_arm(self, screen, pygame) -> None:
        pose = self.arm.pose
        base = (0.0, 0.0, 0.0)
        elbow = self._screen_point_to_world(pose.elbow.x, pose.elbow.y)
        end = self._screen_point_to_world(pose.end_effector.x, pose.end_effector.y)

        projected_base = self._project(base)
        projected_elbow = self._project(elbow)
        projected_end = self._project(end)

        pygame.draw.circle(screen, (39, 50, 54), projected_base, 42)
        pygame.draw.line(screen, config.ARM_SHADOW_COLOR, projected_base, projected_elbow, 22)
        pygame.draw.line(screen, config.ARM_SHADOW_COLOR, projected_elbow, projected_end, 22)
        pygame.draw.line(screen, config.ARM_COLOR, projected_base, projected_elbow, 13)
        pygame.draw.line(screen, config.ARM_COLOR, projected_elbow, projected_end, 13)
        pygame.draw.circle(screen, config.JOINT_COLOR, projected_base, 20)
        pygame.draw.circle(screen, config.JOINT_COLOR, projected_elbow, 17)
        pygame.draw.circle(screen, config.END_EFFECTOR_COLOR, projected_end, 15)

    def _draw_hud(self, screen, font, small_font, pygame) -> None:
        status = self.ai_controller.status
        lines = [
            "Curiosity Arm 3D Digital Twin",
            f"Mode: {status.mode}",
            f"AI task: {status.action} / {status.target_name}",
            f"Confidence: {status.confidence:.2f}",
            f"Shoulder: {self.arm.shoulder.angle_degrees:7.2f} deg",
            f"Elbow:    {self.arm.elbow.angle_degrees:7.2f} deg",
            "SPACE AI on/off  TAB next task  LEFT/RIGHT rotate view  Q/W A/S manual",
        ]
        x, y = 24, 22
        for index, line in enumerate(lines):
            active_font = font if index == 0 else small_font
            color = config.TEXT_COLOR if index == 0 else config.MUTED_TEXT_COLOR
            surface = active_font.render(line, True, color)
            screen.blit(surface, (x, y))
            y += 28 if index == 0 else 22

    def _screen_point_to_world(self, x: float, y: float) -> tuple[float, float, float]:
        dx = x - self.arm.base[0]
        z = self.arm.base[1] - y
        return dx, 0.0, z

    def _screen_target_to_world(self, target: tuple[float, float]) -> tuple[float, float, float]:
        return self._screen_point_to_world(target[0], target[1])

    def _project(self, point: tuple[float, float, float]) -> tuple[int, int]:
        x, y, z = point
        yaw = radians(self.yaw_degrees)
        rotated_x = x * cos(yaw) - y * sin(yaw)
        rotated_y = x * sin(yaw) + y * cos(yaw)
        camera_distance = 900
        scale = camera_distance / (camera_distance + rotated_y)
        screen_x = config.SCREEN_WIDTH / 2 + rotated_x * scale
        screen_y = config.SCREEN_HEIGHT * 0.68 - z * scale - rotated_y * 0.22 * scale
        return round(screen_x), round(screen_y)
