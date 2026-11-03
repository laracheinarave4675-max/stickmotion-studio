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
Expressive hand-drawn stick figures with bold black outlines, readable faces, purposeful props and environments designed for each narration beat. Avoid unrelated stock footage and avoid defaulting to space imagery. The scene should communicate what the narration is describing.

## Current limitations
The planner is rule-based, not an AI model. The current animation is procedural and the browser export is silent WebM, not MP4. SRT and burned-in captions use estimated scene timing, not word-level alignment. Natural English narration, music, sound effects, audio mixing and server-side MP4 rendering are not connected yet.

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
