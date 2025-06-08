import csv
import os
from pathlib import Path

plt = None
try:
    import matplotlib.pyplot as mpl
    plt = mpl
    plt.rcParams.update({"font.family": "sans-serif"})
except Exception:
    pass


LAM_MIN = 0.70
LAM_MAX = 0.95
S_MIN = -1.02
S_MAX = -0.53


def load_data(csv_path: str):
    t = []
    lam = []
    s = []
    trig = []
    with open(csv_path, newline="") as fh:
        reader = csv.DictReader(fh)
        for idx, row in enumerate(reader):
            t.append(idx)
            lam.append(float(row["lambda"]))
            s.append(float(row["S"]))
            trig.append(int(row["ResyncTrigger"]))
    return t, lam, s, trig


def _plot_svg(t, lam, s, trig, out_path):
    width, height = 640, 400
    left, right, top, bottom = 60, 60, 20, 50
    xscale = (width - left - right) / (max(t) - min(t))
    def x(i):
        return left + (i - min(t)) * xscale
    yscale_l = (height - top - bottom) / (LAM_MAX - LAM_MIN)
    def y_l(v):
        return height - bottom - (v - LAM_MIN) * yscale_l
    yscale_s = (height - top - bottom) / (S_MAX - S_MIN)
    def y_s(v):
        return height - bottom - (v - S_MIN) * yscale_s

    path_l = [f"{x(t[0]):.1f},{y_l(lam[0]):.1f}"]
    for i in range(1, len(t)):
        path_l.append(f"{x(t[i]):.1f},{y_l(lam[i]):.1f}")
    path_s = [f"{x(t[0]):.1f},{y_s(s[0]):.1f}"]
    for i in range(1, len(t)):
        path_s.append(f"{x(t[i]):.1f},{y_s(s[i]):.1f}")

    safe_y = y_l(0.75)
    Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as fh:
        fh.write(f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>\n")
        fh.write("  <style>text { font-family: sans-serif; font-size: 12px; }</style>\n")
        # axes
        fh.write(f"  <line x1='{left}' y1='{height-bottom}' x2='{width-right}' y2='{height-bottom}' stroke='black' />\n")
        fh.write(f"  <line x1='{left}' y1='{top}' x2='{left}' y2='{height-bottom}' stroke='black' />\n")
        fh.write(f"  <line x1='{width-right}' y1='{top}' x2='{width-right}' y2='{height-bottom}' stroke='green' />\n")
        # lambda line
        fh.write(f"  <polyline points='{' '.join(path_l)}' fill='none' stroke='blue' />\n")
        # safe line
        fh.write(f"  <line x1='{left}' y1='{safe_y:.1f}' x2='{width-right}' y2='{safe_y:.1f}' stroke='black' stroke-dasharray='4 4' />\n")
        # S line
        fh.write(f"  <polyline points='{' '.join(path_s)}' fill='none' stroke='green' stroke-dasharray='2 2' />\n")
        # triggers
        for i, flag in enumerate(trig):
            if flag == 1:
                tx = x(t[i])
                ty = y_l(lam[i])
                fh.write(f"  <circle cx='{tx:.1f}' cy='{ty:.1f}' r='3' fill='red' />\n")
        # legend (top-right)
        lg_x = width - right + 5
        lg_y = top + 5
        fh.write(f"  <polyline points='{lg_x},{lg_y} {lg_x+20},{lg_y}' stroke='blue' fill='none' />\n")
        fh.write(f"  <text x='{lg_x+25}' y='{lg_y+4}'>λ(t)</text>\n")
        lg_y += 15
        fh.write(f"  <polyline points='{lg_x},{lg_y} {lg_x+20},{lg_y}' stroke='green' stroke-dasharray='2 2' fill='none' />\n")
        fh.write(f"  <text x='{lg_x+25}' y='{lg_y+4}'>S(t)</text>\n")
        lg_y += 15
        fh.write(f"  <line x1='{lg_x}' y1='{lg_y}' x2='{lg_x+20}' y2='{lg_y}' stroke='black' stroke-dasharray='4 4' />\n")
        fh.write(f"  <text x='{lg_x+25}' y='{lg_y+4}'>λ_safe</text>\n")
        lg_y += 15
        fh.write(f"  <circle cx='{lg_x+10}' cy='{lg_y}' r='3' fill='red' />\n")
        fh.write(f"  <text x='{lg_x+25}' y='{lg_y+4}'>Resync</text>\n")
        # labels
        fh.write(f"  <text x='{(left + width - right)/2}' y='{height-10}' text-anchor='middle'>Time [s]</text>\n")
        fh.write(f"  <text x='{15}' y='{(top + height - bottom)/2}' transform='rotate(-90 15 {(top + height - bottom)/2})'>λ(t)</text>\n")
        fh.write(f"  <text x='{width-15}' y='{(top + height - bottom)/2}' transform='rotate(-90 {width-15} {(top + height - bottom)/2})' fill='green'>S(t)</text>\n")
        # caption
        fh.write(f"  <text x='{width/2}' y='{height}' text-anchor='middle'>Resyncによりλが回復する様子を示す</text>\n")
        fh.write("</svg>\n")


def plot_resync(csv_path: str, out_path: str = "figs/figD-1.svg") -> None:
    t, lam, s, trig = load_data(csv_path)
    if plt is not None:
        fig, ax1 = plt.subplots()
        ax1.plot(t, lam, color="blue", label=r"$\\lambda(t)$")
        ax1.axhline(0.75, color="black", linestyle="--", label=r"$\\lambda_{safe}$")
        trig_times = [t[i] for i, val in enumerate(trig) if val == 1]
        trig_vals = [lam[i] for i, val in enumerate(trig) if val == 1]
        if trig_times:
            ax1.scatter(trig_times, trig_vals, color="red", label="Resync Trigger")
        ax1.set_xlabel("Time [s]")
        ax1.set_ylabel(r"$\\lambda(t)$")
        ax1.set_xlim(0, 100)
        ax1.set_ylim(LAM_MIN, LAM_MAX)
        ax2 = ax1.twinx()
        ax2.plot(t, s, color="green", linestyle=":", label="S(t)")
        ax2.set_ylabel("S(t)", color="green")
        ax2.tick_params(axis="y", labelcolor="green")
        lines = ax1.get_lines() + ax2.get_lines()
        labels = [line.get_label() for line in lines]
        fig.legend(lines, labels, loc="upper right")
        plt.figtext(0.5, -0.05, "Resyncによりλが回復する様子を示す", ha="center")
        Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
        fig.tight_layout()
        fig.savefig(out_path)
        plt.close(fig)
    else:
        _plot_svg(t, lam, s, trig, out_path)


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Plot λ(t) resync timeline")
    p.add_argument("csv", help="resync_wave.csv path")
    p.add_argument("--out", default="figs/figD-1.svg", help="output figure path")
    args = p.parse_args()
    plot_resync(args.csv, args.out)
