# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Manim Community Edition animations of electron-phonon coupling phenomena (Holstein, Peierls, polaron, diffusion) for embedding as GIFs in PowerPoint presentations. All outputs use white backgrounds and dark-colored elements.

## Rendering Commands

The manim conda environment must be active (`mamba activate manim`). Run from the project root:

```bash
# Render a scene as MP4 (medium quality, 720p 30fps)
manim -qm electron_phonon.py SceneName

# Convert MP4 to clean GIF (two-pass ffmpeg palette method avoids color artifacts)
cd media/videos/electron_phonon/720p30
ffmpeg -y -i SceneName.mp4 -vf "fps=15,scale=960:-1,palettegen=stats_mode=full" palette.png
ffmpeg -y -i SceneName.mp4 -i palette.png -lavfi "fps=15,scale=960:-1[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5" ../../../../../../SceneName.gif
```

Do NOT use manim's built-in `--format gif` — it produces poor palette quantization (grey/black becomes yellow/green). Always render MP4 first, then convert with ffmpeg.

Clear manim's render cache when code changes aren't reflected: `rm -rf media/`

## Architecture

Single file `electron_phonon.py` with all Scene classes. `manim.cfg` sets `background_color = WHITE`.

**Scenes:** `HolsteinCoupling`, `PeierlsCoupling`, `Polaron`, `Diffusion`

**Animation pattern:** `ValueTracker` + `add_updater`/`always_redraw` for continuous motion. For seamless GIF looping, animate the tracker through exact multiples of `TAU` with `rate_func=linear`.

**Key conventions:**
- White background means all elements must use dark colors (BLACK for outlines/bonds, BLUE for electrons). Text defaults to WHITE in manim — always set `color=BLACK` explicitly.
- Ions: `Circle` with `fill_color=WHITE, fill_opacity=1` so bond lines don't show through.
- Dynamic bonds between moving ions use `always_redraw(lambda: Line(...))` since Line endpoints are baked at construction.
- Lambda closures in loops require default-arg capture: `lambda m, i=i: ...`
- The manim source repo is at `../manim` (ManimCE v0.19.1) for API reference.

## GIF Size Guidelines

For PowerPoint-friendly file sizes: use `fps=15,scale=960:-1` in the ffmpeg conversion. Full 720p 30fps GIFs can exceed 5MB for complex scenes (e.g., Polaron with 2D lattice).
