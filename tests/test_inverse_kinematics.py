import unittest

from simulation.inverse_kinematics import solve_two_link_ik
from simulation.kinematics import forward_kinematics


class InverseKinematicsTests(unittest.TestCase):
    def test_reachable_target_solves_near_target(self) -> None:
        target = (120, 80)
        result = solve_two_link_ik(
            base=(0, 0),
            target=target,
            link_1_length=100,
            link_2_length=75,
            shoulder_limits=(-180, 180),
            elbow_limits=(-180, 180),
        )
        pose = forward_kinematics(
            (0, 0),
            100,
            75,
            result.shoulder_degrees,
            result.elbow_degrees,
        )

        self.assertTrue(result.reachable)
        self.assertAlmostEqual(pose.end_effector.x, target[0], delta=1.0)
        self.assertAlmostEqual(pose.end_effector.y, target[1], delta=1.0)

    def test_out_of_reach_target_reports_unreachable(self) -> None:
        result = solve_two_link_ik(
            base=(0, 0),
            target=(1000, 1000),
            link_1_length=100,
            link_2_length=75,
            shoulder_limits=(-180, 180),
            elbow_limits=(-180, 180),
        )

        self.assertFalse(result.reachable)


if __name__ == "__main__":
    unittest.main()

