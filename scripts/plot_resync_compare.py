"""Generate comparison plot for Resync control strategies.

Creates figure D-2 comparing Fixed and Adaptive Resync methods. The figure
contains a bar chart of mean recovery time and Resync count and an
illustrative $\lambda(t)$ comparison plot. The script falls back to a minimal
SVG output if matplotlib is unavailable.
"""

import os
from pathlib import Path

try:
    import matplotlib.pyplot as plt  # type: ignore
    plt.rcParams.update({"font.family": "sans-serif"})
except Exception:  # pragma: no cover - used when matplotlib is absent
    plt = None

TIME_VALS = [9.4, 6.8]
COUNT_VALS = [7, 2]
LABELS = ["Fixed Resync", "Adaptive Resync"]
_DEF_TIMES = list(range(0, 100, 5))


def _gen_lambda(triggers):
    """Generate sample lambda(t) curve given trigger times."""
    cur = 0.95
    lam = []
    idx = 0
    for t in _DEF_TIMES:
        if idx < len(triggers) and t >= triggers[idx]:
            cur = 0.95
            idx += 1
        else:
            cur -= 0.003
        lam.append(cur)
    return lam

LAM_FIXED = _gen_lambda([15, 30, 45, 60, 75, 90, 95])
LAM_ADAPT = _gen_lambda([30, 80])
LAM_SAFE = 0.75

def _plot_mpl(out_path: str) -> None:
    fig, (ax_bar, ax_line) = plt.subplots(1, 2, figsize=(8, 4))

    x = range(len(LABELS))
    width = 0.35

    bar1 = ax_bar.bar([i - width / 2 for i in x], TIME_VALS, width,
                       label="Mean Recovery Time")
    ax_bar.set_ylabel("Time [s]")

    ax_bar2 = ax_bar.twinx()
    bar2 = ax_bar2.bar([i + width / 2 for i in x], COUNT_VALS, width,
                       color="orange", label="Resync Count")
    ax_bar2.set_ylabel("Count")

    ax_bar.set_xticks(list(x))
    ax_bar.set_xticklabels(LABELS)

    lines = list(bar1) + list(bar2)
    labels = [b.get_label() for b in lines]
    ax_bar.legend(lines, labels)

    ax_line.plot(_DEF_TIMES, LAM_FIXED, label="Fixed Resync")
    ax_line.plot(_DEF_TIMES, LAM_ADAPT, label="Adaptive Resync", linestyle="--")
    ax_line.axhline(LAM_SAFE, color="black", linestyle=":")
    ax_line.set_xlabel("Time [s]")
    ax_line.set_ylabel(r"$\lambda(t)$")
    ax_line.legend()

    fig.suptitle("図D-2 – Resync制御方式の比較（固定 vs Adaptive）")
    fig.tight_layout()
    Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path)
    plt.close(fig)

def _plot_svg(out_path: str) -> None:
    width, height = 640, 360
    sub_w, sub_h = 250, 250
    space = 40
    left = 50
    top = 40
    bottom = 40

    axA_x = left
    axB_x = left + sub_w + space

    def x_bar(ax_x, i, offset):
        return ax_x + 60 + i * 120 + offset

    max_time = max(TIME_VALS) * 1.1
    max_count = max(COUNT_VALS) * 1.2
    scale_time = (sub_h - bottom) / max_time
    scale_count = (sub_h - bottom) / max_count

    def y_time(v):
        return top + sub_h - v * scale_time

    def y_count(v):
        return top + sub_h - v * scale_count

    max_t = _DEF_TIMES[-1]
    scale_x_line = sub_w / max_t
    lam_min, lam_max = 0.72, 0.96
    scale_y_line = sub_h / (lam_max - lam_min)

    def x_line(ax_x, t):
        return ax_x + t * scale_x_line

    def y_line(v):
        return top + sub_h - (v - lam_min) * scale_y_line

    parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>",
        "  <style>text { font-family: sans-serif; font-size: 12px; }</style>",
    ]

    parts.append(f"  <line x1='{axA_x+40}' y1='{top+sub_h}' x2='{axA_x+sub_w}' y2='{top+sub_h}' stroke='black' />")
    parts.append(f"  <line x1='{axA_x+40}' y1='{top}' x2='{axA_x+40}' y2='{top+sub_h}' stroke='black' />")
    parts.append(f"  <line x1='{axA_x+sub_w}' y1='{top}' x2='{axA_x+sub_w}' y2='{top+sub_h}' stroke='orange' />")

    bar_w = 20
    for i in range(2):
        bx = x_bar(axA_x, i, -bar_w/2)
        by = y_time(TIME_VALS[i])
        parts.append(f"  <rect x='{bx}' y='{by}' width='{bar_w}' height='{top+sub_h-by}' fill='steelblue' />")
        bx2 = x_bar(axA_x, i, bar_w/2)
        by2 = y_count(COUNT_VALS[i])
        parts.append(f"  <rect x='{bx2}' y='{by2}' width='{bar_w}' height='{top+sub_h-by2}' fill='orange' />")
        tx = x_bar(axA_x, i, 0)
        parts.append(f"  <text x='{tx}' y='{top+sub_h+15}' text-anchor='middle'>{LABELS[i]}</text>")

    lg_x = axA_x + sub_w - 30
    lg_y = top + 10
    parts.append(f"  <rect x='{lg_x}' y='{lg_y}' width='12' height='12' fill='steelblue' />")
    parts.append(f"  <text x='{lg_x+16}' y='{lg_y+10}'>Mean Recovery Time</text>")
    lg_y += 18
    parts.append(f"  <rect x='{lg_x}' y='{lg_y}' width='12' height='12' fill='orange' />")
    parts.append(f"  <text x='{lg_x+16}' y='{lg_y+10}'>Resync Count</text>")

    parts.append(f"  <text x='{axA_x+sub_w/2}' y='{top+sub_h+35}' text-anchor='middle'>Control Scheme</text>")
    parts.append(f"  <text x='{axA_x+15}' y='{top+sub_h/2}' transform='rotate(-90 {axA_x+15} {top+sub_h/2})'>Time [s]</text>")
    parts.append(f"  <text x='{axA_x+sub_w+20}' y='{top+sub_h/2}' transform='rotate(-90 {axA_x+sub_w+20} {top+sub_h/2})' fill='orange'>Count</text>")

    parts.append(f"  <line x1='{axB_x}' y1='{top+sub_h}' x2='{axB_x+sub_w}' y2='{top+sub_h}' stroke='black' />")
    parts.append(f"  <line x1='{axB_x}' y1='{top}' x2='{axB_x}' y2='{top+sub_h}' stroke='black' />")

    y_safe = y_line(LAM_SAFE)
    parts.append(f"  <line x1='{axB_x}' y1='{y_safe}' x2='{axB_x+sub_w}' y2='{y_safe}' stroke='black' stroke-dasharray='4 4' />")

    path_fixed = [f"{x_line(axB_x, _DEF_TIMES[0])},{y_line(LAM_FIXED[0])}"]
    path_adapt = [f"{x_line(axB_x, _DEF_TIMES[0])},{y_line(LAM_ADAPT[0])}"]
    for i in range(1, len(_DEF_TIMES)):
        path_fixed.append(f"{x_line(axB_x, _DEF_TIMES[i])},{y_line(LAM_FIXED[i])}")
        path_adapt.append(f"{x_line(axB_x, _DEF_TIMES[i])},{y_line(LAM_ADAPT[i])}")
    parts.append(f"  <polyline points='{' '.join(path_fixed)}' fill='none' stroke='blue' />")
    parts.append(f"  <polyline points='{' '.join(path_adapt)}' fill='none' stroke='green' stroke-dasharray='3 3' />")

    lg_x = axB_x + sub_w - 70
    lg_y = top + 10
    parts.append(f"  <polyline points='{lg_x},{lg_y} {lg_x+20},{lg_y}' stroke='blue' fill='none' />")
    parts.append(f"  <text x='{lg_x+25}' y='{lg_y+4}'>Fixed Resync</text>")
    lg_y += 15
    parts.append(f"  <polyline points='{lg_x},{lg_y} {lg_x+20},{lg_y}' stroke='green' stroke-dasharray='3 3' fill='none' />")
    parts.append(f"  <text x='{lg_x+25}' y='{lg_y+4}'>Adaptive Resync</text>")

    parts.append(f"  <text x='{axB_x+sub_w/2}' y='{top+sub_h+35}' text-anchor='middle'>Time [s]</text>")
    parts.append(f"  <text x='{axB_x-30}' y='{top+sub_h/2}' transform='rotate(-90 {axB_x-30} {top+sub_h/2})'>λ(t)</text>")

    parts.append(f"  <text x='{width/2}' y='20' text-anchor='middle'>図D-2 – Resync制御方式の比較（固定 vs Adaptive）</text>")
    parts.append("</svg>")

    Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as fh:
        fh.write("\n".join(parts))

def plot_resync_compare(out_path: str = "figs/figD-2.svg") -> None:
    if plt is not None:
        _plot_mpl(out_path)
    else:
        _plot_svg(out_path)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Plot comparison of Resync control methods")
    p.add_argument("--out", default="figs/figD-2.svg", help="output figure path")
    args = p.parse_args()
    plot_resync_compare(args.out)
