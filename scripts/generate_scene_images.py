#!/usr/bin/env python3
"""Generate bespoke illustrated scene plates with Cloudflare Workers AI (optional free-tier path)."""
from __future__ import annotations
import argparse, base64, json, os, random, subprocess, sys, time, uuid
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from PIL import Image

MODEL = "@cf/black-forest-labs/flux-2-klein-4b"
STYLE = (
    "Premium hand-drawn 2D animated documentary illustration, cinematic story-cartoon frame, "
    "bold clean black ink outlines, richly detailed locations, architecture, furniture, props, "
    "and depth, painterly "
    "muted vintage colors, subtle paper grain, intentional warm/cool lighting, professional "
    "animation background art, carefully composed 16:9 widescreen shot. "
    "Not a stick-figure diagram, not geometric clipart, not photorealistic, not 3D. "
    "No lettering, no subtitles, no logos, no watermark, no borders."
)
NEGATIVE = "text, typography, subtitles, captions, logo, watermark, photorealism, 3D render, empty background, crude stick figures, malformed hands, extra limbs, gore, extreme close-up, giant head, oversized face, floating head, cropped body, duplicate protagonist, collage, split screen"
def load_scenes(text: str):
    js = "import {buildScenePlan} from './src/scene-planner.js'; console.log(JSON.stringify(buildScenePlan(" + json.dumps(text) + ")));"
    return json.loads(subprocess.run(["node", "--input-type=module", "-e", js], check=True, capture_output=True, text=True).stdout)
def make_prompt(scene: dict, index: int, total: int, protagonist: str) -> str:
    props = ", ".join(scene.get("props", [])[:4]) or "period-appropriate objects integrated naturally into the setting"
    narration = " ".join(scene.get("narration", "").split())
    camera = scene.get("camera", "cinematic medium shot")
    return (
        f"{STYLE}\\n"
        "Create one complete, cohesive 2D story-cartoon frame with the people INCLUDED in the illustration. "
        "Show the actual human action from the narration: recognizable expressive illustrated people with "
        "consistent anatomy, clean connected limbs, natural hands, readable faces, distinctive hair and "
        "period-appropriate clothing. The main protagonist must retain the same face, hair, age, body shape "
        "and outfit as the supplied reference image; supporting people must look different from one another. "
        "Do not create stick figures, wireframe bodies, detached limbs, duplicate faces, extra arms, "
        "floating heads, or disconnected outlines.\\n"
        f"Scene {index + 1} of {total}. Setting: {scene.get('setting','specific story location')}. "
        f"Visual category: {scene.get('visual','historical')}. Action to visibly depict: {scene.get('action','observing or explaining')}. "
        f"Emotion and facial acting: {scene.get('mood','explaining')}. Important props: {props}. "
        f"Directed camera composition: {camera}.\\n"
        f"Tell this exact narration beat in a single readable visual moment: {narration}\\n"
        "Art direction: premium hand-drawn 2D animated historical documentary, expressive character design, "
        "confident varied black ink linework, appealing proportions, carefully drawn clothing folds, "
        "subtle painted shadows, rich layered backgrounds with believable perspective, detailed architecture, "
        "furniture and story props, cinematic warm/cool lighting, controlled vintage palette, tactile painted "
        "background texture. This should look like a polished frame from a professionally art-directed "
        "animated documentary, not generic AI clipart. "
        "Vary the camera composition between scenes: wide establishing views with small figures, medium "
        "two-shots for interactions, over-the-shoulder action views, and emotional close-ups only when "
        "the narration calls for them. Keep faces and bodies anatomically coherent and fully composed. "
        "Use the reference image to preserve protagonist identity and the exact drawing style, but invent "
        "a new location, action, staging and camera angle for this scene."
    )[:2048]
def multipart(fields: dict[str, str], files: dict[str, tuple[str, bytes, str]]) -> tuple[bytes, str]:
    boundary = "----StickMotion" + uuid.uuid4().hex
    chunks = []
    for name, value in fields.items():
        chunks.extend([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
            str(value).encode("utf-8"), b"\r\n"
        ])
    for name, (filename, payload, content_type) in files.items():
        chunks.extend([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode(),
            f"Content-Type: {content_type}\r\n\r\n".encode(),
            payload, b"\r\n"
        ])
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"
def call_cloudflare(account: str, token: str, prompt: str, seed: int, reference: bytes | None):
    fields = {"prompt": prompt, "width": "1024", "height": "576", "seed": str(seed), "guidance": "4"}
    files = {}
    if reference:
        files["input_image_0"] = ("style-reference.jpg", reference, "image/jpeg")
    body, content_type = multipart(fields, files)
    url = f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{MODEL}"
    request = Request(url, data=body, method="POST", headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": content_type,
        "Accept": "application/json"
    })
    try:
        with urlopen(request, timeout=240) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:1200]
        raise RuntimeError(f"Cloudflare image request failed ({exc.code}): {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Cloudflare image request failed: {exc.reason}") from exc
    if not payload.get("success", False):
        raise RuntimeError("Cloudflare rejected image request: " + json.dumps(payload.get("errors", []))[:1200])
    result = payload.get("result")
    image_b64 = result.get("image") if isinstance(result, dict) else result
    if not isinstance(image_b64, str) or not image_b64:
        raise RuntimeError("Cloudflare response did not contain a base64 image.")
    try:
        raw = base64.b64decode(image_b64)
        image = Image.open(BytesIO(raw)).convert("RGB")
        out = BytesIO()
        image.save(out, format="PNG", optimize=True)
        return out.getvalue()
    except Exception as exc:
        raise RuntimeError(f"Cloudflare returned an unreadable image: {exc}") from exc
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--narration", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, default=Path("output/scenes"))
    p.add_argument("--max-images", type=int, default=70)
    p.add_argument("--seed", type=int, default=1916)
    p.add_argument("--protagonist", default="the same lead character as the supplied first-scene reference")
    p.add_argument("--delay", type=float, default=1.0)
    a = p.parse_args()
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if not account or not token:
        raise SystemExit("Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN in GitHub Actions secrets.")
    text = a.narration.read_text(encoding="utf-8").strip()
    scenes = load_scenes(text)
    if not scenes:
        raise SystemExit("No scenes were produced from narration.")
    a.output_dir.mkdir(parents=True, exist_ok=True)
    reference_path = a.output_dir / "style-reference.jpg"
    reference = reference_path.read_bytes() if reference_path.exists() else None
    generated = 0
    for i, scene in enumerate(scenes[:max(0, a.max_images)]):
        out = a.output_dir / f"scene_{i+1:04d}.png"
        if out.exists() and out.stat().st_size > 50000:
            if i == 0 and not reference:
                with Image.open(out) as image:
                    image.convert("RGB").resize((512, 288), Image.Resampling.LANCZOS).save(reference_path, "JPEG", quality=88)
                    reference = reference_path.read_bytes()
            continue
        prompt = make_prompt(scene, i, len(scenes), a.protagonist)
        last_error = None
        for attempt in range(3):
            try:
                raw = call_cloudflare(account, token, prompt, a.seed + i, reference if i > 0 else None)
                out.write_bytes(raw)
                generated += 1
                print(f"Generated scene {i+1}/{min(len(scenes),a.max_images)}: {out.name}", flush=True)
                if i == 0 and not reference:
                    with Image.open(out) as image:
                        image.convert("RGB").resize((512, 288), Image.Resampling.LANCZOS).save(reference_path, "JPEG", quality=88)
                    reference = reference_path.read_bytes()
                break
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(2 ** attempt)
        else:
            raise SystemExit(f"Scene {i+1} failed after 3 attempts: {last_error}")
        if a.delay > 0:
            time.sleep(a.delay)
    print(json.dumps({"scene_count": len(scenes), "generated_this_run": generated, "available_images": len(list(a.output_dir.glob("scene_*.png"))), "model": MODEL, "resolution": "1024x576", "reference_image": str(reference_path) if reference else None}))
if __name__ == "__main__":
    main()
