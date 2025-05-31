"""Generate a simple error analysis flow chart using graphviz."""

from __future__ import annotations

from pathlib import Path

try:
    from graphviz import Digraph
except Exception:
    print("\u26A0\ufe0f  Graphviz unavailable (Python binding missing)")
    Digraph = None


def main(out_path: str = "docs/plot/fig7_4.png") -> None:
    if Digraph is None:
        return

    dot = Digraph("error_flow")
    dot.attr(rankdir="TB")
    dot.node("start", "Start")
    dot.node("measure", "Experimental Data")
    dot.node("fit", "Parameter Mapping")
    dot.node("compare", "Compare to Theory")
    dot.node("analyze", "Error Sources")
    dot.edges([
        ("start", "measure"),
        ("measure", "fit"),
        ("fit", "compare"),
        ("compare", "analyze"),
    ])
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    dot.format = "png"
    try:
        dot.render(out_path, cleanup=True)
        print(f"\u2705 Graph generated at {out_path}")
    except Exception as e:
        print(f"\u26A0\ufe0f  Graphviz render failed: {e}")


if __name__ == "__main__":
    main()
