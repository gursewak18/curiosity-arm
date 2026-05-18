"""Serial communication wrapper for Arduino integration."""

from __future__ import annotations


class SerialConnection:
    def __init__(self, port: str, baud_rate: int = 115200) -> None:
        self.port = port
        self.baud_rate = baud_rate
        self._serial = None

    def connect(self) -> None:
        try:
            import serial
        except ImportError as exc:
            raise RuntimeError("Install pyserial before using hardware mode.") from exc

        self._serial = serial.Serial(self.port, self.baud_rate, timeout=1)

    def send_line(self, line: str) -> None:
        if self._serial is None:
            raise RuntimeError("Serial connection is not open.")
        self._serial.write((line.strip() + "\n").encode("utf-8"))

    def close(self) -> None:
        if self._serial is not None:
            self._serial.close()
            self._serial = None

