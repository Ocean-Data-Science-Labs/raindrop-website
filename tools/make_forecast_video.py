"""The "What does it look like?" video: the example chart scrolling down inside the square box, then back up (a loop).

    uv run --quiet --with imageio --with imageio-ffmpeg --with pillow --with numpy python tools/make_forecast_video.py
Writes assets/example-forecast.mp4 (H.264, no sound) and assets/example-forecast-poster.jpg (the first frame).
"""
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image

SITE = Path(__file__).resolve().parents[1]
SIZE, FPS = 720, 30  # the box is 353 CSS px; 720 px stays sharp on 2x screens
HOLD_TOP, DOWN, HOLD_BOTTOM, UP = 1.5, 11.0, 2.0, 2.5  # seconds

chart = Image.open(SITE / "assets/example-forecast-mornington.png").convert("RGB")
chart = chart.resize((SIZE, round(chart.height * SIZE / chart.width)), Image.LANCZOS)
pixels = np.asarray(chart)
travel = pixels.shape[0] - SIZE
ease = lambda t: t * t * (3 - 2 * t)  # smoothstep: starts and stops gently

offsets = ([0] * int(HOLD_TOP * FPS)
           + [travel * ease(i / (DOWN * FPS)) for i in range(int(DOWN * FPS))]
           + [travel] * int(HOLD_BOTTOM * FPS)
           + [travel * (1 - ease(i / (UP * FPS))) for i in range(int(UP * FPS))])
out = SITE / "assets/example-forecast.mp4"
with imageio.get_writer(out, fps=FPS, codec="libx264", quality=None, pixelformat="yuv420p", macro_block_size=16,
                        ffmpeg_params=["-crf", "24", "-preset", "slow", "-movflags", "+faststart", "-an"]) as w:
    for y in offsets:
        w.append_data(pixels[round(y):round(y) + SIZE])
Image.fromarray(pixels[:SIZE]).save(SITE / "assets/example-forecast-poster.jpg", quality=85)
print(f"{out.name}: {len(offsets) / FPS:.1f} s, {out.stat().st_size / 1e6:.2f} MB; scroll {travel} px")
