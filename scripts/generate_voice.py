#!/usr/bin/env python3
"""Generate a short English narration WAV with the open-source Piper TTS engine."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys

MAX_CHARACTERS = 1200
DEFAULT_VOICE = "en_US-lessac-medium"

def validate_narration(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Narration is empty.")
    if len(cleaned) > MAX_CHARACTERS:
        raise ValueError(f"Narration is {len(cleaned)} characters; limit is {MAX_CHARACTERS}.")
    return cleaned

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    parser.add_argument("--model-dir", type=Path, default=Path("models"))
    args = parser.parse_args()

    try:
        narration = validate_narration(args.input.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    args.model_dir.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            [sys.executable, "-m", "piper.download_voices", args.voice,
             "--download-dir", str(args.model_dir)],
            check=True,
        )
        from piper import PiperVoice
        model_path = args.model_dir / f"{args.voice}.onnx"
        if not model_path.is_file():
            raise FileNotFoundError(f"Voice model was not downloaded: {model_path}")
        import wave
        voice = PiperVoice.load(str(model_path))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(args.output), "wb") as wav_file:
            voice.synthesize_wav(narration, wav_file)
        metadata = {
            "engine": "Piper TTS",
            "voice": args.voice,
            "characters": len(narration),
            "output": args.output.name,
            "format": "WAV",
            "limit_characters": MAX_CHARACTERS,
        }
        args.output.with_suffix(".json").write_text(
            json.dumps(metadata, indent=2) + "\\n", encoding="utf-8"
        )
        print(json.dumps(metadata))
    except Exception as exc:
        print(f"Voice generation failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
