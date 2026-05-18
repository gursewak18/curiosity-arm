"""Curiosity Arm application entry point."""

import argparse

from ai.arm_controller import IndustrialAIArmController
from simulation.arm import RoboticArm
from simulation.dashboard import CuriosityArmDashboard
from simulation.renderer import PygameRenderer
from simulation.renderer_3d import Pygame3DRenderer


def main() -> None:
    parser = argparse.ArgumentParser(description="Curiosity Arm simulator and AI controller")
    parser.add_argument(
        "--mode",
        choices=("dashboard", "2d", "ai", "3d", "3d-ai"),
        default="dashboard",
        help="Choose simulator mode. Default: dashboard",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=None,
        help="Optional smoke-test frame limit. Omit for normal interactive use.",
    )
    args = parser.parse_args()

    arm = RoboticArm.default()
    ai_controller = IndustrialAIArmController(arm)

    if args.mode == "dashboard":
        renderer = CuriosityArmDashboard(arm, ai_controller)
    elif args.mode == "3d":
        renderer = Pygame3DRenderer(arm, ai_controller)
    elif args.mode == "3d-ai":
        ai_controller.set_enabled(True)
        renderer = Pygame3DRenderer(arm, ai_controller)
    else:
        renderer = PygameRenderer(arm, ai_controller, start_ai=args.mode == "ai")

    renderer.run(max_frames=args.frames)


if __name__ == "__main__":
    main()
