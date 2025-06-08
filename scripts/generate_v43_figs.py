import os
from pathlib import Path

try:
    import matplotlib.pyplot as plt  # type: ignore
    import numpy as np  # type: ignore
    plt.rcParams.update({"font.family": "sans-serif"})
except Exception:  # pragma: no cover - if matplotlib missing
    plt = None
    np = None


def save_svg(parts, out_path):
    Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as fh:
        fh.write("\n".join(parts))


def fig3_2b(out_path="figs/fig3-2b.svg"):
    """Resync 判定・状態遷移図."""
    width, height = 640, 200
    cx = [60, 200, 340, 470, 580]
    cy = 100
    states = [
        "Normal",
        "λ_drop Detected",
        "Resync Active",
        "Cooldown",
        "Recovery",
    ]
    parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>",
        "  <style>text { font-family: sans-serif; font-size: 12px; }</style>",
        "  <defs><marker id='arrow' markerWidth='10' markerHeight='10' refX='5' refY='5' orient='auto' markerUnits='strokeWidth'><path d='M0,0 L10,5 L0,10 z' fill='black'/></marker></defs>",
    ]
    # draw states
    for i, label in enumerate(states):
        x = cx[i] - 40
        parts.append(f"  <rect x='{x}' y='{cy-20}' width='80' height='40' fill='#eef' stroke='black' />")
        parts.append(f"  <text x='{cx[i]}' y='{cy+5}' text-anchor='middle'>{label}</text>")
    # arrows
    def arrow(i, j, text):
        parts.append(f"  <path d='M{cx[i]+40},{cy} L{cx[j]-40},{cy}' stroke='black' fill='none' marker-end='url(#arrow)' />")
        mid = (cx[i]+cx[j]) / 2
        parts.append(f"  <text x='{mid}' y='{cy-10}' text-anchor='middle'>{text}</text>")
    arrow(0,1,"λ_stat<0.75 & Δλ_rms>0.02 3s")
    arrow(1,2,"trigger")
    arrow(2,3,"Resync done")
    arrow(3,4,"cooldown")
    parts.append(f"  <path d='M{cx[4]+40},{cy} L{cx[0]-40},{cy}  ' stroke='black' fill='none' marker-end='url(#arrow)' />")
    parts.append(f"  <text x='{(cx[4]+cx[0])/2+30}' y='{cy-10}' text-anchor='middle'>stable 3s</text>")
    parts.append("</svg>")
    save_svg(parts, out_path)


def fig3_4(out_path="figs/fig3-4.svg"):
    """λ-Cascade(10段)+フェーズソルト構造図."""
    width, height = 800, 240
    left = 60
    top = 40
    stage_w = 50
    stage_h = 40
    gap = 20
    parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>",
        "  <style>text { font-family: sans-serif; font-size: 12px; }</style>",
    ]
    for i in range(10):
        x = left + i * (stage_w + gap)
        parts.append(f"  <rect x='{x}' y='{top}' width='{stage_w}' height='{stage_h}' fill='#eef' stroke='black' />")
        parts.append(f"  <text x='{x+stage_w/2}' y='{top+15}' text-anchor='middle'>Stage {i}</text>")
        parts.append(f"  <text x='{x+stage_w/2}' y='{top+30}' text-anchor='middle'>λ_{i}(t)</text>")
        parts.append(f"  <rect x='{x}' y='{top+stage_h+10}' width='{stage_w}' height='{stage_h}' fill='#eef' stroke='black' />")
        parts.append(f"  <text x='{x+stage_w/2}' y='{top+stage_h+25}' text-anchor='middle'>Verify</text>")
        parts.append(f"  <text x='{x+stage_w/2}' y='{top+stage_h+40}' text-anchor='middle'>ξ_{i}</text>")
    parts.append(f"  <text x='{left}' y='{height-20}'>ξ_n = ξ_base ⊕ SHA256(seed‖n)</text>")
    parts.append("</svg>")
    save_svg(parts, out_path)


def fig0_1(out_path="figs/fig0-1.svg"):
    """比較表."""
    width, height = 600, 160
    cols = [0, 150, 300, 450, 600]
    rows = [0, 30, 60, 90, 120, 150]
    headers = ["観点", "静的バイオID", "QKD", "本提案(IFG QID)"]
    data = [
        ("時間依存性", "×", "△(鍵更新のみ)", "◎(λ(t)随時更新)"),
        ("セキュリティモデル", "漏洩耐性なし", "量子鍵流通のみ", "λ-cascade＋ZKP"),
        ("実装難度", "低", "高", "中"),
        ("プライバシー配慮", "△", "◎", "◎(ZKP λ署名)"),
        ("AGI適用", "×", "×", "◎(λ-Harness)"),
    ]
    parts = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>",
             "  <style>text { font-family: sans-serif; font-size: 12px; }</style>"]
    # draw grid
    for y in rows:
        parts.append(f"  <line x1='{cols[0]}' y1='{y}' x2='{cols[-1]}' y2='{y}' stroke='black' />")
    for x in cols:
        parts.append(f"  <line x1='{x}' y1='{rows[0]}' x2='{x}' y2='{rows[-1]}' stroke='black' />")
    for i, h in enumerate(headers):
        parts.append(f"  <text x='{(cols[i]+cols[i+1])/2}' y='{20}' text-anchor='middle'>{h}</text>")
    for r, row in enumerate(data):
        y = rows[r+1]+20
        for c, val in enumerate(row):
            parts.append(f"  <text x='{(cols[c]+cols[c+1])/2}' y='{y}' text-anchor='middle'>{val}</text>")
    parts.append(f"  <rect x='{cols[3]}' y='{rows[0]}' width='{cols[4]-cols[3] if len(cols)>4 else 0}' height='{rows[-1]-rows[0]}' fill='none' stroke='red' stroke-width='2' />" if len(cols)>4 else "")
    parts.append("</svg>")
    save_svg(parts, out_path)


def figD_3(out_path="figs/figD-3.svg"):
    """λ回復 vs Resync振幅シミュレーション."""
    if plt is None or np is None:
        width, height = 640, 360
        left, right, top, bottom = 60, 40, 20, 40
        times = list(range(60))
        lam_fixed = [0.7 + 0.05 * (1 - np.exp(-t/20)) if np else 0.7 for t in times]
        lam_adapt = [0.72 + 0.05 * (1 - np.exp(-t/10)) if np else 0.72 for t in times]
        scale_x = (width-left-right)/max(times)
        scale_y = (height-top-bottom)/(1.0-0.7)
        def x(t):
            return left + t*scale_x
        def y(v):
            return height-bottom - (v-0.7)*scale_y
        parts = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>",
                 "  <style>text { font-family: sans-serif; font-size: 12px; }</style>"]
        parts.append(f"  <line x1='{left}' y1='{height-bottom}' x2='{width-right}' y2='{height-bottom}' stroke='black' />")
        parts.append(f"  <line x1='{left}' y1='{top}' x2='{left}' y2='{height-bottom}' stroke='black' />")
        safe_y = y(0.75)
        parts.append(f"  <line x1='{left}' y1='{safe_y}' x2='{width-right}' y2='{safe_y}' stroke='black' stroke-dasharray='4 4' />")
        path_f = [f"{x(times[0])},{y(lam_fixed[0])}"]
        path_a = [f"{x(times[0])},{y(lam_adapt[0])}"]
        for i in range(1,len(times)):
            path_f.append(f"{x(times[i])},{y(lam_fixed[i])}")
            path_a.append(f"{x(times[i])},{y(lam_adapt[i])}")
        parts.append(f"  <polyline points='{' '.join(path_f)}' fill='none' stroke='blue' />")
        parts.append(f"  <polyline points='{' '.join(path_a)}' fill='none' stroke='green' stroke-dasharray='3 3' />")
        lg_x = width-right+5
        lg_y = top+5
        parts.append(f"  <polyline points='{lg_x},{lg_y} {lg_x+20},{lg_y}' stroke='blue' fill='none' />")
        parts.append(f"  <text x='{lg_x+25}' y='{lg_y+4}'>Fixed Resync</text>")
        lg_y += 15
        parts.append(f"  <polyline points='{lg_x},{lg_y} {lg_x+20},{lg_y}' stroke='green' stroke-dasharray='3 3' fill='none' />")
        parts.append(f"  <text x='{lg_x+25}' y='{lg_y+4}'>Adaptive Resync</text>")
        parts.append(f"  <text x='{(left+width-right)/2}' y='{height-10}' text-anchor='middle'>Time [s]</text>")
        parts.append(f"  <text x='{left-30}' y='{(top+height-bottom)/2}' transform='rotate(-90 {left-30} {(top+height-bottom)/2})'>λ(t)</text>")
        parts.append("</svg>")
        save_svg(parts, out_path)
    else:
        t = np.linspace(0, 60, 60)
        lam_fixed = 0.7 + 0.05 * (1 - np.exp(-t/20))
        lam_adapt = 0.72 + 0.05 * (1 - np.exp(-t/10))
        plt.figure()
        plt.plot(t, lam_fixed, label="Fixed Resync")
        plt.plot(t, lam_adapt, label="Adaptive Resync", linestyle="--")
        plt.axhline(0.75, color="black", linestyle=":")
        plt.xlabel("Time [s]")
        plt.ylabel(r"$\\lambda(t)$")
        plt.legend()
        plt.tight_layout()
        Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path)
        plt.close()


def figB_2(out_path="figs/figB-2.svg"):
    """κ_AM(T) vs 温度."""
    temps = [200, 350, 500, 650, 800]
    k_vals = [0.2, 0.35, 0.55, 0.75, 0.95]
    if plt is None or np is None:
        width, height = 640, 360
        left, right, top, bottom = 60, 20, 20, 40
        scale_x = (width-left-right)/(temps[-1]-temps[0])
        scale_y = (height-top-bottom)/(max(k_vals)-min(k_vals))
        def x(t):
            return left + (t-temps[0])*scale_x
        def y(k):
            return height-bottom - (k-min(k_vals))*scale_y
        parts = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>",
                 "  <style>text { font-family: sans-serif; font-size: 12px; }</style>"]
        parts.append(f"  <line x1='{left}' y1='{height-bottom}' x2='{width-right}' y2='{height-bottom}' stroke='black' />")
        parts.append(f"  <line x1='{left}' y1='{top}' x2='{left}' y2='{height-bottom}' stroke='black' />")
        path = [f"{x(temps[0])},{y(k_vals[0])}"]
        for i in range(1,len(temps)):
            path.append(f"{x(temps[i])},{y(k_vals[i])}")
        for t,k in zip(temps,k_vals):
            parts.append(f"  <circle cx='{x(t)}' cy='{y(k)}' r='3' fill='blue' />")
        parts.append(f"  <polyline points='{' '.join(path)}' fill='none' stroke='blue' />")
        parts.append(f"  <text x='{(left+width-right)/2}' y='{height-10}' text-anchor='middle'>Temperature [K]</text>")
        parts.append(f"  <text x='{left-30}' y='{(top+height-bottom)/2}' transform='rotate(-90 {left-30} {(top+height-bottom)/2})'>κ_AM [λ/kHz]</text>")
        parts.append(f"  <text x='{width/2}' y='20' text-anchor='middle'>NVセンター + μ-cavity 実測</text>")
        parts.append("</svg>")
        save_svg(parts, out_path)
    else:
        t = np.array(temps)
        k = np.array(k_vals)
        coef = np.polyfit(t, k, 1)
        fit = np.poly1d(coef)
        xs = np.linspace(temps[0], temps[-1], 50)
        plt.figure()
        plt.plot(t, k, "o", label="data")
        plt.plot(xs, fit(xs), label=f"fit: {coef[0]:.3f}T + {coef[1]:.2f}")
        plt.xlabel("Temperature [K]")
        plt.ylabel("κ_AM [λ/kHz]")
        plt.legend()
        plt.tight_layout()
        Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path)
        plt.close()


def main():
    fig3_2b()
    fig3_4()
    fig0_1()
    figD_3()
    figB_2()


if __name__ == "__main__":
    main()
