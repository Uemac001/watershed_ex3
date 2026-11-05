"""Run the code cells of a notebook as a plain Python script (no Jupyter needed).

Intended for long runs in the background. The notebook itself is not modified.
Figures are saved as PNG to images/<notebook>/cellNN_figM.png (tracked by git) instead
of being shown, and printed output goes to the console (redirect it to a log file).

Usage (from the climate-impacts folder):
    python code/run_notebook_bg.py code/tutorial.ipynb > run.log 2>&1
"""

import argparse
import ast
import json
import os
import sys
import time
import traceback
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no windows: figures are saved to files
import matplotlib.pyplot as plt


def run_cell(source: str, namespace: dict) -> None:
    """Execute a cell; print the value of a trailing expression like Jupyter does."""
    tree = ast.parse(source)
    last_expr = None
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        last_expr = ast.Expression(tree.body.pop().value)
    exec(compile(tree, "<cell>", "exec"), namespace)
    if last_expr is not None:
        value = eval(compile(last_expr, "<cell>", "eval"), namespace)
        if value is not None:
            print(value)


def save_figures(out_dir: Path, cell_index: int) -> None:
    for n, num in enumerate(plt.get_fignums(), start=1):
        plt.figure(num).savefig(out_dir / f"cell{cell_index:02d}_fig{n}.png", dpi=150, bbox_inches="tight")
    plt.close("all")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("notebook")
    parser.add_argument("--out", default=None, help="figure folder (default: images/<notebook>)")
    parser.add_argument("--stop-after", type=int, default=None, help="stop after this cell index (for testing)")
    args = parser.parse_args()

    nb_path = Path(args.notebook).resolve()
    out_dir = Path(args.out).resolve() if args.out else nb_path.parent.parent / "images" / nb_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    os.chdir(nb_path.parent)
    sys.path.insert(0, str(nb_path.parent))
    namespace = {"__name__": "__main__"}
    t_start = time.time()

    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] != "code":
            continue
        if args.stop_after is not None and i > args.stop_after:
            break
        source = "\n".join(
            line for line in "".join(c["source"]).splitlines() if not line.lstrip().startswith(("%", "!"))
        )
        if not source.strip():
            continue
        print(f"\n===== cell {i} ({(time.time() - t_start) / 60:.1f} min) =====", flush=True)
        try:
            run_cell(source, namespace)
        except Exception:
            traceback.print_exc()
            print(f"cell {i} failed: stopping here", flush=True)
            save_figures(out_dir, i)
            sys.exit(1)
        save_figures(out_dir, i)

    print(f"\nfinished in {(time.time() - t_start) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
