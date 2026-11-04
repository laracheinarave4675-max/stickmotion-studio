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
    "Premium stylized 3D animated documentary frame, cinematic miniature-world composition, "
    "classic bare stick figures in a richly dimensional 3D world: a clean white circular head and ONLY thin black straight lines for torso, arms and legs, "
    "one single straight line torso, two straight line arms and two straight line legs, tiny visible circular joints, simple dot eyes, "
    "absolutely no clothing, no tunic, no robe, no jacket, no tie, no shirt, no pants, no shoes, no hands, no feet, no neck, "
    "no shoulders, no chest, no hips, no body volume, no human silhouette; detailed environments, "
    "physically based materials, realistic soft shadows, ambient occlusion, volumetric lighting, "
    "strong foreground-midground-background separation, atmospheric perspective, shallow depth of field, "
    "professional feature-animation quality, carefully composed 16:9 widescreen shot. "
    "Characters must remain stickmen, never realistic human-bodied people. "
    "No lettering, no subtitles, no logos, no watermark, no borders."
)
NEGATIVE = "text, typography, subtitles, captions, logo, watermark, photorealistic humans, realistic human body, muscular anatomy, flat vector art, crude anatomy, detached limbs, extra limbs, gore, extreme close-up, giant head, oversized face, floating head, cropped body, duplicate protagonist, collage, split screen"
def load_scenes(text: str):
    js = "import {buildScenePlan} from './src/scene-planner.js'; console.log(JSON.stringify(buildScenePlan(" + json.dumps(text) + ")));"
    return json.loads(subprocess.run(["node", "--input-type=module", "-e", js], check=True, capture_output=True, text=True).stdout)
def make_prompt(scene: dict, index: int, total: int, protagonist: str) -> str:
    props = ", ".join(scene.get("props", [])[:4]) or "period-appropriate objects integrated naturally into the setting"
    narration = " ".join(scene.get("narration", "").split())
    camera = scene.get("camera", "cinematic medium shot")
    return (
        f"{STYLE}\\n"
        "Create one complete, cohesive stylized 3D animated frame with stickman characters INCLUDED. "
        "Every character must be an unmistakable bare stick figure: one white circular head, one single straight black line torso, "
        "two thin black line arms and two thin black line legs, tiny joint dots, and nothing else. "
        "NO clothing or accessories of any kind: NO hat, NO tie, NO coat, NO tunic, NO robe, NO shirt, NO trousers, NO shoes, NO bag. "
        "NO neck, NO shoulders, NO chest, NO waist, NO hips, NO body mass, NO realistic hands or feet. "
        "Preserve this exact stick-figure silhouette at every camera angle. Add depth through lighting, shadows and 3D environment, "
        "not by turning the characters into realistic humanoids. The protagonist retains the same round head, face marks and accessory. "
        "No detached limbs, duplicate heads or extra arms.\\n"
        f"Scene {index + 1} of {total}. Setting: {scene.get('setting','specific story location')}. "
        f"Visual category: {scene.get('visual','historical')}. Action to visibly depict: {scene.get('action','observing or explaining')}. "
        f"Emotion and facial acting: {scene.get('mood','explaining')}. Important props: {props}. "
        f"Directed camera composition: {camera}.\\n"
        f"Tell this exact narration beat in a single readable visual moment: {narration}\\n"
        "Art direction: premium cinematic 3D animated documentary environment with tiny minimalist 2D line-art stick figures, "
        "the characters remain flat black rods and white circles while the world around them is fully dimensional, "
        "soft contact shadows, ambient occlusion, cinematic rim lighting and realistic bounce light, "
        "detailed layered environments with strong vanishing points and foreground objects, rich material texture, "
        "controlled cinematic color grade, volumetric haze and selective depth of field. Avoid flat vector art, "
        "flat 2D illustration, front-facing diagram layouts, and orthographic compositions. "
        "Vary camera direction between scenes: low-angle perspective, high-angle looking down, three-quarter view, "
        "over-the-shoulder, deep wide establishing shot, diagonal tracking composition, and close-up only when "
        "the narration calls for it. Use visible parallax cues, foreground framing and strong perspective depth. "
        "Use the reference image to preserve protagonist identity and the exact stickman design, but invent "
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
