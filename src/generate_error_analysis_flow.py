"""Generate a simple error analysis flow chart using graphviz."""

from __future__ import annotations

from pathlib import Path
from graphviz import Digraph


def main(out_path: str = "docs/plot/fig7_4.png") -> None:
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
    dot.render(out_path, cleanup=True)


if __name__ == "__main__":
    main()
