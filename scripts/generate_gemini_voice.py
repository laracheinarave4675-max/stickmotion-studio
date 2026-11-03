#!/usr/bin/env python3
"""Generate long-form English narration with Gemini TTS and join PCM chunks into WAV."""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import wave
from pathlib import Path

SAMPLE_RATE = 24000
CHANNELS = 1
SAMPLE_WIDTH = 2
MAX_CHARACTERS = 18000
CHUNK_CHARACTERS = 2800
DEFAULT_MODEL = "gemini-2.5-flash-preview-tts"
DEFAULT_VOICE = "Kore"

def validate_narration(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Narration is empty.")
    if len(cleaned) > MAX_CHARACTERS:
        raise ValueError(f"Narration is {len(cleaned)} characters; limit is {MAX_CHARACTERS}.")
    return cleaned

def split_text(text: str, max_chars: int = CHUNK_CHARACTERS) -> list[str]:
    """Split at sentence/paragraph boundaries when possible; never drop text."""
    text = validate_narration(text)
    if max_chars < 100:
        raise ValueError("Chunk size must be at least 100 characters.")
    chunks: list[str] = []
    remaining = text
    while len(remaining) > max_chars:
        window = remaining[:max_chars + 1]
        candidates = [m.end() for m in re.finditer(r"(?:[.!?][\"')\]]*\s+|\n\s*\n)", window)]
        cut = candidates[-1] if candidates else window.rfind(" ")
        if cut < max_chars // 2:
            cut = max_chars
        part = remaining[:cut].strip()
        if not part:
            cut = max_chars
            part = remaining[:cut].strip()
        chunks.append(part)
        remaining = remaining[cut:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks

def write_wav(path: Path, pcm_chunks: list[bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(CHANNELS)
        wav.setsampwidth(SAMPLE_WIDTH)
        wav.setframerate(SAMPLE_RATE)
        for pcm in pcm_chunks:
            if len(pcm) % SAMPLE_WIDTH:
                raise ValueError("Gemini returned an incomplete 16-bit PCM sample.")
            wav.writeframes(pcm)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    parser.add_argument("--style", default="Calm, authoritative, cinematic documentary narration. Natural pacing, clear articulation, restrained emotion.")
    args = parser.parse_args()

    try:
        narration = validate_narration(args.input.read_text(encoding="utf-8"))
        chunks = split_text(narration)
    except (OSError, ValueError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    if not os.environ.get("GEMINI_API_KEY"):
        print("Missing GEMINI_API_KEY environment variable.", file=sys.stderr)
        return 2

    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        pcm_chunks: list[bytes] = []
        for index, chunk in enumerate(chunks, start=1):
            prompt = f"{args.style} Read the following narration verbatim. Do not add, omit, or paraphrase any words.\n\n{chunk}"
            response = client.models.generate_content(
                model=args.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=args.voice)
                        )
                    ),
                ),
            )
            audio = None
            for candidate in (response.candidates or []):
                for part in (candidate.content.parts or []):
                    if part.inline_data and part.inline_data.data:
                        audio = part.inline_data.data
                        break
                if audio:
                    break
            if not audio:
                raise RuntimeError(f"No audio returned for chunk {index}/{len(chunks)}.")
            pcm_chunks.append(audio)
            print(f"Generated chunk {index}/{len(chunks)} ({len(chunk)} characters).")
        write_wav(args.output, pcm_chunks)
        metadata = {
            "engine": "Gemini TTS",
            "model": args.model,
            "voice": args.voice,
            "style": args.style,
            "characters": len(narration),
            "chunks": len(chunks),
            "sample_rate": SAMPLE_RATE,
            "format": "WAV PCM 16-bit mono",
            "output": args.output.name,
        }
        args.output.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        print(json.dumps(metadata))
        return 0
    except Exception as exc:
        print(f"Gemini voice generation failed: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
