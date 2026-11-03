import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "render_video.py"
SPEC = importlib.util.spec_from_file_location("render_video", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class RendererTests(unittest.TestCase):
    def test_scene_planner_contract_and_frame_dimensions(self):
        scenes = MODULE.load_scenes("A prisoner searches for the key and escapes through the dark corridor.")
        self.assertTrue(scenes)
        scene = scenes[0]
        for key in ("narration", "title", "visual", "action", "mood", "props"):
            self.assertIn(key, scene)
        frame = MODULE.draw_scene(scene, 0, 0.5, 5.0, scene["narration"])
        self.assertEqual(frame.size, (1920, 1080))
        self.assertEqual(frame.mode, "RGB")

    def test_long_caption_is_paginated_not_discarded(self):
        text = " ".join(["A very important detail appears in the scene."] * 12)
        lines = MODULE.wrap(text, width=66)
        pages = [lines[i:i+2] for i in range(0, len(lines), 2)]
        self.assertGreater(len(pages), 2)
        self.assertEqual(sum(len(page) for page in pages), len(lines))

if __name__ == "__main__":
    unittest.main()
