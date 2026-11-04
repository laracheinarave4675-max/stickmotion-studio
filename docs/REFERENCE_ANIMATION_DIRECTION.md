# StickMotion Studio — Reference Animation Direction

Status: approved visual target; implementation work starts from the current procedural renderer.
Reference: user-provided screenshots from the two WWI/WWII story-animation videos (2026-11-04).

## Non-negotiable target
Produce a narrated, illustrated story-cartoon—not a bare stick-figure slideshow and not a canvas with a few primitive shapes. A successful output should feel like a deliberately directed animated documentary with scenes that explain and dramatize the narration.

## Visual grammar extracted from the references
- Character design: recognizable illustrated people with white/light faces, bold ink outlines, readable eyes and brows, distinct hair/headwear, clothing silhouettes, and emotion-specific mouth/face shapes. Crowd members should vary rather than clone one identical rig.
- Environments: complete scene-specific locations (streets, interiors, classrooms, offices, battle locations, homes), with perspective, architecture, furniture, props, and depth layers.
- Shot language: wide establishing shots, group compositions, medium action shots, close-ups for emotional beats, and occasional stylized explanatory frames. Frame choice must reflect the narration beat.
- Art direction: hand-drawn 2D cartoon; controlled ink linework; muted, story-appropriate palette; warm interiors and daylight scenes contrasted with cold/dark dramatic scenes; intentional shadows and light.
- Story continuity: recurring protagonists keep their design, clothing, and relevant objects between adjacent shots. Props are placed and used, not arbitrarily scattered.
- Editorial rhythm: scene changes follow narrative ideas; visual variety is meaningful. Use pans/push-ins, reframing, cuts, and selective transitions rather than a repetitive motion loop.
- Tone: historical/war scenes may be dramatic but should remain non-graphic; use visual metaphors when needed.

## Pipeline principles
1. Segment narration into visual beats, not just sentences. Each beat needs a subject, action, location, emotional state, key prop, shot size, and transition.
2. Build/reuse illustrated assets (characters, poses, backgrounds, props) and compose them into scenes. Do not depend on one generic procedural person to represent every line.
3. Animate scene layers and character parts with restrained purposeful movement; camera motion supports the action.
4. Preserve narrator-led pacing and keep subtitles unobtrusive. Music and sound effects are subordinate to voice and specific events.
5. Keep the phone as the user's control surface; heavy rendering occurs in GitHub Actions/cloud.
6. Work in short pilots first. Never scale runtime until a rendered artifact is visually reviewed.

## Quality gates
- A 60-second pilot must demonstrate multiple scene types, character identity and expression, actual story-specific set dressing, varied shot framing, and meaningful animation.
- The result must be reviewed as video—not judged only by CI, frame dimensions, or successful MP4 encoding.
- If the procedural drawing approach cannot meet the reference art direction, replace the scene construction approach rather than decorating the current generic stick figure.
- No claim of reference-level quality until the user reviews and approves the artifact.

## Implementation strategy
Use a hybrid illustrated-scene approach: reusable drawn character/prop assets and composed environment artwork, with lightweight 2D rigging and camera motion. Reserve generated imagery or heavier techniques for cases where they are available within the user's no-budget constraint and can preserve style/continuity. Avoid assuming paid image/video APIs.
