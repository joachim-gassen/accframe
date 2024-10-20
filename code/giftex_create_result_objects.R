# --- Giftex: Tables ---------------------------------------------------------- 

giftex_tab_desc_dyad_period <- function(
  dta = grounds,
  vars = c(
    "wage", "effort", "payoff_employer", "payoff_employee", "payoff_total"
  ),
  var_labels = c(
    "Wage Paid", "Effort Returned", "Payoff Firm", "Payoff Manager", 
    "Combined Payoff"
  ),
  var_tests = rep("t", length(vars))
) {
  desc_table(dta, vars, var_labels, var_tests)
}

giftex_tab_desc_participant <- function(
    dta = gpart,
    vars = c(
      "cc_pre_passed", "cc_post1_passed" 
    ),
    var_labels = c(
      "Passed Calculation Checks", "Recalls Role of Multiplier"
    ),
    var_tests = rep("chisq", length(vars))
) {
  desc_table(dta, vars, var_labels, var_tests)
}

giftex_tab_desc_dyad <- function(
  dta = gdyads,
  vars = c("mn_payoff_firm", "mn_payoff_manager", "mn_payoff_combined"),
  var_labels = c(
    "Average Payoff Firm", "Average Payoff Manager", "Average Combined Payoff"
  ),
  var_tests = rep("t", length(vars))
) {
  desc_table(dta, vars, var_labels, var_tests)
}

giftex_tab_regression_results_effort <- function(dta = grounds) {
  mod_fe <- feols(
    effort ~ experiment | round, 
    cluster = c("round", "session_code^group_id"), 
    data = dta
  )
  mod_by_rounds <- feols(
    effort ~ experiment*round, 
    cluster = c("round", "session_code^group_id"), 
    data = dta
  )
  reg_table(list(mod_fe, mod_by_rounds))
}

giftex_tab_regression_results_wage <- function(dta = grounds) {
  mod_fe <- feols(
    wage ~ experiment | round, 
    cluster = c("round", "session_code^group_id"), data = grounds
  )
  mod_by_rounds <- feols(
    wage ~ experiment*round, 
    cluster = c("round", "session_code^group_id"), data = grounds
  )
  reg_table(list(mod_fe, mod_by_rounds))
}

giftex_tab_regression_results_wage_effort <- function(dta = grounds) {
  mod_fe <- feols(
    effort ~ wage*experiment | round, 
    cluster = c("round", "session_code^group_id"), 
    data = dta
  )
  
  coef_map <- c(
    "Intercept", CONDITIONS[2], "Wage",
    glue("Wage \u00d7 {CONDITIONS[2]}")
  )
  names(coef_map) <- c(
    "(Intercept)", 
    glue("experiment{CONDITIONS[2]}"), "wage",
    glue("wage:experiment{CONDITIONS[2]}")
  )
  
  modelsummary(
    output = "gt",
    mod_fe,
    statistic = "{std.error} ({p.value})",
    shape = term ~ model + statistic,
    gof_map = list(
      list(raw = "adj.r.squared", clean = "Adjusted R²", fmt = 3),
      list(
        raw = "nobs", clean = "Number of observations", 
        fmt = function(x) format(x, big.mark=",")
      )
    ),
    coef_map = coef_map
  )
}

giftex_tab_regression_results_payoff <- function(dta = gpart) {
  mod_payoff_part <- feols(
    payoff ~ experiment*role, data = gpart, 
    cluster = c( "session_code^group_id")
  )

  coef_map <- c(
    "Intercept", "Firm",CONDITIONS[2], 
    glue("Firm \u00d7 {CONDITIONS[2]}")
  )
  names(coef_map) <- c(
    "(Intercept)", "roleEmployer", 
    glue("experiment{CONDITIONS[2]}"), 
    glue("experiment{CONDITIONS[2]}:roleEmployer")
  )
  
  modelsummary(
    output = "gt",
    mod_payoff_part,
    statistic = "{std.error} ({p.value})",
    shape = term ~ model + statistic,
    gof_map = list(
      list(raw = "adj.r.squared", clean = "Adjusted R²", fmt = 3),
      list(
        raw = "nobs", clean = "Number of observations", 
        fmt = function(x) format(x, big.mark=",")
      )
    ),
    coef_map = coef_map
  )
}

giftex_tab_reasons_wage <- function(
    dta = greasons,
    vars = c(
      "wage_mentions_payoff", "wage_mentions_other",
      "reason_wage_self_payoff", "reason_wage_other_payoff", 
      "reason_wage_fairness", "reason_wage_recip"
    ),
    var_labels = c(
      "Mentions Payoff", "Mentions Other",
      "Cares About Own Payoff", "Cares About Other Payoff", 
      "Cares About Fairness", "Cares About Reciprocity"
    ),
    var_tests = c("chisq", "chisq", "t", "t", "t", "t", "t")
) {
  # not sure whether this works
  if (is.null(dta)) stop(
    "Reasons have not been classified for this experimental run yet."
  )
  desc_table(dta, vars, var_labels, var_tests)
}

giftex_tab_reasons_effort <- function(
    dta = greasons,
    vars = c(
      "effort_mentions_payoff", "effort_mentions_other",
      "reason_effort_self_payoff", "reason_effort_other_payoff", 
      "reason_effort_fairness", "reason_effort_recip"
    ),
    var_labels = c(
      "Mentions Payoff", "Mentions Other",
      "Cares About Own Payoff", "Cares About Other Payoff", 
      "Cares About Fairness", "Cares About Reciprocity"
    ),
    var_tests = c("chisq", "chisq", "t", "t", "t", "t", "t")
) {
  # not sure whether this works
  if (is.null(dta)) stop(
    "Reasons have not been classified for this experimental run yet."
  )
  desc_table(dta, vars, var_labels, var_tests)
}


# --- Giftex: Figures -----------------------------------------------------------

giftex_fig_wage_by_period <- function(dta = grounds) {
  names(color_scale) <- unique(levels(dta$experiment))
  color_scale_labs <- CONDITIONS
  df <- dta %>%
    group_by(round, experiment) %>%
    summarise(
      mn_wage = mean(wage),
      lb = mn_wage - 1.96*sd(wage)/sqrt(n()),
      ub = mn_wage + 1.96*sd(wage)/sqrt(n())
    )
  
  ggplot(df, aes(x = round, y = mn_wage, color = experiment)) +
    geom_point(position = position_dodge(width = 0.5)) +
    geom_errorbar(
      aes(ymin = lb, ymax = ub), width = 0,
      position = position_dodge(width = 0.5)
    ) +
    labs(
      x = "Period",
      y = "Wage",
      color = "Treatment"
    ) +
    scale_x_continuous(breaks = 1:10) +
    theme_classic(base_size = 16) + 
    scale_color_manual("", values = color_scale, labels = color_scale_labs) +
    theme(plot.title.position =  "plot", legend.position = "bottom")
}

giftex_fig_effort_by_period <- function(dta = grounds) {
  names(color_scale) <- unique(levels(dta$experiment))
  color_scale_labs <- CONDITIONS
  df <- dta %>%
    group_by(round, experiment) %>%
    summarise(
      mn_effort = mean(effort),
      lb = mn_effort - 1.96*sd(effort)/sqrt(n()),
      ub = mn_effort + 1.96*sd(effort)/sqrt(n())
    )
  
  ggplot(df, aes(x = round, y = mn_effort, color = experiment)) +
    geom_point(position = position_dodge(width = 0.5)) +
    geom_errorbar(
      aes(ymin = lb, ymax = ub), width = 0,
      position = position_dodge(width = 0.5)
    ) +
    labs(
      x = "Period",
      y = "Effort",
      color = "Treatment"
    ) +
    scale_x_continuous(breaks = 1:10) +
    theme_classic(base_size = 16) + 
    scale_color_manual("", values = color_scale, labels = color_scale_labs) +
    theme(plot.title.position =  "plot", legend.position = "bottom")
}

giftex_fig_wage_effort <- function(dta = grounds) {
  names(color_scale) <- unique(levels(dta$experiment))
  color_scale_labs <- CONDITIONS
  ggplot(
    dta, 
    aes(x = wage, y = effort, color = experiment, group = experiment)
  ) + geom_jitter(size = 0.25) + 
    geom_smooth(method = "lm") + 
    scale_color_manual("", values = color_scale, labels = color_scale_labs) +
    labs(color = "", x = "Wage Paid", y = "Effort Level") +
    theme_classic() + 
    theme(
      legend.position = "bottom",
      panel.grid.minor = element_blank()
    )
  
}
