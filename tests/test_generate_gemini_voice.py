import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "generate_gemini_voice.py"
SPEC = importlib.util.spec_from_file_location("generate_gemini_voice", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class GeminiNarrationTests(unittest.TestCase):
    def test_rejects_empty_text(self):
        with self.assertRaises(ValueError):
            MODULE.validate_narration("  ")

    def test_rejects_over_limit(self):
        with self.assertRaises(ValueError):
            MODULE.validate_narration("x" * (MODULE.MAX_CHARACTERS + 1))

    def test_splits_long_text_without_losing_words(self):
        source = ("First sentence has enough words. Second sentence follows here. " * 80).strip()
        chunks = MODULE.split_text(source, 250)
        self.assertGreater(len(chunks), 1)
        self.assertEqual(" ".join(chunks).replace("  ", " "), source.replace("  ", " "))
        self.assertTrue(all(len(chunk) <= 250 for chunk in chunks))

    def test_short_text_stays_one_chunk(self):
        self.assertEqual(MODULE.split_text("A short narration."), ["A short narration."])

    def test_wav_is_written_with_valid_header(self):
        import tempfile
        import wave
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "voice.wav"
            MODULE.write_wav(path, [b"\\x00\\x00" * 240])
            with wave.open(str(path), "rb") as wav:
                self.assertEqual(wav.getframerate(), 24000)
                self.assertEqual(wav.getnchannels(), 1)
                self.assertEqual(wav.getnframes(), 240)

if __name__ == "__main__":
    unittest.main()
