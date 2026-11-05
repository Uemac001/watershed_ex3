# climate-impacts

Rainfall-runoff modelling of future climate (Watershed Modelling, Exercise 3).

## Setup (Windows)

The virtual environment lives outside polybox so that it is not synced. It is the one
shared with Exercise 2; the Jupyter kernel is called `watmod`.

```bash
python -m venv ~/.venvs/watmod
~/.venvs/watmod/Scripts/python -m pip install -r requirements-windows.txt
~/.venvs/watmod/Scripts/python -m ipykernel install --user --name watmod
```

MATLAB needs the Statistics and Machine Learning Toolbox.

## Run

All commands are run from this folder.

1. Generate the weather series (writes `data/<STATION>_OUT.mat`). Stations: `GSTEIG`, `HONDRICH`, `LATTERBACH`.

   ```bash
   matlab -batch "addpath('WeaGETS/Ex3-WeaGETS'); run_weagets_batch('LATTERBACH','Seed',1)"
   ```

   See `help run_weagets_batch` for the Markov order, distribution and number of years.
   The original dialog version is `RUN_WeaGETS.m`.

2. Open `code/tutorial.ipynb` with the `watmod` kernel, or run it without Jupyter and save
   every figure to `images/tutorial/`:

   ```bash
   ~/.venvs/watmod/Scripts/python code/run_notebook_bg.py code/tutorial.ipynb
   ```

## Layout

- `code/BucketModel/bucket_model.py`: bucket model from Exercise 2 (corrected rain/snow
  partition, PET output, optional glacier ice melt via `is_glacier` and `k_ice`).
- `code/paths.py`: all project paths.
- `images/`: plots, tracked by git.
- `data/`: generated data, not tracked by git.
- `WeaGETS/Ex3-WeaGETS/*_WEAGETS_IN.mat`: observed input, not tracked by git. After a fresh
  clone, copy these files from the course material into that folder.
