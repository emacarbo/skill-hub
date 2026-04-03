---
name: statsmodels
description: "Python library for statistical modeling, inference, and diagnostics."
---

# Statsmodels

Python's premier library for statistical modeling -- estimation, inference, and diagnostics across regression, GLM, discrete choice, and time series methods. Use for rigorous statistical analysis where coefficient interpretation and hypothesis testing matter (not just prediction).

## Key Patterns

- **Always add constant**: `X = sm.add_constant(X_data)` -- statsmodels does not include intercept by default
- **Formula API**: `smf.ols('y ~ x1 + C(category) + x1:x2', data=df).fit()` for R-style model specification
- **Model selection by outcome type**: continuous -> OLS, binary -> Logit, count -> Poisson/NegBin, time series -> ARIMA
- **Check assumptions**: residual plots, Breusch-Pagan for heteroskedasticity, Durbin-Watson for autocorrelation, Jarque-Bera for normality
- **Robust standard errors**: `results.get_robustcov_results('HC3')` when heteroskedasticity is present
- **Model comparison**: AIC/BIC for non-nested models, likelihood ratio test for nested models
- **Time series workflow**: stationarity test (ADF) -> ACF/PACF -> fit ARIMA -> residual diagnostics -> forecast
- **Overdispersion check**: If Poisson `pearson_chi2 / df_resid > 1.5`, switch to Negative Binomial
- **Marginal effects**: `results.get_margeff()` for interpretable effect sizes in logit/probit models
- **Always validate**: out-of-sample prediction or cross-validation, not just in-sample R-squared

## Quick Reference

### Model Selection by Outcome Type

| Outcome | Model | Key Output |
|:--------|:------|:-----------|
| Continuous | `sm.OLS` | Coefficients, R-squared, F-test |
| Binary | `sm.Logit` / `sm.Probit` | Odds ratios, marginal effects |
| Count | `sm.GLM(family=Poisson())` | Rate ratios, overdispersion check |
| Overdispersed count | `NegativeBinomial` | Rate ratios |
| Time series | `ARIMA` / `SARIMAX` | Forecast with confidence intervals |
| Weighted | `sm.WLS` | Coefficients with weighted errors |
| Quantile | `sm.QuantReg` | Conditional quantiles |

### Core Code Patterns

```python
import statsmodels.api as sm
import statsmodels.formula.api as smf
import numpy as np

# OLS regression
X = sm.add_constant(X_data)
results = sm.OLS(y, X).fit()
print(results.summary())
print(f"R-squared: {results.rsquared:.4f}")
print(f"Coefficients:\n{results.params}")
print(f"P-values:\n{results.pvalues}")

# Formula API (automatic dummy coding, interactions)
results = smf.ols('y ~ x1 + x2 + C(group)', data=df).fit()
results = smf.ols('y ~ x1 * x2', data=df).fit()           # with interaction
results = smf.ols('y ~ x + I(x**2)', data=df).fit()        # polynomial

# Logistic regression
results = sm.Logit(y_binary, X).fit()
odds_ratios = np.exp(results.params)
marginal = results.get_margeff()

# Time series
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
adf_pvalue = adfuller(series)[1]  # <0.05 means stationary
results = ARIMA(series, order=(1,1,1)).fit()
forecast = results.get_forecast(steps=10).summary_frame()

# GLM (Poisson for counts)
results = sm.GLM(y_counts, X, family=sm.families.Poisson()).fit()
overdispersion = results.pearson_chi2 / results.df_resid  # >1.5 -> use NegBin

# Robust standard errors
robust_results = results.get_robustcov_results('HC3')

# Diagnostics
from statsmodels.stats.diagnostic import het_breuschpagan
bp_pvalue = het_breuschpagan(results.resid, X)[1]

# Model comparison
print(f"AIC: {results.aic:.2f}, BIC: {results.bic:.2f}")
```

### Common Pitfalls

- Forgetting `sm.add_constant()` -- coefficients will be wrong
- Using OLS for binary/count outcomes -- use Logit or Poisson instead
- Ignoring convergence warnings -- check optimization output
- Using Poisson with overdispersed data -- check dispersion ratio
- Comparing non-nested models with likelihood ratio test -- use AIC/BIC instead
- Not differencing non-stationary time series before fitting ARIMA

## When to Use

- Fitting regression models where you need p-values, confidence intervals, and hypothesis tests
- Analyzing count data, binary outcomes, or ordinal responses with proper link functions
- Time series forecasting with ARIMA/SARIMAX and formal stationarity testing
- Running diagnostic tests (heteroskedasticity, autocorrelation, normality, influence)
- Producing publication-ready statistical tables and inference summaries

## Resources

- [Statsmodels Documentation](https://www.statsmodels.org/stable/)
- [User Guide](https://www.statsmodels.org/stable/user-guide.html)
