"""Object detection adapter placeholder.

Stage 5 will return detected object names and positions for autonomous pick and
place behavior.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DetectedObject:
    label: str
    x: float
    y: float
    confidence: float


class ObjectDetector:
    def detect(self) -> list[DetectedObject]:
        raise NotImplementedError("Stage 5: connect YOLO, OpenCV DNN, or another model.")

