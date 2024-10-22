# --- Trust: Tables ---------------------------------------------------------- 

trust_tab_desc_dyad_period <- function(
  dta = trounds,
  vars = c(
    "sent_amount", "sent_back_amount", "pct_returned",
    "payoff_inv", "payoff_man", "payoff_total"
  ),
  var_labels = c(
    "Investment", "Dividend", "% Returned",
    "Payoff Investor", "Payoff Manager", "Combined Payoff"
  ),
  var_tests = rep("t", length(vars))
) {
  desc_table(dta, vars, var_labels, var_tests)
}

trust_tab_desc_participant <- function(
    dta = tparticipants,
    vars = c(
      "cc_passed", "mc_passed" 
    ),
    var_labels = c(
      "Understood Role of Multiplier", "Recalls Role"
    ),
    var_tests = rep("chisq", length(vars))
) {
  desc_table(dta, vars, var_labels, var_tests)
}

trust_tab_desc_dyad <- function(
  dta = tdyads,
  vars = c("mn_payoff_inv", "mn_payoff_man", "mn_payoff_combined"),
  var_labels = c(
    "Average Payoff Investor", "Average Payoff Manager", "Average Combined Payoff"
  ),
  var_tests = rep("t", length(vars))
) {
  desc_table(dta, vars, var_labels, var_tests)
}

trust_tab_regression_results_inv <- function(dta = trounds) {
  mod_fe <- feols(
    sent_amount ~ experiment | round, 
    cluster = c("round", "session_code^group_id"), 
    data = dta
  )
  mod_by_rounds <- feols(
    sent_amount ~ experiment*round, 
    cluster = c("round", "session_code^group_id"), 
    data = dta
  )
  reg_table(list(mod_fe, mod_by_rounds))
}

trust_tab_regression_results_pct_ret <- function(dta = trounds) {
  mod_fe <- feols(
    pct_returned ~ experiment | round, 
    cluster = c("round", "session_code^group_id"), 
    data = dta
  )
  mod_by_rounds <- feols(
    pct_returned ~ experiment*round, 
    cluster = c("round", "session_code^group_id"), 
    data = dta
  )
  reg_table(list(mod_fe, mod_by_rounds))
}

trust_tab_regression_results_payoff <- function(dta = tparticpants) {
  mod_payoff <- feols(
    payoff ~ experiment*role, 
    cluster = c( "session_code^group_id"),
    data = tparticipants
  )

  coef_map <- c(
    "Intercept", "Investor", CONDITIONS[2], 
    glue("Investor \u00d7 {CONDITIONS[2]}")
  )
  names(coef_map) <- c(
    "(Intercept)", "roleSender", 
    glue("experiment{CONDITIONS[2]}"), 
    glue("experiment{CONDITIONS[2]}:roleSender")
  )
  
  modelsummary(
    output = "gt",
    mod_payoff,
    statistic = "{std.error} ({p.value})",
    shape = term ~ model + statistic,  
    gof_map = list(
      list(raw = "adj.r.squared", clean = "Adjusted R2", fmt = 3),
      list(
        raw = "nobs", clean = "Number of observations", 
        fmt = function(x) format(x, big.mark=",")
      )
    ),
    coef_map = coef_map
  )
}

trust_tab_reasons_sent <- function(
    dta = treasons,
    vars = c(
      "sent_mentions_payoff", "sent_mentions_other",
      "reason_sent_self_payoff", "reason_sent_other_payoff", 
      "reason_sent_fairness", "reason_sent_trust"
    ),
    var_labels = c(
      "Mentions Payoff", "Mentions Other",
      "Cares About Own Payoff", "Cares About Other Payoff", 
      "Cares About Fairness", "Cares About Trust"
    ),
    var_tests = c("chisq", "chisq", "t", "t", "t", "t", "t")
) {
  # not sure whether this works
  if (is.null(dta)) stop(
    "Reasons have not been classified for this experimental run yet."
  )
  desc_table(dta, vars, var_labels, var_tests)
}

trust_tab_reasons_sent_back <- function(
    dta = treasons,
    vars = c(
      "back_mentions_payoff", "back_mentions_other",
      "reason_back_self_payoff", "reason_back_other_payoff", 
      "reason_back_fairness", "reason_back_trust"
    ),
    var_labels = c(
      "Mentions Payoff", "Mentions Other",
      "Cares About Own Payoff", "Cares About Other Payoff", 
      "Cares About Fairness", "Cares About Trust"
    ),
    var_tests = c("chisq", "chisq", "t", "t", "t", "t", "t")
) {
  # not sure whether this works
  if (is.null(dta)) stop(
    "Reasons have not been classified for this experimental run yet."
  )
  desc_table(dta, vars, var_labels, var_tests)
}

# --- Trust: Figures -----------------------------------------------------------

trust_fig_inv_by_period <- function(dta = trounds) {
  names(color_scale) <- unique(levels(dta$experiment))
  color_scale_labs <- CONDITIONS
  df <- dta %>%
    group_by(round, experiment) %>%
    summarise(
      mn_sent_amount = mean(sent_amount),
      lb = mn_sent_amount - 1.96*sd(sent_amount)/sqrt(n()),
      ub = mn_sent_amount + 1.96*sd(sent_amount)/sqrt(n())
    )
  
  ggplot(df, aes(x = round, y = mn_sent_amount, color = experiment)) +
    geom_point(position = position_dodge(width = 0.5)) +
    geom_errorbar(
      aes(ymin = lb, ymax = ub), width = 0,
      position = position_dodge(width = 0.5)
    ) +
    labs(
      x = "Period",
      y = "Investment",
      color = "Treatment"
    ) +
    scale_x_continuous(breaks = 1:10) +
    theme_classic(base_size = 12) + 
    scale_color_manual("", values = color_scale, labels = color_scale_labs) +
    theme(plot.title.position =  "plot", legend.position = "bottom")
}

trust_fig_div_share_by_period <- function(dta = trounds) {
  names(color_scale) <- unique(levels(dta$experiment))
  color_scale_labs <- CONDITIONS
  df <- dta %>%
    group_by(round, experiment) %>%
    summarise(
      mn_pct_returned = mean(pct_returned, na.rm = TRUE),
      lb = mn_pct_returned - 1.96*sd(pct_returned, na.rm = TRUE)/sqrt(sum(!is.na(pct_returned))),
      ub = mn_pct_returned + 1.96*sd(pct_returned, na.rm = TRUE)/sqrt(sum(!is.na(pct_returned)))
    )
  
  ggplot(df, aes(x = round, y = mn_pct_returned, color = experiment)) +
    geom_point(position = position_dodge(width = 0.5)) +
    geom_errorbar(
      aes(ymin = lb, ymax = ub), width = 0,
      position = position_dodge(width = 0.5)
    ) +
    labs(
      x = "Period",
      y = "Dividend Share",
      color = "Treatment"
    ) +
    scale_x_continuous(breaks = 1:10) +
    scale_y_continuous(labels = scales::percent) +
    theme_classic(base_size = 12) + 
    scale_color_manual("", values = color_scale, labels = color_scale_labs) +
    theme(plot.title.position =  "plot", legend.position = "bottom")
}

