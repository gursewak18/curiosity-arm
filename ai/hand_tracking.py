"""Hand tracking adapter placeholder.

Stage 4 will use OpenCV and MediaPipe here to convert webcam hand landmarks into
robotic arm targets.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class HandTarget:
    x: float
    y: float
    confidence: float


class HandTracker:
    def get_target(self) -> HandTarget | None:
        raise NotImplementedError("Stage 4: connect OpenCV + MediaPipe hand tracking.")

