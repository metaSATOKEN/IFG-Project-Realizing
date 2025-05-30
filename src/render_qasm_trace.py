#!/usr/bin/env python3
"""Render QASM execution trace as a series of images or an animated GIF."""
from __future__ import annotations

import json
import os
from typing import Dict, List

from PIL import Image, ImageDraw, ImageFont

TRACE_PATH = "result/qasm_trace.json"
PNG_DIR = "docs/plot"
GIF_PATH = "result/qasm_trace.gif"


def load_trace(path: str) -> List[Dict]:
    """Return list of trace step dictionaries from ``path``."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def draw_step(step: Dict, font: ImageFont.ImageFont) -> Image.Image:
    """Return an image visualizing ``step``."""
    qubits = step["qubits"]
    width = 220
    height = 30 + 20 * len(qubits)
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    gate = step["gate"]
    args = step.get("args", [])
    title = f"Step {step['step']}: {gate}"
    if args:
        title += f" q[{args[0]}], q[{args[1]}]"
    draw.text((10, 5), title, fill="black", font=font)

    y = 25
    for idx, bit in enumerate(qubits):
        state = "\N{LARGE GREEN SQUARE}" if bit else "\N{BLACK LARGE SQUARE}"
        draw.text((10, y), f"q[{idx:2d}]: {state}", fill="black", font=font)
        y += 20

    return img


def main() -> None:
    trace = load_trace(TRACE_PATH)
    if not trace:
        print(f"Trace file {TRACE_PATH} not found or empty")
        return

    os.makedirs(PNG_DIR, exist_ok=True)
    try:
        font = ImageFont.truetype("DejaVuSansMono.ttf", 14)
    except OSError:
        font = ImageFont.load_default()

    frames = []
    for step in trace:
        img = draw_step(step, font)
        png_path = os.path.join(PNG_DIR, f"qasm_trace_step_{step['step']:03d}.png")
        img.save(png_path)
        frames.append(img)

    if frames:
        frames[0].save(
            GIF_PATH,
            save_all=True,
            append_images=frames[1:],
            duration=600,
            loop=0,
        )

    print(f"Wrote {len(frames)} frames to {PNG_DIR} and {GIF_PATH}")


if __name__ == "__main__":
    main()
