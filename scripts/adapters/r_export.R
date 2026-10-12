# Explicit export contract for EXISTING coefficient/event-study results in R.
# Do not recompute a model or manufacture a confidence interval in the visualization step.
# E.g. use broom::tidy(fit, conf.int=TRUE) only IF its SE and CI assumptions match
# your actual method; for custom clustered CIs supply your own already computed table.
ssv_export_coefficients <- function(result_table, path, model_label = 'Model 1') {
  stopifnot(all(c('term','estimate','ci_low','ci_high') %in% names(result_table)))
  out <- result_table[, c('term','estimate','ci_low','ci_high')]
  out$model <- model_label
  out <- out[,c('term','model','estimate','ci_low','ci_high')]
  write.csv(out, file=path, row.names=FALSE, na='')
  invisible(path)
}
ssv_export_event_study <- function(result_table, path) {
  stopifnot(all(c('event_time','estimate','ci_low','ci_high') %in% names(result_table)))
  out <- result_table[, c('event_time','estimate','ci_low','ci_high')]
  write.csv(out, file=path, row.names=FALSE, na='')
  invisible(path)
}
