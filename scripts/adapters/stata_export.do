* STATA EXAMPLE / manual interface: export ALREADY COMPUTED estimates and CI bounds.
* Use your exact estimator's own SE/CI; do not silently replace clustered, bootstrap,
* or small-sample t intervals with +/-1.96*SE. Do not infer CI from stars.
*
* Example for any approved result dataset already containing:
*   term (string) model (string) estimate ci_low ci_high (numeric)
*   save and reopen your copy before exporting; adjust names explicitly.
*
* use "my_existing_coefficient_results.dta", clear
* order term model estimate ci_low ci_high
* keep term model estimate ci_low ci_high
* export delimited using "normalized_coefficients.csv", replace
*
* For event studies, your data must contain event_time (numeric, integer), estimate,
* ci_low and ci_high. Omit the reference period from the export instead of
* fabricating an estimate or CI for it.
