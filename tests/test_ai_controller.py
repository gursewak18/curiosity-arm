import unittest

from ai.arm_controller import IndustrialAIArmController
from simulation.arm import RoboticArm


class AIControllerTests(unittest.TestCase):
    def test_controller_sets_target_when_enabled(self) -> None:
        arm = RoboticArm.default()
        controller = IndustrialAIArmController(arm)

        controller.set_enabled(True)
        controller.update(0.1)

        self.assertIsNotNone(arm.target)
        self.assertEqual(controller.status.mode, "AI autonomous")
        self.assertGreater(controller.status.confidence, 0)

    def test_controller_can_advance_target(self) -> None:
        arm = RoboticArm.default()
        controller = IndustrialAIArmController(arm)
        first = controller.target_index

        controller.next_target()

        self.assertNotEqual(controller.target_index, first)


if __name__ == "__main__":
    unittest.main()
