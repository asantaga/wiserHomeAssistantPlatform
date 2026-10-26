"""Regression tests for continuous-integration workflow coverage."""

from pathlib import Path
import unittest


WORKFLOWS = Path(__file__).parents[1] / ".github/workflows"


class CIWorkflowTest(unittest.TestCase):
    def test_validation_runs_on_active_branches(self):
        workflow = (WORKFLOWS / "validate.yml").read_text()

        self.assertIn("branches: [dev, master]", workflow)
        self.assertEqual(workflow.count("branches: [dev, master]"), 2)
        self.assertNotIn("branches:\n      - main", workflow)

    def test_validation_runs_complete_test_suite(self):
        workflow = (WORKFLOWS / "validate.yml").read_text()

        self.assertIn(
            "python -m pip install -r tests/requirements.txt",
            workflow,
        )
        self.assertIn("python -m unittest discover -s tests", workflow)

    def test_release_build_runs_complete_test_suite(self):
        workflow = (WORKFLOWS / "publish.yml").read_text()

        self.assertIn("python -m unittest discover -s tests", workflow)
        self.assertNotIn("unittest discover -s tests -p", workflow)


if __name__ == "__main__":
    unittest.main()
