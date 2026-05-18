import unittest

from simulation.kinematics import forward_kinematics


class ForwardKinematicsTests(unittest.TestCase):
    def test_straight_arm_points_right(self) -> None:
        pose = forward_kinematics((0, 0), 100, 50, 0, 0)

        self.assertAlmostEqual(pose.elbow.x, 100)
        self.assertAlmostEqual(pose.elbow.y, 0)
        self.assertAlmostEqual(pose.end_effector.x, 150)
        self.assertAlmostEqual(pose.end_effector.y, 0)

    def test_elbow_angle_is_relative_to_shoulder(self) -> None:
        pose = forward_kinematics((0, 0), 100, 50, 90, -90)

        self.assertAlmostEqual(pose.elbow.x, 0, places=6)
        self.assertAlmostEqual(pose.elbow.y, 100, places=6)
        self.assertAlmostEqual(pose.end_effector.x, 50, places=6)
        self.assertAlmostEqual(pose.end_effector.y, 100, places=6)


if __name__ == "__main__":
    unittest.main()

