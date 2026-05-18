"""Keyboard input mapping."""

import config
from simulation.arm import RoboticArm


def handle_keyboard(keys, arm: RoboticArm, pygame) -> None:
    if keys[pygame.K_q]:
        arm.rotate_shoulder(-config.KEYBOARD_STEP_DEGREES)
    if keys[pygame.K_w]:
        arm.rotate_shoulder(config.KEYBOARD_STEP_DEGREES)
    if keys[pygame.K_a]:
        arm.rotate_elbow(-config.KEYBOARD_STEP_DEGREES)
    if keys[pygame.K_s]:
        arm.rotate_elbow(config.KEYBOARD_STEP_DEGREES)

