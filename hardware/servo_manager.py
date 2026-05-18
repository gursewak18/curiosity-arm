"""Servo angle formatting and validation."""

from simulation.joints import clamp


class ServoManager:
    def __init__(self, shoulder_pin: int = 9, elbow_pin: int = 10) -> None:
        self.shoulder_pin = shoulder_pin
        self.elbow_pin = elbow_pin

    def format_angles(self, shoulder_degrees: float, elbow_degrees: float) -> str:
        shoulder = round(clamp(shoulder_degrees, 0, 180))
        elbow = round(clamp(elbow_degrees, 0, 180))
        return f"S:{shoulder};E:{elbow}"

