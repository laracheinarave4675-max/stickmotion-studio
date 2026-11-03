# StickMotion Studio

A mobile-first animated storytelling studio for history, survival, true crime, investigations, disasters, wars and other narrative documentaries.

## Current prototype
- Responsive script editor for phone screens.
- Sentence-to-scene storyboard planner.
- Genre-aware visual classification: history, crime, investigation, survival, desert, shipwreck, wilderness, war, disaster, prison, night, conversation and journey.
- Expressive stick-figure preview, scene navigation and JSON export.
- Dependency-free Node.js unit tests.

## Visual direction
Expressive hand-drawn stick figures with bold black outlines, readable faces, purposeful props and environments designed for each narration beat. Avoid unrelated stock footage and avoid defaulting to space imagery. The scene should communicate what the narration is describing.

## Current limitations
The planner is rule-based, not an AI model. The current preview is a prototype, not a rendered video. Natural English narration, word-level subtitles, sound effects, music mixing and MP4 rendering are not connected yet.

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
Open index.html in a modern browser, or serve this folder with a static web server. Run tests with `npm test`.

## Deployment
Enable GitHub Pages in repository Settings → Pages and choose GitHub Actions as the source.
