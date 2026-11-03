# StickMotion Studio — Project State

Last updated: 2026-11-03 (milestone: genre pivot)

## Product direction (confirmed)
This is a story-animation studio, not a space/science video maker. The intended channel subjects include history, survival stories, true crime, investigations, disasters, wars, mysteries, and related narrative documentaries.

## Visual identity
Keep the reference look: expressive hand-drawn stick figures, bold black outlines, round heads, readable facial expressions, simple but purposeful sets, props, and occasional perspective rooms. No stock footage or unrelated generic imagery. Build scene-specific visual storytelling.

## User constraints
- User works from an Android phone; no desktop workflow should be required from the user.
- Prioritize free/open-source components and avoid paid APIs/services unless explicitly approved.
- Target output: 16:9, 1920x1080, 30fps MP4 plus SRT.
- Long-term target: paste English narration for a ~15-minute video and generate scene plan, animation, natural English voice, synchronized subtitles, music/SFX and rendered MP4.
- Quality first; validate 60 seconds before scaling to 5 and then 15 minutes.
- Do not claim full AI video generation is implemented until it is actually built and tested.

## Current implementation (2026-11-03)
- Mobile-first static web UI.
- Sentence-based scene planner in src/scene-planner.js.
- Rule-based scene categories: historical, crime, investigation, prison, survival, desert, shipwreck, wilderness, war, disaster, night, conversation, journey and generic explanatory scenes.
- Canvas preview now includes hand-drawn procedural backdrops for historical settings, crime scenes, evidence boards, survival landscapes, deserts, shipwrecks, wilderness, battlefields, disaster aftermath and prison cells.
- Example script now demonstrates a Titanic-style shipwreck survival story.
- CI JavaScript syntax check passed. First genre test run exposed a category-priority collision (prison escape classified as generic survival); prison priority was corrected and a fresh CI run is pending.
- Canvas stick-figure preview with play/pause and scene navigation.
- JSON scene-plan export.
- Node built-in unit tests in tests/scene-planner.test.js.
- GitHub Pages workflow exists; Pages deployment still requires Pages source to be enabled in repository settings.
- No TTS, word-level subtitle alignment, AI semantic planner, sound design, or MP4 renderer is integrated yet.

## Current milestone
Continue refining narrative scene classification and character actions; verify the latest CI run. The earlier space-oriented visuals are no longer the product direction. Keep the project-state file updated after meaningful changes.

## Next milestones
1. Scene-specific sets, props, camera framing and character actions for the target genres.
2. Better sentence/paragraph beat segmentation and shot variety.
3. Structured scene JSON with action, setting, props, camera, mood, narration timing and transition.
4. Free/open-source English TTS and subtitle timing experiments.
5. 60-second rendered MP4 prototype, then quality/performance review.
6. Scale to 5 minutes and finally 15 minutes at 1080p/30fps.

## Development rule
Never confuse a successful static-site deployment with a finished video generator. Record test results, known limitations, and next action here after each milestone.
