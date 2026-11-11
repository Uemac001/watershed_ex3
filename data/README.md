# data

WeaGETS output files are named `<STATION>_O<order>_D<distribution>_OUT.mat`.

- `O`: Markov chain order (1, 2 or 3)
- `D`: precipitation distribution (1 Exponential, 2 Gamma, 3 Skewed normal, 4 Mixed exponential)

All `O*_D*` files use the same settings: 1500 years (50 realizations of 30 years), threshold 0.1 mm, seed 1.
They are made by `WeaGETS/Ex3-WeaGETS/run_weagets_all.m`.

## In git

| File | Simulation |
|---|---|
| `GSTEIG_O1_D2_OUT.mat` | Gsteig, order 1 + Gamma |
| `GSTEIG_O2_D2_OUT.mat` | Gsteig, order 2 + Gamma (the chosen setting) |

The observed input is `WeaGETS/Ex3-WeaGETS/GSTEIG_WEAGETS_IN.mat`.

## Local only (not in git)

| File | Simulation |
|---|---|
| `GSTEIG_O*_D*_OUT.mat` (other 10) | the other combinations, compared in `images/weagets_comparison` |
| `GSTEIG_OUT.mat` | same data as `GSTEIG_O1_D2_OUT.mat` |
| `LATTERBACH_OUT.mat` | Latterbach, order 1 + Gamma, seed 1 |
| `Future<Station>[_O*_D*]/` | future climate CSVs (delta change), made by the notebooks |
