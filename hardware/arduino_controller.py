"""High-level Arduino controller."""

from hardware.serial_communication import SerialConnection
from hardware.servo_manager import ServoManager


class ArduinoController:
    def __init__(self, port: str) -> None:
        self.connection = SerialConnection(port)
        self.servos = ServoManager()

    def connect(self) -> None:
        self.connection.connect()

    def move_to(self, shoulder_degrees: float, elbow_degrees: float) -> None:
        command = self.servos.format_angles(shoulder_degrees, elbow_degrees)
        self.connection.send_line(command)

    def close(self) -> None:
        self.connection.close()

