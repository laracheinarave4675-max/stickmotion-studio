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
    "Hand-drawn 2D storybook documentary cartoon, polished editorial illustration, "
    "recognizable human cartoon characters with expressive white or light-toned faces, bold clean ink outlines, "
    "readable eyes, eyebrows and mouth shapes, distinctive hairstyles and period-appropriate clothing silhouettes. "
    "Characters have complete illustrated bodies, heads, necks, torsos, arms, hands, legs and shoes; "
    "never stick figures, never black rods, never floating white spheres. "
    "Rich fully illustrated story-specific environments with perspective architecture, furniture, props and layered depth. "
    "Muted cinematic palette, warm interiors and daylight contrasted with cold dramatic night scenes, intentional shadows, "
    "subtle painterly texture, expressive acting, professional historical animated documentary art direction. "
    "Wide 16:9 composition, no lettering, no subtitles, no logos, no watermark."
)
NEGATIVE = "stick figure, stickman, black rod body, line-art person, white ball head, sphere head, faceless mannequin, primitive geometric human, photorealistic human, text, typography, subtitles, logo, watermark, gore, extra limbs, malformed hands, duplicate protagonist, collage, split screen"
def load_scenes(text: str):
    js = "import {buildScenePlan} from './src/scene-planner.js'; console.log(JSON.stringify(buildScenePlan(" + json.dumps(text) + ")));"
    return json.loads(subprocess.run(["node", "--input-type=module", "-e", js], check=True, capture_output=True, text=True).stdout)
def make_prompt(scene: dict, index: int, total: int, protagonist: str) -> str:
    props = ", ".join(scene.get("props", [])[:5]) or "objects naturally used by the characters in this location"
    narration = " ".join(scene.get("narration", "").split())
    camera = scene.get("camera", "cinematic medium shot")
    action = scene.get("action", "show the character physically doing the action described")
    mood = scene.get("mood", "emotion clearly visible in face and posture")
    setting = scene.get("setting", "a specific, fully dressed story location")
    shot_patterns = [
        "wide establishing composition showing the location and one clear focal action",
        "tight over-the-shoulder composition focused on the hands and important object",
        "low three-quarter medium shot with the protagonist dominating the foreground",
        "high-angle composition revealing the geography and character positions",
        "intimate facial close-up with the relevant story object visible",
        "wide cinematic aftermath composition with strong foreground, middle ground and background layers",
    ]
    shot = shot_patterns[index % len(shot_patterns)]
    return (
        f"{STYLE}\\n"
        f"Create a single coherent illustrated frame for scene {index + 1} of {total}. "
        "Show actual illustrated people, not symbols or stick figures. "
        "Character design: rounded expressive faces, visible eyes and eyebrows, clear mouth expression, "
        "distinct hair or period headwear, complete clothed bodies with believable cartoon proportions, "
        "bold dark ink contour lines and carefully drawn hands and shoes. "
        "Maintain the same lead character identity, face, hairstyle and outfit across all scenes. "
        f"Lead character continuity note: {protagonist}. "
        f"Location and environment: {setting}. "
        f"Visible physical action (must be unmistakable at a glance): {action}. "
        f"Emotion and body language: {mood}. Essential story props being handled or interacted with: {props}. "
        f"Camera direction: {camera}. Required composition variation: {shot}. "
        f"Narration beat to dramatize: {narration}. "
        "Compose a specific narrative moment, not a generic group portrait. "
        "The people must interact with the environment and props: hands grasp, point, open, carry, write, reach, "
        "or support objects as the action requires. Show contextual details that prove the location and era. "
        "Use varied wide establishing, medium action, over-shoulder and emotional close shots as appropriate. "
        "Hand-drawn 2D animation film aesthetic, sophisticated storyboarding, expressive character acting, "
        "layered painted background, consistent ink weight, restrained cinematic color grading, strong readable silhouettes. "
        "Do not use 3D plastic toy aesthetics, bare stick figures, black line bodies, spherical blank heads, "
        "generic empty backgrounds, random props, or repeated static poses. "
        "If a reference image is provided, use it ONLY to preserve the lead character's face, hair, clothing design, line quality and palette. "
        "Do NOT copy its camera angle, pose, group arrangement, background, furniture, props or composition. "
        "Every scene must be a visibly different illustration with a new camera position and a new physical action. "
        "Never repeat the same group portrait or room layout unless the narration explicitly requires it. "
        "Absolutely no text, fake writing, pseudo-letters, labels, signs, captions, speech bubbles or typography anywhere."
    )[:3000]

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
    reference_path = a.output_dir / "character-reference.jpg"
    reference = reference_path.read_bytes() if reference_path.exists() else None
    generated = 0
    for i, scene in enumerate(scenes[:max(0, a.max_images)]):
        out = a.output_dir / f"scene_{i+1:04d}.png"
        if out.exists() and out.stat().st_size > 50000:
            if i == 0 and not reference:
                with Image.open(out) as image:
                    image = image.convert("RGB")
                    w, h = image.size
                    # Isolate the lead character region so later generations inherit character design,
                    # not the first scene's full group layout and background.
                    crop = image.crop((int(w * 0.22), int(h * 0.08), int(w * 0.68), int(h * 0.94)))
                    canvas = Image.new("RGB", (512, 288), (224, 216, 199))
                    crop.thumbnail((280, 270), Image.Resampling.LANCZOS)
                    canvas.paste(crop, ((512 - crop.width) // 2, (288 - crop.height) // 2))
                    canvas.save(reference_path, "JPEG", quality=92)
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
                        image = image.convert("RGB")
                        w, h = image.size
                        crop = image.crop((int(w * 0.22), int(h * 0.08), int(w * 0.68), int(h * 0.94)))
                        canvas = Image.new("RGB", (512, 288), (224, 216, 199))
                        crop.thumbnail((280, 270), Image.Resampling.LANCZOS)
                        canvas.paste(crop, ((512 - crop.width) // 2, (288 - crop.height) // 2))
                        canvas.save(reference_path, "JPEG", quality=92)
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
