"""Inverse kinematics for a planar 2-link robotic arm."""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, atan2, cos, degrees, hypot, sin

from simulation.joints import clamp


@dataclass(frozen=True)
class IKResult:
    shoulder_degrees: float
    elbow_degrees: float
    reachable: bool
    distance: float


def solve_two_link_ik(
    base: tuple[float, float],
    target: tuple[float, float],
    link_1_length: float,
    link_2_length: float,
    shoulder_limits: tuple[float, float],
    elbow_limits: tuple[float, float],
) -> IKResult:
    """Calculate joint angles that place the end effector near a target."""
    dx = target[0] - base[0]
    dy = target[1] - base[1]
    distance = hypot(dx, dy)

    min_reach = abs(link_1_length - link_2_length)
    max_reach = link_1_length + link_2_length
    reachable = min_reach <= distance <= max_reach
    clamped_distance = clamp(distance, min_reach + 0.001, max_reach - 0.001)

    cos_elbow = (
        clamped_distance**2 - link_1_length**2 - link_2_length**2
    ) / (2 * link_1_length * link_2_length)
    cos_elbow = clamp(cos_elbow, -1.0, 1.0)
    elbow = acos(cos_elbow)

    shoulder_offset = atan2(
        link_2_length * sin(elbow),
        link_1_length + link_2_length * cos(elbow),
    )
    shoulder = atan2(dy, dx) - shoulder_offset

    shoulder_degrees = clamp(degrees(shoulder), shoulder_limits[0], shoulder_limits[1])
    elbow_degrees = clamp(degrees(elbow), elbow_limits[0], elbow_limits[1])

    return IKResult(
        shoulder_degrees=shoulder_degrees,
        elbow_degrees=elbow_degrees,
        reachable=reachable,
        distance=distance,
    )
