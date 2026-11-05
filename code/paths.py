"""Project paths, resolved from this file so they work from any working directory."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEAGETS_DIR = ROOT / "WeaGETS" / "Ex3-WeaGETS"  # WeaGETS code and observed input (*_WEAGETS_IN.mat)
DATA_DIR = ROOT / "data"  # generated data, not tracked by git (*_OUT.mat, future climate CSVs)
IMAGES_DIR = ROOT / "images"  # plots, tracked by git

DATA_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)


def weagets_input(station: str) -> Path:
    """Observed climate for a station, e.g. weagets_input("LATTERBACH")."""
    return WEAGETS_DIR / f"{station}_WEAGETS_IN.mat"


def weagets_output(station: str) -> Path:
    """WeaGETS simulation written by run_weagets_batch.m."""
    return DATA_DIR / f"{station}_OUT.mat"


def future_climate_dir(station: str) -> Path:
    """Folder of the delta-change future climate CSVs for a station."""
    return DATA_DIR / f"Future{station.capitalize()}"
