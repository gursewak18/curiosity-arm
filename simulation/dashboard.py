"""Unified interactive dashboard for Curiosity Arm."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin

import config
from ai.arm_controller import IndustrialAIArmController
from controls.keyboard import handle_keyboard
from simulation.arm import RoboticArm


@dataclass(frozen=True)
class Button:
    label: str
    rect: tuple[int, int, int, int]
    action: str


class CuriosityArmDashboard:
    """Single control-room interface for simulation, AI control, and testing."""

    def __init__(self, arm: RoboticArm, ai_controller: IndustrialAIArmController) -> None:
        self.arm = arm
        self.ai_controller = ai_controller
        self.yaw_degrees = -35.0
        self.hardware_sim_enabled = True
        self.active_view = "2d"
        self.buttons = [
            Button("2D VIEW", (24, 82, 112, 38), "view_2d"),
            Button("3D VIEW", (146, 82, 112, 38), "view_3d"),
            Button("AI ON/OFF", (28, 626, 132, 42), "toggle_ai"),
            Button("NEXT TASK", (174, 626, 132, 42), "next_task"),
            Button("RESET", (320, 626, 104, 42), "reset"),
            Button("HW SIM", (438, 626, 104, 42), "toggle_hw"),
        ]

    def run(self, max_frames: int | None = None) -> None:
        try:
            import pygame
        except ImportError as exc:
            raise SystemExit(
                "pygame is required to run the dashboard. Install it with: pip install pygame"
            ) from exc

        pygame.init()
        pygame.display.set_caption("Curiosity Arm - AI Robotics Control Interface")
        screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Segoe UI", 18)
        small_font = pygame.font.SysFont("Segoe UI", 14)
        tiny_font = pygame.font.SysFont("Segoe UI", 12)

        running = True
        frame_count = 0
        while running:
            dt = clock.get_time() / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.ai_controller.toggle()
                    elif event.key == pygame.K_TAB:
                        self.ai_controller.next_target()
                    elif event.key == pygame.K_r:
                        self.arm.reset()
                    elif event.key == pygame.K_1:
                        self.active_view = "2d"
                    elif event.key == pygame.K_2:
                        self.active_view = "3d"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(event.pos)

            keys = pygame.key.get_pressed()
            handle_keyboard(keys, self.arm, pygame)
            if keys[pygame.K_LEFT]:
                self.yaw_degrees -= 1.2
            if keys[pygame.K_RIGHT]:
                self.yaw_degrees += 1.2

            self.ai_controller.update(dt)
            self.arm.update()
            self._draw(screen, font, small_font, tiny_font, pygame)
            pygame.display.flip()
            clock.tick(config.FPS)

            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                running = False

        pygame.quit()

    def _handle_click(self, position: tuple[int, int]) -> None:
        for button in self.buttons:
            if point_in_rect(position, button.rect):
                self._run_button_action(button.action)
                return

        if self.active_view == "2d" and point_in_rect(position, self._workspace_rect()):
            self.ai_controller.set_enabled(False)
            self.arm.set_target(position)

    def _run_button_action(self, action: str) -> None:
        if action == "toggle_ai":
            self.ai_controller.toggle()
        elif action == "view_2d":
            self.active_view = "2d"
        elif action == "view_3d":
            self.active_view = "3d"
        elif action == "next_task":
            self.ai_controller.next_target()
        elif action == "reset":
            self.arm.reset()
        elif action == "toggle_hw":
            self.hardware_sim_enabled = not self.hardware_sim_enabled

    def _draw(self, screen, font, small_font, tiny_font, pygame) -> None:
        screen.fill((12, 17, 19))
        self._draw_header(screen, font, small_font, pygame)
        self._draw_view_tabs(screen, tiny_font, pygame)
        title = "2D SIMULATION" if self.active_view == "2d" else "3D DIGITAL TWIN"
        self._draw_panel(screen, self._workspace_rect(), title, small_font, pygame)
        if self.active_view == "2d":
            self._draw_2d_view(screen, small_font, pygame)
        else:
            self._draw_3d_view(screen, small_font, pygame)
        self._draw_bottom_console(screen, small_font, tiny_font, pygame)

    def _draw_header(self, screen, font, small_font, pygame) -> None:
        status = self.ai_controller.status
        title = font.render("Curiosity Arm AI Robotics Control Interface", True, config.TEXT_COLOR)
        screen.blit(title, (24, 22))
        subtitle = small_font.render(
            f"Mode: {status.mode}   Task: {status.action} / {status.target_name}   Confidence: {status.confidence:.2f}",
            True,
            config.MUTED_TEXT_COLOR,
        )
        screen.blit(subtitle, (24, 54))

        state_color = config.REACHABLE_COLOR if self.ai_controller.enabled else config.UNREACHABLE_COLOR
        pygame.draw.circle(screen, state_color, (1038, 34), 8)
        label = small_font.render("AI", True, config.TEXT_COLOR)
        screen.blit(label, (1050, 25))

    def _draw_view_tabs(self, screen, font, pygame) -> None:
        for button in self.buttons[:2]:
            active = (
                button.action == "view_2d"
                and self.active_view == "2d"
                or button.action == "view_3d"
                and self.active_view == "3d"
            )
            color = (34, 87, 69) if active else (33, 45, 49)
            pygame.draw.rect(screen, color, button.rect, border_radius=5)
            pygame.draw.rect(screen, (83, 101, 107), button.rect, 1, border_radius=5)
            label = font.render(button.label, True, config.TEXT_COLOR)
            label_rect = label.get_rect(
                center=(button.rect[0] + button.rect[2] / 2, button.rect[1] + button.rect[3] / 2)
            )
            screen.blit(label, label_rect)

    def _draw_panel(self, screen, rect: tuple[int, int, int, int], title: str, font, pygame) -> None:
        x, y, width, height = rect
        pygame.draw.rect(screen, (18, 25, 28), rect, border_radius=6)
        pygame.draw.rect(screen, (45, 58, 63), rect, 1, border_radius=6)
        surface = font.render(title, True, config.MUTED_TEXT_COLOR)
        screen.blit(surface, (x + 16, y + 12))
        pygame.draw.line(screen, (45, 58, 63), (x, y + 42), (x + width, y + 42), 1)

    def _draw_2d_view(self, screen, font, pygame) -> None:
        viewport = self._workspace_rect()
        clip = screen.get_clip()
        screen.set_clip(viewport)
        x0, y0, width, height = viewport
        for x in range(x0 + 16, x0 + width, 40):
            pygame.draw.line(screen, config.GRID_COLOR, (x, y0 + 44), (x, y0 + height), 1)
        for y in range(y0 + 48, y0 + height, 40):
            pygame.draw.line(screen, config.GRID_COLOR, (x0, y), (x0 + width, y), 1)

        pygame.draw.circle(screen, (31, 62, 66), self.arm.base, round(self.arm.max_reach), 1)
        if self.arm.target is not None:
            color = config.TARGET_COLOR
            if self.arm.last_ik_result and not self.arm.last_ik_result.reachable:
                color = config.UNREACHABLE_COLOR
            target = round(self.arm.target[0]), round(self.arm.target[1])
            pygame.draw.circle(screen, color, target, 15, 1)
            pygame.draw.line(screen, color, (target[0] - 10, target[1]), (target[0] + 10, target[1]), 2)
            pygame.draw.line(screen, color, (target[0], target[1] - 10), (target[0], target[1] + 10), 2)

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
        screen.set_clip(clip)

        hint = font.render("Click anywhere in the workspace to set a manual target", True, config.MUTED_TEXT_COLOR)
        screen.blit(hint, (42, 568))

    def _draw_3d_view(self, screen, font, pygame) -> None:
        viewport = self._workspace_rect()
        clip = screen.get_clip()
        screen.set_clip(viewport)
        for x in range(-320, 361, 80):
            pygame.draw.line(screen, (32, 43, 47), self._project((x, -240, 0)), self._project((x, 240, 0)), 1)
        for y in range(-240, 281, 80):
            pygame.draw.line(screen, (32, 43, 47), self._project((-320, y, 0)), self._project((360, y, 0)), 1)

        origin = self._project((0, 0, 0))
        pygame.draw.line(screen, (245, 101, 101), origin, self._project((145, 0, 0)), 3)
        pygame.draw.line(screen, (72, 187, 120), origin, self._project((0, 145, 0)), 3)
        pygame.draw.line(screen, (96, 165, 250), origin, self._project((0, 0, 145)), 3)

        for target in self.ai_controller.targets:
            point = self._project(self._screen_target_to_world(target.position))
            pygame.draw.circle(screen, (93, 124, 133), point, 7, 1)

        if self.arm.target is not None:
            point = self._project(self._screen_target_to_world(self.arm.target))
            pygame.draw.circle(screen, config.TARGET_COLOR, point, 12, 2)

        pose = self.arm.pose
        base = self._project((0.0, 0.0, 0.0))
        elbow = self._project(self._screen_point_to_world(pose.elbow.x, pose.elbow.y))
        end = self._project(self._screen_point_to_world(pose.end_effector.x, pose.end_effector.y))
        pygame.draw.circle(screen, (39, 50, 54), base, 42)
        pygame.draw.line(screen, config.ARM_SHADOW_COLOR, base, elbow, 22)
        pygame.draw.line(screen, config.ARM_SHADOW_COLOR, elbow, end, 22)
        pygame.draw.line(screen, config.ARM_COLOR, base, elbow, 13)
        pygame.draw.line(screen, config.ARM_COLOR, elbow, end, 13)
        pygame.draw.circle(screen, config.JOINT_COLOR, base, 20)
        pygame.draw.circle(screen, config.JOINT_COLOR, elbow, 17)
        pygame.draw.circle(screen, config.END_EFFECTOR_COLOR, end, 15)
        screen.set_clip(clip)

        hint = font.render("Left / Right rotates 3D camera", True, config.MUTED_TEXT_COLOR)
        screen.blit(hint, (42, 568))

    def _draw_bottom_console(self, screen, font, tiny_font, pygame) -> None:
        console = (24, 608, 1052, 86)
        pygame.draw.rect(screen, (18, 25, 28), console, border_radius=6)
        pygame.draw.rect(screen, (45, 58, 63), console, 1, border_radius=6)

        for button in self.buttons[2:]:
            color = (33, 45, 49)
            if button.action == "toggle_ai" and self.ai_controller.enabled:
                color = (34, 87, 69)
            if button.action == "toggle_hw" and self.hardware_sim_enabled:
                color = (34, 64, 93)
            pygame.draw.rect(screen, color, button.rect, border_radius=5)
            pygame.draw.rect(screen, (83, 101, 107), button.rect, 1, border_radius=5)
            label = tiny_font.render(button.label, True, config.TEXT_COLOR)
            label_rect = label.get_rect(center=(button.rect[0] + button.rect[2] / 2, button.rect[1] + button.rect[3] / 2))
            screen.blit(label, label_rect)

        pose = self.arm.pose
        hardware_state = "simulated link armed" if self.hardware_sim_enabled else "hardware output disabled"
        readout = [
            f"Shoulder {self.arm.shoulder.angle_degrees:7.2f} deg",
            f"Elbow {self.arm.elbow.angle_degrees:7.2f} deg",
            f"End ({pose.end_effector.x:6.1f}, {pose.end_effector.y:6.1f})",
            hardware_state,
            "Keyboard: 1 for 2D, 2 for 3D, SPACE AI, TAB task, Q/W shoulder, A/S elbow, R reset, ESC quit",
        ]
        x, y = 574, 620
        for line in readout:
            surface = font.render(line, True, config.MUTED_TEXT_COLOR)
            screen.blit(surface, (x, y))
            y += 15

    def _screen_point_to_world(self, x: float, y: float) -> tuple[float, float, float]:
        dx = x - self.arm.base[0]
        z = self.arm.base[1] - y
        return dx, 0.0, z

    def _screen_target_to_world(self, target: tuple[float, float]) -> tuple[float, float, float]:
        return self._screen_point_to_world(target[0], target[1])

    def _workspace_rect(self) -> tuple[int, int, int, int]:
        return 24, 132, 1052, 460

    def _project(self, point: tuple[float, float, float]) -> tuple[int, int]:
        x, y, z = point
        yaw = radians(self.yaw_degrees)
        rotated_x = x * cos(yaw) - y * sin(yaw)
        rotated_y = x * sin(yaw) + y * cos(yaw)
        camera_distance = 900
        scale = camera_distance / (camera_distance + rotated_y)
        screen_x = config.SCREEN_WIDTH / 2 + rotated_x * scale
        screen_y = 444 - z * scale - rotated_y * 0.22 * scale
        return round(screen_x), round(screen_y)


def point_in_rect(point: tuple[int, int], rect: tuple[int, int, int, int]) -> bool:
    x, y = point
    rect_x, rect_y, width, height = rect
    return rect_x <= x <= rect_x + width and rect_y <= y <= rect_y + height
