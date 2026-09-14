#!/bin/bash
set -e
cd "$(dirname "$0")"
rm -rf media/
manim -qm tracer_diffusion.py TracerDiffusion
cd media/videos/tracer_diffusion/720p30
ffmpeg -y -i TracerDiffusion.mp4 -vf "fps=15,scale=960:-1,palettegen=stats_mode=full" palette.png
ffmpeg -y -i TracerDiffusion.mp4 -i palette.png -lavfi "fps=15,scale=960:-1[x];[x][1:v]paletteuse=dither=floyd_steinberg" ../../../../TracerDiffusion.gif
