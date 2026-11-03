import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "generate_voice.py"
SPEC = importlib.util.spec_from_file_location("generate_voice", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class NarrationValidationTests(unittest.TestCase):
    def test_strips_whitespace(self):
        self.assertEqual(MODULE.validate_narration("  Hello world.  "), "Hello world.")

    def test_rejects_empty_text(self):
        with self.assertRaises(ValueError):
            MODULE.validate_narration("  \n ")

    def test_rejects_text_over_limit(self):
        with self.assertRaises(ValueError):
            MODULE.validate_narration("a" * (MODULE.MAX_CHARACTERS + 1))

    def test_accepts_exact_limit(self):
        self.assertEqual(len(MODULE.validate_narration("a" * MODULE.MAX_CHARACTERS)), MODULE.MAX_CHARACTERS)

if __name__ == "__main__":
    unittest.main()
