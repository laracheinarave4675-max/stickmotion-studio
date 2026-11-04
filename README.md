# StickMotion Studio

A mobile-first animated storytelling studio for history, survival, true crime, investigations, disasters, wars and other narrative documentaries.

## Current prototype
- Responsive script editor for phone screens.
- Sentence-to-scene storyboard planner.
- Genre-aware visual classification: history, crime, investigation, survival, desert, shipwreck, wilderness, war, disaster, prison, night, conversation and journey.
- Expressive stick-figure preview, scene navigation and JSON scene-plan export.
- Browser-side animated WebM preview export (real-time recording; silent).
- Optional burned-in narration captions and separate scene-timed SRT export.
- Estimated storyboard runtime, export progress and cancellation.
- Dependency-free Node.js unit tests.

## Visual direction
The approved target is a cinematic illustrated story-cartoon: expressive, varied characters with clear faces and clothing; richly dressed, story-specific streets and interiors; props that matter to the narration; wide, medium and emotional close-up shots; muted painted color, ink outlines, lighting and camera movement. Do not settle for bare stick figures, empty backgrounds or unrelated stock footage.

## Current limitations
The scene planner is still rule-based. When Cloudflare Workers AI credentials are configured, the MP4 renderer can use bespoke AI-generated scene illustrations; these are still images animated with camera moves and dissolves, not frame-by-frame character animation. Without those credentials, the procedural illustrated fallback is used. Scene timing and subtitles remain word-count estimates rather than word-level alignment.

## Output target
1920x1080, 16:9, 30fps, MP4 plus separate SRT.

## Roadmap
1. Genre-specific scene planning and animated sets.
2. Richer character actions, props, camera framing and transitions.
3. Structured AI scene planner.
4. Free/open-source English TTS and accurate subtitle timing.
5. 60-second MP4 validation, then 5-minute and 15-minute rendering.

See [PROJECT_STATE.md](PROJECT_STATE.md) for the durable project log and current next steps.

## Run locally
Open index.html in a modern browser, or serve this folder with a static web server. Run syntax checks with `npm run check` and tests with `npm test`.

## Deployment
Enable GitHub Pages in repository Settings → Pages and choose GitHub Actions as the source.

## Short narration voice test (free cloud workflow)

The repository includes an optional manual Piper TTS workflow. It runs on a GitHub-hosted CPU runner and does not require a paid TTS API or a secret key.

1. Open [Actions → Generate short narration voice](https://github.com/laracheinarave4675-max/stickmotion-studio/actions/workflows/generate-voice.yml).
2. Choose **Run workflow**, paste a short English narration (maximum 1,200 characters), and choose a Piper voice.
3. Wait for the workflow to finish, open its run, and download the `stickmotion-piper-voice` artifact. It contains a WAV file, metadata JSON and the input text.

This is a bounded prototype, not a 15-minute production service. GitHub Actions availability and usage limits apply. Piper is an open-source engine; individual voice model terms should be checked before commercial use. The generated WAV is not yet automatically merged into the browser WebM export or an MP4.


## Gemini TTS long-form voice workflow (new)

A second voice path is available for quality comparison. It uses the Gemini Developer API (not Google Cloud Text-to-Speech billing) and generates WAV audio from narration in sentence-aware chunks.

1. Create a Gemini API key in [Google AI Studio](https://aistudio.google.com/).
2. In the GitHub repository, open Settings → Secrets and variables → Actions → New repository secret.
3. Name the secret `GEMINI_API_KEY` and paste the key as its value. Never put the key in a workflow input, source file, or chat.
4. Open [Actions → Generate narration with Gemini TTS](https://github.com/laracheinarave4675-max/stickmotion-studio/actions/workflows/generate-gemini-voice.yml), choose Run workflow, paste up to 18,000 characters, choose a male voice/model/style, and run.
5. Download the `stickmotion-gemini-voice` artifact when complete.

The workflow defaults to `gemini-2.5-flash-preview-tts`; `gemini-3.1-flash-tts-preview` is also selectable. It joins 2,800-character narration chunks into one 24 kHz mono WAV. This is a long-form experiment, not yet a proven 15-minute production pipeline: actual account quota, model access, audio continuity and pronunciation must be tested. Gemini API free-tier availability and limits can change; Google Cloud Text-to-Speech has separate billing rules. The free Gemini API tier may use submitted data to improve Google products, so do not submit private or sensitive narration.

The Piper workflow remains as a no-key fallback. Neither voice path is yet muxed automatically into the MP4 renderer.


## Cloud MP4 pilot (bounded test)
The manual **Render StickMotion 60-second MP4 pilot** workflow creates a short narrated video without requiring a local computer. It uses the repository's Gemini API secret (`GEMINI_API_KEY`), the selected Gemini male voice (default: Charon), the story-aware scene planner, the illustrated Pillow renderer, and FFmpeg. If Cloudflare AI secrets are configured, it first creates bespoke scene artwork with FLUX.2 Klein 4B and uses those images as animated scene plates. The output artifact contains an H.264/AAC MP4, an SRT file, narration WAV, generated music WAV, event SFX WAV, and render metadata.

This is a deliberately bounded proof of concept: narration is limited to 1,800 characters and rendered audio to 90 seconds. The fallback renderer uses scene-aware procedural sets, poses, props and simple motion. The AI-image path creates a new illustrated image per scene, then applies Ken Burns camera movement and dissolves; it is not yet full frame-by-frame character animation. An original procedural cinematic music bed is automatically ducked under the narrator, and simple synthetic sound-effect cues are selected from story events (doors/keys, steps, water, wind, impacts, fire and reveals). These are generated sounds, not recorded foley; precise word-level subtitle alignment is not included. GitHub Actions usage is subject to the account's available minutes and quotas; do not assume unlimited free rendering.

To run it: open **Actions → Render StickMotion 60-second MP4 pilot → Run workflow**, paste a short English narration, keep Charon selected, and download the `stickmotion-mp4-pilot` artifact when the run succeeds. Inspect the actual MP4 before using longer scripts.


Renderer notes: long captions are paginated into readable two-line screens during each scene. The CI suite includes a frame-rendering regression test to catch mismatches between the story planner and the MP4 renderer.


## Optional AI-generated scene artwork (Cloudflare Workers AI)

The renderer can replace its procedural scene drawings with bespoke 2D illustrations generated from each narration beat. It uses Cloudflare's hosted **FLUX.2 Klein 4B** model and reuses the first generated scene as a visual reference for later scenes to encourage character and style continuity.

Cloudflare Workers AI currently includes **10,000 Neurons per day on the Free Workers plan**, resetting at 00:00 UTC. This is a daily allowance, not unlimited generation; requests stop when the free allocation is exhausted. FLUX.2 Klein 4B supports multi-reference images and fixed four-step generation. Check Cloudflare's current pricing and model terms before large runs.

To enable the optional path:

1. In Cloudflare, open Workers AI → Use REST API and create a token with **Workers AI Read** and **Workers AI Edit** permissions. Copy the Account ID.
2. In GitHub, open Settings → Secrets and variables → Actions.
3. Add repository secrets named \`CLOUDFLARE_ACCOUNT_ID\` and \`CLOUDFLARE_API_TOKEN\`.
4. Run **Actions → Render StickMotion 60-second MP4 pilot**. The workflow generates scene images before rendering. If either secret is absent, it uses the local illustrated fallback instead.
5. Download the \`stickmotion-mp4-pilot\` artifact and review the actual video.

The generator saves one image per planned scene, defaults to a bounded number of images, reuses a small reference image for visual continuity, and can resume by skipping existing scene files. AI scene images are 1024×576 and are upscaled to 1920×1080 in the final MP4. This improves the illustrated look but does not create full character rig animation; camera motion and dissolves animate the still artwork. Never place API tokens in source files or workflow inputs.
