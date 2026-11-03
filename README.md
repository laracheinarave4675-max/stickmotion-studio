# StickMotion Studio

A mobile-first prototype for turning narration into expressive stick-figure storyboards.

## What works now

- Responsive script editor designed for phone screens.
- Automatic sentence-to-scene grouping.
- Lightweight keyword-based scene and mood classification.
- Multiple procedural visual environments: room, night, space, clock/time, conversation, journey and science concept.
- Animated stick-figure poses and expressions.
- Play/pause, previous/next scene navigation and scene progress.
- Export of an editable JSON scene plan.

## What is not connected yet

This is not yet the complete AI video generator. It does not currently generate narration, word-level subtitles, AI-planned shot instructions, sound effects, or downloadable MP4 files. The scene classifier is rule-based and is intended as a temporary baseline before adding a proper planning model.

## Visual direction

Expressive hand-drawn stick figures with bold black outlines, readable facial expressions, simple environments and purposeful props. The goal is to visualize the meaning of each narration beat, not to use unrelated stock footage.

## Roadmap

1. Validate the visual direction and mobile storyboard experience.
2. Improve character rigging, pose variety, scene composition and camera language.
3. Introduce structured AI scene planning with editable shot descriptions.
4. Add natural English narration and accurate subtitle alignment.
5. Add cloud rendering and validate a 60-second MP4.
6. Scale carefully to 5 minutes, then 15 minutes at 1080p/30fps.

## Run

Open index.html in a modern browser, or serve this repository with any static web server.

## Deployment

The repository includes a GitHub Actions workflow for GitHub Pages. In repository Settings → Pages, choose **GitHub Actions** as the build and deployment source. The site will then deploy after a workflow run succeeds.

## Output format target

1920×1080, 16:9, 30fps, MP4 with a separate SRT subtitle file.

## License

To be decided before incorporating third-party code or assets.
