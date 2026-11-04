import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("generate_scene_images", ROOT / "scripts" / "generate_scene_images.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class SceneImageTests(unittest.TestCase):
    def test_prompt_contains_story_beat_and_consistent_art_direction(self):
        scene = {
            "narration": "The young soldier reads a letter beside the trench.",
            "setting": "battlefield",
            "visual": "war",
            "action": "observing or explaining",
            "mood": "worried",
            "props": ["letter", "rifle"],
            "camera": "tight medium shot"
        }
        prompt = MODULE.make_prompt(scene, 0, 5, "young soldier in a navy uniform")
        self.assertIn("Hand-drawn 2D animation film aesthetic", prompt)
        self.assertIn("complete clothed bodies", prompt)
        self.assertIn("reads a letter", prompt)
        self.assertIn("never stick figures", prompt)
        self.assertIn("Required composition variation", prompt)
        self.assertIn("Do NOT copy its camera angle", prompt)
        self.assertIn("no text, fake writing", prompt)
        other = MODULE.make_prompt(scene, 1, 5, "young soldier in a navy uniform")
        self.assertNotEqual(prompt, other)
        self.assertLessEqual(len(prompt), 3000)

    def test_multipart_request_encodes_reference_image(self):
        body, content_type = MODULE.multipart(
            {"prompt": "a cinematic illustrated scene", "width": "1024"},
            {"input_image_0": ("reference.jpg", b"fake-image-bytes", "image/jpeg")}
        )
        self.assertIn("multipart/form-data; boundary=", content_type)
        self.assertIn(b'name="input_image_0"; filename="reference.jpg"', body)
        self.assertIn(b"fake-image-bytes", body)
        self.assertIn(b'name="prompt"', body)

if __name__ == "__main__":
    unittest.main()
