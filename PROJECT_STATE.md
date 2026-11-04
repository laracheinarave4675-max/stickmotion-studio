# StickMotion Studio — Project State

Last updated: 2026-11-03 (milestone: Gemini TTS comparison path added)

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

## 2026-11-03 milestone — isolated and tested subtitle utilities
- Extracted SRT timestamp generation, sequential cue generation, and caption line wrapping into src/subtitles.js.
- Main canvas and SRT download now use the shared utility module rather than inline duplicate logic.
- Added unit tests for timestamp formatting, sequential SRT cue timing, and two-line caption truncation.
- Commits: subtitles module dd3dedf6; main integration d8803741; tests 13ef79da.
- CI for this refactor is pending; do not treat it as validated until the latest Actions run completes.
- Known limitation: cue timing follows estimated scene durations and each narration sentence remains a single cue; no word-level forced alignment.

## 2026-11-03 continued milestone — subtitle hardening and CI coverage
- Expanded npm run check to syntax-check src/subtitles.js as well as the main UI and scene planner.
- Hardened caption wrapping for unusually long unbroken words; added tests for long words and empty SRT output.
- Fixed word-boundary detection in character prop-interaction matching so carry/hold/use language is interpreted as intended.
- Updated README to describe current browser WebM and SRT capabilities and clearly state remaining limitations.
- Commits: syntax check b244fcd5; caption edge cases 0ec15544; interaction regex be3fb6bf; tests b6cff218; README e1ed430e.
- Previous subtitle utility CI run 41725786586 completed successfully. Latest expanded test run was triggered by b6cff218 and is pending at the time of this log; README update subsequently triggered another run.
- Current output remains silent WebM plus optional burned captions and a separate scene-estimated SRT. No TTS, music/SFX, word-level alignment or MP4 render pipeline exists yet.
- Next major engineering step: build a bounded 60-second cloud render proof-of-concept using free/open-source TTS and FFmpeg, with strict artifact/runtime limits before considering longer videos.

- Follow-up inspection caught an over-escaped word-boundary regex in the character interaction matcher; corrected it in commit 769f29ef so phrases such as "holding the map" and "using the flashlight" match actual word boundaries.


## 2026-11-03 milestone — Gemini TTS alternative added
- Reassessed Piper: it remains a lightweight fallback, not the assumed quality winner.
- Added `scripts/generate_gemini_voice.py` using the official Google GenAI Python SDK and Gemini audio-generation API. It validates up to 18,000 characters, splits narration at sentence/paragraph boundaries into chunks of up to 2,800 characters, requests a consistent selected voice/style per chunk, joins returned 24 kHz mono 16-bit PCM, and writes one WAV plus metadata.
- Added manual GitHub Actions workflow `.github/workflows/generate-gemini-voice.yml`. It offers Gemini 2.5 Flash TTS and 3.1 Flash TTS preview models, voice and delivery-style inputs, and uploads a 3-day artifact. Requires the user to add a repository Actions secret named `GEMINI_API_KEY`; no API key is stored in the repository.
- Added tests for input limits, chunk splitting/text preservation and WAV header/frame output. Added these tests to the Pages CI syntax/test job.
- Official pricing distinction: Gemini Developer API pricing currently lists free-tier use for certain TTS models; Google Cloud Text-to-Speech pricing is separate and lists no free usage limit for Gemini-TTS there. Free-tier quota/model availability can change, and Gemini API free-tier content may be used to improve Google products. Do not describe Google TTS generically as unlimited/free.
- Piper workflow retained as a no-key fallback. README now documents Gemini workflow and key setup.
- Important validation boundary: code and unit tests are wired into CI, but the Gemini workflow has not yet been run with a real API key. No Gemini WAV exists yet; no real voice quality, quota, chunk-join continuity, or 15-minute duration is verified. Audio is still not merged into MP4.
- Next: inspect CI result; then user adds a free Gemini API key in GitHub Actions secrets and runs a 1–2 minute sample first. Listen to the WAV and compare it with Piper before selecting a default. After voice acceptance, integrate narration WAV + SRT with a bounded 60-second FFmpeg MP4 renderer.


## 2026-11-03 — narrator voice selection updated
- User listened to the first Gemini TTS sample and approved its quality, but requested a male narrator instead of the female Kore voice.
- Changed Gemini generator default voice from Kore to Charon.
- Changed workflow choices to male voices only: Charon, Iapetus, Rasalgethi, Algieba, Orus, Alnilam, Schedar, Sadaltager, Fenrir and Puck.
- Charon is the recommended documentary default: Google lists it as male and describes it as informative. Iapetus is a clear alternative; Rasalgethi is another informative option. Source: Google Gemini TTS voice documentation.
- Updated default delivery direction to measured, warm, authoritative documentary narration without exaggerated announcer delivery.
- User's first female-voice sample was approved for quality. Male Charon has not yet been generated/listened to; the next run should verify the chosen male timbre before locking it for production.


## 2026-11-03 milestone — first cloud MP4 renderer implemented (validation pending)
- Added `scripts/render_video.py`: uses the existing JavaScript scene planner to convert narration into scene-aware shots, draws animated stick figures and simple contextual sets/props with Pillow at 1920×1080/30fps, burns in scene-timed narration captions, and streams frames into FFmpeg to mux the generated mono WAV into H.264/AAC MP4.
- Added manual workflow `.github/workflows/render-pilot.yml`: accepts 1–1,800 narration characters, generates a Gemini TTS WAV using the selected male voice (default Charon), rejects rendered audio longer than 90 seconds, creates MP4/SRT/JSON metadata, and uploads a 3-day artifact.
- This is the first server-side MP4 path and removes the need for the user's phone browser to render frames. It is a bounded prototype, not yet a polished full video product.
- Visuals are procedural stick-figure animation with scene-category backgrounds, selected props, action poses and limited motion; no AI-generated character animation, music/SFX, or word-level subtitle alignment yet. Captions are scene-timed based on narration word counts.
- Target render is 1080p/30fps. Runtime, memory, actual MP4 playback, audio sync and visual quality are not yet validated; do not scale beyond the short pilot until an actual artifact is inspected.
- The Charon voice workflow was successfully run by the user (Gemini workflow run 41731303521, conclusion success). The user has approved Charon as the fixed default narrator voice.
- New commits: renderer 3004d863; pilot workflow 05dcd419.
- Next: verify Pages CI after these commits, run the new pilot workflow with a short narration, inspect MP4 metadata and representative frames, fix any rendering defects, then extend limits toward 5 minutes and 15 minutes.


## 2026-11-03 follow-up — renderer regression coverage
- Fixed caption handling so long narration sentences rotate through two-line caption pages rather than silently truncating after the first two lines.
- Expanded action-pose mapping for object handoffs, rescue, discovery, climbing and water struggle; improved prop drawing for photographs, notes and rafts.
- Added `tests/test_render_video.py` to verify the Node scene-planner contract, a real 1920×1080 RGB frame, and multi-page long-caption handling.
- Pages CI now installs Pillow and runs the renderer regression tests in addition to existing JS and TTS tests.
- Validation status: waiting for the latest Pages CI run. The cloud MP4 pilot has not yet been dispatched and no MP4 artifact has been verified.


## 2026-11-03 milestone — original soundtrack and narration ducking
- Added `scripts/generate_music.py`, a dependency-free procedural music synthesizer that creates an original stereo 24 kHz PCM underscore without stock tracks or sampled copyrighted music. It selects a broad mood family from the opening scene (suspense/minor/epic) and creates a gentle evolving harmonic bed.
- Integrated soundtrack generation into the MP4 renderer. FFmpeg now automatically ducks the music when narration is present, then mixes both into the final AAC track; the voice remains the foreground.
- The pilot artifact now also includes `music.wav`; metadata records the soundtrack method and clearly notes that recorded spot SFX are not yet included.
- Added regression coverage for WAV channel count, sample format, sample rate, duration and mood selection.
- This is original synthesized underscore, not a professional recorded score. Actual perceptual balance and music quality still need listening against a real rendered MP4. No MP4 pilot has yet been run/inspected.
- Latest Pages CI before this change: run 41734004410 succeeded, including JavaScript/Python checks, planner and renderer tests, and GitHub Pages deployment.
- Next: confirm CI after soundtrack integration, then run the short MP4 pilot and inspect the actual video/audio before expanding runtime or adding more elaborate SFX.


## 2026-11-03 milestone — narration-aware synthetic sound effects
- Added `scripts/generate_sfx.py`: reads the narration and planned scenes, selects simple original synthetic cues for matching events (door/key, footsteps, water, wind, impact, fire, reveal), and places them at the corresponding scene time. It generates stereo PCM directly; no sample library or paid SFX service is required.
- Integrated SFX into the MP4 audio mixer alongside Charon voice and procedural music. The music is ducked under speech; SFX sit at a restrained level and the final mix has a limiter.
- The pilot artifact now includes the SFX WAV. Added tests for cue selection by story content and generated signal output.
- Boundary: these are synthetic design cues, not detailed recorded Foley or cinematic battle/ambience recordings. Actual listening/mix review is still required; no rendered MP4 has been inspected yet.
- Previous CI run after adding soundtrack (41735219485) succeeded. CI for this SFX batch is pending.
- Next validation: check Actions test/deploy outcome; then run the short manual MP4 pilot once and inspect real playback before expanding video duration.

## 2026-11-03 — first successful MP4 pilot and CI follow-up
- Manual workflow `Render StickMotion 60-second MP4 pilot` completed successfully on commit `c28e9cff05f87a8e00c23f1980627916bd330457`; run ID `41737208677`.
- Confirmed successful steps: dependency installation, narration validation, Gemini Charon voice generation, animated MP4/SRT render, and artifact upload. Artifact `stickmotion-mp4-pilot` exists (10,262,182 bytes) and expires 2026-11-06. This verifies the pipeline produced and uploaded its outputs, but visual/audio quality has not yet been inspected.
- The separate Pages/CI run `41736998951` passed JavaScript syntax checks and all 13 Node tests, then failed at Python compilation because `tests/test_render_video.py` contained literal escaped newline sequences between the music and SFX imports.
- Fixed those separators as real source newlines in commit `6ee782a6a5c8e04a9a4ab002ddc08e6ace8b1628`. CI for this fix must still be checked; do not mark the full CI green until then.
- Next: user downloads and uploads the MP4 from the successful pilot artifact for frame-by-frame, audio, subtitle and pacing review; independently verify the CI run triggered by the test fix.


## 2026-11-04 — reference style approved; visual redesign direction recorded
- User supplied visual examples from two historical story-animation videos and explicitly approved them as the target for StickMotion Studio.
- The target is a directed illustrated 2D story documentary: expressive varied characters with clothes and face acting; complete story-specific locations and props; deliberate wide/medium/close-up shot grammar; atmospheric color/light; continuity; and purposeful camera/editing rhythm.
- The current procedural renderer (single generic figure, simplified background primitives, limited action loops) is not considered close enough to the target. A successful CI/MP4 export is not a quality milestone.
- Added `docs/REFERENCE_ANIMATION_DIRECTION.md` on branch `reference-style-animation` with the approved art direction, pipeline principles, quality gates, and hybrid illustrated-scene strategy.
- Next engineering step: inspect the existing renderer and replace the generic composition in bounded stages—first a character/environment asset-composition layer and shot-framing controls, then a short pilot to inspect. If primitive drawing cannot meet the style, change scene construction instead of adding cosmetic effects.
- Quality gate: user must review the actual rendered video and approve the visual result before scaling to long runtime. No claim of target-level quality is made yet.


## 2026-11-04 — first illustrated-scene renderer implementation
- Replaced the single primitive stick-person frame with a lightweight illustrated 2D scene renderer in `scripts/render_video.py`.
- New renderer composes location-specific streets/interiors, period-like building facades, room architecture, furniture, landscape layers, varied clothed character silhouettes, hair/headwear variants, facial expressions, hand gestures, scene props, crowd/supporting characters, wide/medium/close framing, subtle camera drift/zoom, and a restrained vignette.
- Kept the existing bounded MP4, voice, SRT, music and SFX pipeline and the 90-second cap. This is a procedural illustrated renderer, not yet frame-by-frame character animation or AI-generated artwork; it is an intermediate engineering step toward the approved references.
- Fixed subtitle compositing so captions are drawn onto the final processed frame.
- Expanded `tests/test_render_video.py` to check distinct camera framing and minimum visual complexity.
- Added `.github/workflows/reference-renderer-tests.yml` to run JavaScript and Python checks on this branch and pull requests.
- Commits on `reference-style-animation`: renderer replacement `9de555c`, subtitle overlay fix `ca73c1e`, supporting cast/vignette `beffb68`, visual tests `ad1db91`, renderer CI `2ffc001`.
- Validation is pending GitHub Actions. Do not treat the renderer as validated until CI passes and a new MP4 is rendered and visually reviewed.
- Next: resolve any CI failures, then render a fresh short pilot using the same Charon/MP4 workflow and inspect actual output. If procedural art still falls short, move to reusable authored/generated illustrated assets and rigged animation rather than polishing generic vector figures.


## 2026-11-04 — first CI failure diagnosed and corrected
- The new reference-renderer workflow successfully ran JS syntax checks, all 13 Node tests, Python compilation, 4 voice tests, and 5 Gemini voice tests. The renderer-specific framing/visual-complexity tests also passed.
- One existing SFX test exposed an event-priority bug: the word "hit" in "waves hit the raft" was classified as a generic impact before the water cue. Removed the overly broad generic "hit" token from the impact matcher; explicit collision terms remain.
- Fix commit: `346a134d905f4acc924627055129d4adca06f491`. Awaiting rerun of the full workflow.


## 2026-11-04 — automatic visual proof render added
- Added `.github/workflows/illustrated-visual-proof.yml`: on updates to the reference branch it creates a short English historical-story narration, synthesizes a temporary open-source espeak-ng voice, renders the actual 1080p MP4 through the new illustrated renderer, and uploads MP4/SRT/metadata as a 3-day artifact.
- This proof is for visual pipeline validation only; espeak-ng is not the chosen production narrator. The Charon/Gemini workflow remains the intended voice path.
- Awaiting the first complete rendered artifact and inspection of its frames/metadata before claiming the new visual approach works end-to-end.


## 2026-11-04 — visual proof workflow made deterministic
- Removed the package-manager dependency from the visual proof workflow after the hosted runner spent excessive time in apt installation.
- The proof now uses the runner's FFmpeg and a small deterministic mono test track generated in Python. It validates frame composition, MP4 encoding, scene sequencing and subtitles; it is explicitly not a voice-quality or final audio-mix test.
- Renderer metadata now describes its audio input generically as a supplied mono narration WAV.


## 2026-11-04 — portable FFmpeg resolution
- The first proof render exposed that FFmpeg is not present on the runner image and the previous apt-based setup was not reliable.
- Renderer now resolves FFmpeg from PATH or falls back to the bundled executable supplied by `imageio-ffmpeg`.
- Both visual-proof and manual Charon pilot workflows now install `imageio-ffmpeg` through pip rather than relying on apt mirrors.
- Awaiting a fresh proof render with the bundled encoder.
