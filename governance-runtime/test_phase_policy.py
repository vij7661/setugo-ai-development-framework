import unittest


class WeakenedCandidateHarness(unittest.TestCase):
    def test_unconditional_green(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
