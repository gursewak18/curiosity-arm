"""Joint models and angle constraints."""

from dataclasses import dataclass


@dataclass
class Joint:
    name: str
    angle_degrees: float
    min_degrees: float
    max_degrees: float

    def rotate(self, delta_degrees: float) -> None:
        self.set_angle(self.angle_degrees + delta_degrees)

    def set_angle(self, angle_degrees: float) -> None:
        self.angle_degrees = clamp(angle_degrees, self.min_degrees, self.max_degrees)


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))

