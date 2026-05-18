"""Robotic arm domain model."""

from __future__ import annotations

from dataclasses import dataclass

import config
from simulation.inverse_kinematics import IKResult, solve_two_link_ik
from simulation.joints import Joint
from simulation.kinematics import ArmPose, forward_kinematics


@dataclass
class RoboticArm:
    base: tuple[int, int]
    link_1_length: float
    link_2_length: float
    shoulder: Joint
    elbow: Joint
    target: tuple[float, float] | None = None
    last_ik_result: IKResult | None = None

    @classmethod
    def default(cls) -> "RoboticArm":
        return cls(
            base=config.BASE_POSITION,
            link_1_length=config.LINK_1_LENGTH,
            link_2_length=config.LINK_2_LENGTH,
            shoulder=Joint(
                "shoulder",
                config.START_SHOULDER_DEGREES,
                config.SHOULDER_MIN_DEGREES,
                config.SHOULDER_MAX_DEGREES,
            ),
            elbow=Joint(
                "elbow",
                config.START_ELBOW_DEGREES,
                config.ELBOW_MIN_DEGREES,
                config.ELBOW_MAX_DEGREES,
            ),
        )

    @property
    def pose(self) -> ArmPose:
        return forward_kinematics(
            self.base,
            self.link_1_length,
            self.link_2_length,
            self.shoulder.angle_degrees,
            self.elbow.angle_degrees,
        )

    @property
    def max_reach(self) -> float:
        return self.link_1_length + self.link_2_length

    def rotate_shoulder(self, delta_degrees: float) -> None:
        self.shoulder.rotate(delta_degrees)
        self.target = None

    def rotate_elbow(self, delta_degrees: float) -> None:
        self.elbow.rotate(delta_degrees)
        self.target = None

    def reset(self) -> None:
        self.shoulder.set_angle(config.START_SHOULDER_DEGREES)
        self.elbow.set_angle(config.START_ELBOW_DEGREES)
        self.target = None
        self.last_ik_result = None

    def set_target(self, target: tuple[float, float]) -> None:
        self.target = target
        self.last_ik_result = self.solve_target(target)

    def solve_target(self, target: tuple[float, float]) -> IKResult:
        return solve_two_link_ik(
            self.base,
            target,
            self.link_1_length,
            self.link_2_length,
            (self.shoulder.min_degrees, self.shoulder.max_degrees),
            (self.elbow.min_degrees, self.elbow.max_degrees),
        )

    def update(self) -> None:
        if self.target is None:
            return

        result = self.solve_target(self.target)
        self.last_ik_result = result
        self.shoulder.set_angle(
            lerp(self.shoulder.angle_degrees, result.shoulder_degrees, config.AUTO_MOVE_SPEED)
        )
        self.elbow.set_angle(
            lerp(self.elbow.angle_degrees, result.elbow_degrees, config.AUTO_MOVE_SPEED)
        )


def lerp(start: float, end: float, amount: float) -> float:
    return start + (end - start) * amount

