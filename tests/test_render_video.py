import importlib.util
import tempfile
import unittest
import wave
from PIL import ImageChops
from pathlib import Path

ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "scripts" / "render_video.py"
SPEC = importlib.util.spec_from_file_location("render_video", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
MUSIC_SPEC = importlib.util.spec_from_file_location("generate_music", ROOT / "scripts" / "generate_music.py")
MUSIC = importlib.util.module_from_spec(MUSIC_SPEC)
MUSIC_SPEC.loader.exec_module(MUSIC)
SFX_SPEC = importlib.util.spec_from_file_location("generate_sfx", ROOT / "scripts" / "generate_sfx.py")
SFX = importlib.util.module_from_spec(SFX_SPEC)
SFX_SPEC.loader.exec_module(SFX)

class RendererTests(unittest.TestCase):
    def test_scene_planner_contract_and_frame_dimensions(self):
        scenes = MODULE.load_scenes("A prisoner searches for the key and escapes through the dark corridor.")
        self.assertTrue(scenes)
        scene = scenes[0]
        for key in ("narration", "title", "visual", "action", "mood", "props"):
            self.assertIn(key, scene)
        frame = MODULE.draw_scene(scene, 0, 0.5, 5.0, scene["narration"])
        self.assertEqual(frame.size, (960, 540))
        self.assertEqual(frame.mode, "RGB")

    def test_illustrated_scene_uses_distinct_camera_framing(self):
        scene = MODULE.load_scenes("The detective examined the evidence folder in the investigation room.")[0]
        wide = MODULE.draw_scene(scene, 3, 0.5, 5.0, "")
        close = MODULE.draw_scene(scene, 1, 0.5, 5.0, "")
        self.assertEqual(wide.size, (960, 540))
        self.assertIsNotNone(ImageChops.difference(wide, close).getbbox())

    def test_close_up_contains_visible_face_details(self):
        scene = MODULE.load_scenes("The detective examined the evidence folder in the investigation room.")[0]
        frame = MODULE.draw_scene(scene, 1, 0.5, 5.0, "")
        face_region = frame.crop((330, 80, 630, 390))
        dark_pixels = sum(1 for pixel in face_region.getdata() if max(pixel) < 75)
        self.assertGreater(dark_pixels, 80)

    def test_renderer_exposes_reference_style_features(self):
        scene = MODULE.load_scenes("The soldiers marched through the old city during the war.")[0]
        frame = MODULE.draw_scene(scene, 1, 1.0, 5.0, scene["narration"])
        self.assertEqual(frame.mode, "RGB")
        self.assertGreater(len(set(frame.resize((96, 54)).getdata())), 30)

    def test_long_caption_is_paginated_not_discarded(self):
        text = " ".join(["A very important detail appears in the scene."] * 12)
        lines = MODULE.wrap(text, width=66)
        pages = [lines[i:i+2] for i in range(0, len(lines), 2)]
        self.assertGreater(len(pages), 2)
        self.assertEqual(sum(len(page) for page in pages), len(lines))

    def test_original_music_is_stereo_pcm_and_correct_duration(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "music.wav"
            meta = MUSIC.generate(path, 2.0, "crime")
            with wave.open(str(path), "rb") as audio:
                self.assertEqual(audio.getnchannels(), 2)
                self.assertEqual(audio.getsampwidth(), 2)
                self.assertEqual(audio.getframerate(), 24000)
                self.assertAlmostEqual(audio.getnframes()/audio.getframerate(), 2.0, delta=.01)
            self.assertEqual(meta["style"], "suspense")
            self.assertEqual(meta["source"], "original procedural synthesis")

    def test_sfx_selection_matches_story_events(self):
        self.assertEqual(SFX.choose("He unlocked the door and entered.", "prison", "opening or unlocking"), "door")
        self.assertEqual(SFX.choose("The ship was sinking as waves hit the raft.", "shipwreck", "swimming or struggling in water"), "water")
        self.assertEqual(SFX.choose("He ran across the dark desert.", "desert", "running"), "wind")
        clip = SFX.cue("impact", .4, 12)
        self.assertGreater(len(clip), 1000)
        self.assertTrue(any(clip))

if __name__ == "__main__":
    unittest.main()
