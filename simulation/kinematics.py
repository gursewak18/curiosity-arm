"""Forward kinematics for a 2-link robotic arm."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def as_int_tuple(self) -> tuple[int, int]:
        return round(self.x), round(self.y)


@dataclass(frozen=True)
class ArmPose:
    base: Point
    elbow: Point
    end_effector: Point


def forward_kinematics(
    base: tuple[float, float],
    link_1_length: float,
    link_2_length: float,
    shoulder_degrees: float,
    elbow_degrees: float,
) -> ArmPose:
    """Return base, elbow, and end-effector positions for a planar 2-link arm."""
    base_point = Point(base[0], base[1])

    theta_1 = radians(shoulder_degrees)
    theta_2 = radians(shoulder_degrees + elbow_degrees)

    elbow = Point(
        base_point.x + link_1_length * cos(theta_1),
        base_point.y + link_1_length * sin(theta_1),
    )
    end_effector = Point(
        elbow.x + link_2_length * cos(theta_2),
        elbow.y + link_2_length * sin(theta_2),
    )

    return ArmPose(base=base_point, elbow=elbow, end_effector=end_effector)

