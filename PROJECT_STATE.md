# StickMotion Studio — Project State

Last updated: 2026-11-03 (milestone: first real browser video export path)

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
- Sentence-based scene planner in src/scene-planner.js extracts suggested action, props, setting, camera framing and transition for each narration beat. Past-tense movement verbs (ran/fled/chased) are included.
- Rule-based scene categories: historical, crime, investigation, prison, survival, desert, shipwreck, wilderness, war, disaster, night, conversation, journey and generic explanatory scenes.
- Canvas preview now includes hand-drawn procedural backdrops for historical settings, crime scenes, evidence boards, survival landscapes, deserts, shipwrecks, wilderness, battlefields, disaster aftermath and prison cells.
- Example script now demonstrates a Titanic-style shipwreck survival story.
- CI on commit 44eb5fcd passed both `npm run check` and all scene planner tests. It then failed only at Configure Pages because GitHub Pages is not enabled. The preceding syntax failure was caused by a literal escaped newline in main.js; fixed in 44eb5fcd.
- CI for commit 15e7033a passed JavaScript syntax and all planner tests; only Configure Pages fails because Pages is disabled.
- Supporting-character and expanded-prop commits d5ade7ee and 86ea7c58: syntax and planner tests passed on d5ade7ee; workflow failed only at Configure Pages. Commit 86ea7c58 was superseded/cancelled by subsequent workflow activity.
- Hand-held prop animation commit 17d8d7c2 is pushed; CI run 41723395642 is queued at last check.
- Canvas stick-figure preview with play/pause and scene navigation.
- JSON scene-plan export includes setting, action, props, camera and transition fields alongside narration, mood, visual category and duration.
- Canvas character rig now changes arm poses for running/fighting, searching, hiding and climbing; walking/running animate leg stride. Basic drawn props include water bottle, map, keys, evidence folder and flashlight.
- Storyboard cards display the extracted action, setting and identified props, so the user can inspect the visual plan before export.
- Canvas now adds contextual supporting figures in crime, investigation, war, prison, disaster and shipwreck scenes, in addition to the conversation scene.
- Expanded procedural prop drawings: boat/raft, food/rations, fire, letter/note, clock, rope and a simple non-graphic weapon prop, alongside bottle, map, keys, flashlight and evidence folder.
- Primary character can now visibly hold and carry selected props (water bottle, map, keys, flashlight, letter/note, evidence folder) in a hand pose instead of only displaying them as detached set dressing.
- Node built-in unit tests in tests/scene-planner.test.js.
- GitHub Pages workflow exists; Pages deployment still requires Pages source to be enabled in repository settings.
- No TTS, word-level subtitle alignment, AI semantic planner, sound design, or MP4 renderer is integrated yet.

## Current milestone
Verify CI for 17d8d7c2. Then make held props and gestures semantically selective (not every mentioned object automatically held), add interaction beats such as opening doors/picking up clues, and improve camera framing. Next major milestone remains a 60-second rendered MP4 with voice/subtitles; no real MP4 renderer is connected yet. Next major milestone remains a 60-second rendered MP4 with voice/subtitles; no real MP4 renderer is connected yet. Next major milestone remains a 60-second rendered MP4 with voice/subtitles; no real MP4 renderer is connected yet. The earlier space-oriented visuals are no longer the product direction. Keep the project-state file updated after meaningful changes.

## Next milestones
1. Scene-specific sets, props, camera framing and character actions for the target genres.
2. Better sentence/paragraph beat segmentation and shot variety.
3. Structured scene JSON with action, setting, props, camera, mood, narration timing and transition.
4. Free/open-source English TTS and subtitle timing experiments.
5. 60-second rendered MP4 prototype, then quality/performance review.
6. Scale to 5 minutes and finally 15 minutes at 1080p/30fps.

## Development rule
Never confuse a successful static-site deployment with a finished video generator. Record test results, known limitations, and next action here after each milestone.


## 2026-11-03 continued milestone — animated WebM export
- Added a browser-side animated preview export using canvas.captureStream(30) and MediaRecorder. It records the storyboard scenes in sequence and downloads a silent WebM file. This is a real video-file export path, not MP4 and not a full production render; it has no narration, music, SFX or subtitles.
- Added an Export video control and live status text. Export runs in real time; keep the page open. Browser support and memory limits vary, so start with short storyboards.
- Added planner actions: opening/unlocking, picking up/collecting, helping/rescuing, reaching/handing over, plus unit tests.
- Character rig now has dedicated arm poses for opening, picking up, rescuing and handing/reaching. Prop-in-hand rendering is now conditional on an interaction action or narration that explicitly says carrying/holding/using, reducing unrelated objects appearing in hands.
- Commits: UI/export 8a6961a3, action rules ef07948b, newline/regex fixes 0f265075 and 3cb1c619.
- Earlier run 41723433478 passed syntax and all tests; only Pages setup failed because Pages is not enabled.
- Latest CI for WebM/action-rule commits is pending; interaction pose commit fd25ab91 was just pushed and also needs CI verification.
- Next: add scene duration and total runtime display, robust export cancellation/error cleanup, and test WebM output on Android. Then add generated voice/subtitles and a server-side MP4 path.

## 2026-11-03 continued milestone — export controls and first successful Pages deployment
- User enabled GitHub Pages source as GitHub Actions in repository settings (confirmed by screenshot); this removed the previous Pages configuration blocker.
- Fixed malformed newline in the example narration string in src/main.js.
- Fixed splitNarration in src/scene-planner.js to split at sentence boundaries and paragraph breaks without breaking sentences into individual words.
- Fixed escaped-newline corruption in tests/scene-planner.test.js, including the paragraph-break test and direct object-interaction tests.
- Added estimated total storyboard duration beside the scene count.
- Hardened animated WebM export: progress status, Cancel control, empty-file/error handling, track cleanup, and restoration of the selected scene/playback state after completion or cancellation.
- Current export remains silent WebM recorded in real time; no narration, music, SFX, subtitles, or MP4 encoding.
- Latest validated commit before this log: c587fc33.
- GitHub Actions run 41724933422 completed successfully: JavaScript syntax check passed, all scene planner tests passed, Pages configuration passed, artifact upload passed, and deployment passed.
- Remaining: validate the deployed page and WebM export on Android; then build the 60-second voice/subtitle/MP4 pipeline before scaling.

## 2026-11-03 milestone — subtitle output
- Added optional narration captions drawn directly onto the canvas; because the WebM recorder captures the canvas, captions are burned into exported video when the checkbox is enabled.
- Added SRT subtitle export with scene-based start/end times derived from the storyboard's estimated durations.
- Added an independent Export SRT control and a toggle for burned-in captions.
- SRT generation is scene-timed, not word-aligned; current scene durations remain estimates, so subtitle timing must be reviewed before final publication.
- Browser video output is still silent WebM; MP4 and voice generation are not yet implemented.
- Commits: caption/SRT logic 00c040fb, UI e2e24670, styling 54f265e9, escape correction c3623dc3.
- Latest CI for this milestone is running; confirm syntax, tests and deployment before treating it as validated.
- Next: validate UI/export on mobile browser; implement a 60-second voice + captions + mux/render pipeline with freely available components, then measure runtime/quality.
