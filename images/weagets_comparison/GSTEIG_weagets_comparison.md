# GSTEIG: WeaGETS combinations vs observations

Bias = mean over realizations relative to observed; MAE over the 12 months. KS: truncated 2-sample test on precipitation above the observed 95% quantile, one test per 30-year realization. Sorted by mean rank (1 = closest to observed).

| Combination | Annual P bias [%] | Wet days/month MAE [d] | Wet-day intensity bias [%] | Dry spell bias [%] | Wet spell bias [%] | Longest dry spell bias [%] | Annual max P bias [%] | KS extremes p<0.05 [n] | KS extremes median p | T mean MAE [degC] | T std MAE [degC] | n realizations | Mean rank |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Order 2 + Gamma | -0.282 | 0.187 | -0.014 | 0.294 | -0.05 | -12.909 | -0.861 | 0 | 0.496 | 0.257 | 0.199 | 50 | 4.1 |
| Order 2 + Skewed normal | 0.459 | 0.187 | 0.721 | 0.294 | -0.05 | -12.909 | 0.401 | 1 | 0.475 | 0.251 | 0.187 | 50 | 5.2 |
| Order 1 + Skewed normal | 0.61 | 0.128 | 0.8 | -0.025 | -0.212 | -27.939 | 1.311 | 0 | 0.516 | 0.262 | 0.176 | 50 | 5.5 |
| Order 3 + Gamma | -0.443 | 0.248 | 0.017 | 0.634 | -0.124 | -9.515 | -1.313 | 0 | 0.521 | 0.28 | 0.192 | 50 | 5.6 |
| Order 3 + Skewed normal | 0.284 | 0.248 | 0.739 | 0.634 | -0.124 | -9.515 | 1.306 | 0 | 0.406 | 0.272 | 0.174 | 50 | 5.7 |
| Order 1 + Mixed exponential | -0.01 | 0.178 | 0.136 | -0.146 | -0.223 | -27.697 | -4.717 | 0 | 0.499 | 0.259 | 0.191 | 50 | 5.7 |
| Order 1 + Gamma | -0.167 | 0.128 | 0.027 | -0.025 | -0.212 | -27.939 | -1.579 | 1 | 0.507 | 0.275 | 0.205 | 50 | 5.9 |
| Order 2 + Mixed exponential | -0.245 | 0.231 | -0.001 | -0.001 | -0.315 | -19.394 | -4.855 | 2 | 0.44 | 0.275 | 0.178 | 50 | 6.5 |
| Order 3 + Mixed exponential | -0.283 | 0.287 | -0.023 | 0.153 | -0.17 | -14.061 | -4.54 | 1 | 0.423 | 0.253 | 0.178 | 50 | 6.5 |
| Order 2 + Exponential | -0.288 | 0.187 | -0.022 | 0.294 | -0.05 | -12.909 | -16.33 | 42 | 0.011 | 0.257 | 0.199 | 50 | 6.8 |
| Order 1 + Exponential | -0.174 | 0.128 | 0.02 | -0.025 | -0.212 | -27.939 | -16.812 | 38 | 0.011 | 0.275 | 0.205 | 50 | 7.3 |
| Order 3 + Exponential | -0.456 | 0.248 | 0.003 | 0.634 | -0.124 | -9.515 | -16.661 | 42 | 0.006 | 0.28 | 0.192 | 50 | 8 |
