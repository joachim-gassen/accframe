# Utility code needed by the code that imports experimental data and
# generates result objects - source this once in your main code
# before sourcing the other code files.

suppressMessages({
  library(tidyverse)
  library(glue)
  library(ggbeeswarm)
  library(fixest)
  library(gt)
  library(kableExtra)
  library(modelsummary)
  library(showtext)
  
  devtools::source_url(
    "https://raw.githubusercontent.com/trr266/treat/main/code/R/theme_trr.R"
  )
})

color_scale <- RColorBrewer::brewer.pal(3 ,"Set1")[c(2, 1)]

# --- Constants ----------------------------------------------------------------

EXPERIMENTS <- c("honesty", "giftex", "trust")
CONDITIONS <- c("Neutral", "Contextualized")

# --- Installing TRR fonts -----------------------------------------------------

trr266_fonts_available <- all(c("Cambria", "Calibri Light") %in% font_families())

if (!trr266_fonts_available) {
  # On Mac with MS Office installation you need to add the Office
  # Fonts to the font path. The following depends on your 
  # installation but _should_ work in most cases
  
  office_font_path <- "/Applications/Microsoft Word.app/Contents/Resources/DFonts"
  if (Sys.info()["sysname"] == "Darwin") {
    if (dir.exists(office_font_path)) font_paths(office_font_path)
    else stop("MS Office font path not found")
  }
  
  rv <- tryCatch({
    font_add(family = "Cambria", regular = "Cambria.ttc")
    font_add(family = "Calibri Light", regular = "calibril.ttf")
  }, error = function(e) {
    message(sprintf("Failed to install TRR 266 fonts: %s", e))
    invisible(font_families())        
  })
  
  trr266_fonts_available <- all(c("Cambria", "Calibri Light") %in% rv)
  if (trr266_fonts_available) message("Successfully installed TRR 266 fonts") 
}

# --- Utility functions --------------------------------------------------------

center_table <- function(x) {
  x[1] <- paste0("\\begin{center}", x[1], "\\end{center}")
  x
}
remove_column_labels <- function(x) {
  x[1] <- sub("\\\\toprule\\n.*\\\\midrule", "\\\\toprule\\\n", x[1])
  x
}

# Needs \usepackage{adjustbox} in preamble
fit_gt_table_to_slide <- function(x, scale = 1) {
  if (scale == 1) repstr <- "\\\\resizebox{\\\\columnwidth}{!}{\\\\begin{tabular}"
  else repstr <- paste0("\\\\resizebox{", scale, "\\\\columnwidth}{!}{\\\\begin{tabular}")
  x[1] <- sub("\\\\begin\\{longtable\\}", repstr, x[1])
  x[1] <- sub("\\\\end\\{longtable\\}", "\\\\end{tabular}}", x[1])
  x
}

fit_gt_table_to_slide_long <- function(x, scale = 1) {
  if (scale == 1) repstr <- "\\\\resizebox*{!}{\\\\textheight}{\\\\begin{tabular}"
  else repstr <- paste0("\\\\resizebox*{!}{", scale, "\\\\textheight}{\\\\begin{tabular}")
  x[1] <- sub("\\\\begin\\{longtable\\}", repstr, x[1])
  x[1] <- sub("\\\\end\\{longtable\\}", "\\\\end{tabular}}", x[1])
  x
}

post_process_reg_table <- function(x) {
  x[1] <- sub("\\{lcc\\}", "\\{lrrr\\}", x[1])
  x[1] <- sub("\\{lcccc\\}", "\\{lrrrrrr\\}", x[1])
  x[1] <- gsub("\\{2\\}", "\\{3\\}", x[1])
  x[1] <- sub("\\{2-3\\}", "\\{2-4\\}", x[1])
  x[1] <- sub("\\{4-5\\}", "\\{5-7\\}", x[1])
  x[1] <- gsub("Est\\.\\s*&\\s*S\\.E\\.\\s*\\(p\\s*\\)", "Est & S.E. & p-value", x[1])
  x[1] <- gsub("\\((<?[01]\\.\\d{3})\\)", "& \\1", x[1])
  x[1] <- gsub("&\\s*&", "& & &", x[1])
  x[1] <- sub("Adjusted R", "\\\\midrule\\\nAdjusted R", x[1])
  x
}

cost <- function(e) {
  case_when(
    round(e, 2) == 0.1 ~ 0,
    round(e, 2) == 0.2 ~ 1,
    round(e, 2) == 0.3 ~ 2,
    round(e, 2) == 0.4 ~ 4,
    round(e, 2) == 0.5 ~ 6,
    round(e, 2) == 0.6 ~ 8,
    round(e, 2) == 0.7 ~ 10,
    round(e, 2) == 0.8 ~ 12,
    round(e, 2) == 0.9 ~ 15,
    round(e, 2) == 1.0 ~ 28,
    TRUE ~ NA
  )
}

mypvalue <- function(x) {
  if (x < 0.001) return("p < 0.001")
  else return (sprintf("p = %.3f", x))
}

get_desc_row <- function(test, depvar, dta) {
  dv_nf <- dta %>% filter(
    experiment == CONDITIONS[1], is.finite(.data[[depvar]])
  ) %>% pull(.data[[depvar]])
  dv_bf <- dta %>% filter(
    experiment == CONDITIONS[2], is.finite(.data[[depvar]])
  ) %>% pull(.data[[depvar]])
  dv <- dta %>% pull(.data[[depvar]])
  idv <- dta$experiment
  
  if (test == "t") {
    rv <- t.test(dv ~ idv)
    stat_str = sprintf("t = %.2f", -rv$statistic)
  } else if (test == "chisq") {
    if (length(unique(dv)) > 1) {
      rv <- chisq.test(dv, idv)
      stat_str = sprintf("χ² = %.2f", rv$statistic)
    } else {
      stat_str = "—"
      rv <- list(p.value = 1)
    }
  } else stop(glue("Unknown test '{test}'"))
  c(
    format(length(dv_nf), big.marks = ","), 
    sprintf("%.3f", mean(dv_nf)), sprintf("%.3f", sd(dv_nf)),
    format(length(dv_bf), big.marks = ","), 
    sprintf("%.3f", mean(dv_bf)), sprintf("%.3f", sd(dv_bf)),
    stat_str, mypvalue(rv$p.value)
  )
}

desc_table <- function(dta, vars, var_labels, var_tests) {
  tab_mat <- matrix(NA_character_, nrow = length(vars), ncol = 8)
  for (r in seq_along(vars)) {
    tab_mat[r,] <- get_desc_row(var_tests[r], vars[r], dta)
  }
  tab <- as.data.frame(tab_mat) %>%
    mutate(V0 = var_labels) %>%
    select(V0, everything())
  
  gt(tab, rowname_col = "row_names") %>%
    cols_label(
      V0 = "", V1 = "N", V2 = "Mean", V3 = "SD", 
      V4 = "N", V5 = "Mean", V6 = "SD",
      V7 = "", V8 = ""
    ) %>%
    tab_spanner(label = CONDITIONS[1], columns = 2:4) %>%
    tab_spanner(label = CONDITIONS[2], columns = 5:7) %>%
    tab_spanner(label = "Tests for Differences", columns = 8:9) 
}

reg_table <- function(mods) {
  coef_map <- c(
    "Intercept", CONDITIONS[2], "Period",
    glue("Period \u00d7 {CONDITIONS[2]}")
  )
  names(coef_map) <- c(
    "(Intercept)", 
    glue("experiment{CONDITIONS[2]}"), "round",
    glue("experiment{CONDITIONS[2]}:round")
  )
  
  modelsummary(
    output = "gt",
    list(
      "Period Fixed Effects" = mods[[1]], 
      "Interacted by Period" = mods[[2]]
    ),
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

# --- Functions to read experiment data ----------------------------------------

honesty_read_exp_data <- function(dversion = "2024-06-17") {
  hrounds <<- read_csv(
    glue("data/generated/honesty_{dversion}_rounds.csv"), show_col_types = FALSE
  ) %>%
    mutate(
      experiment = factor(ifelse(
        experiment == "fhonesty",
        CONDITIONS[2], CONDITIONS[1]
      ), CONDITIONS),
      slack = reported_amount - true_amount,
      truthful = ifelse(
        true_amount == 6000, NA, 
        as.integer(reported_amount == true_amount)
      ),
      honesty = ifelse(
        true_amount == 6000, NA, 
        1 - (reported_amount - true_amount)/(6000 - true_amount)
      ),
      all_slack = honesty == 0
    )
  
  hparticipants <<- read_csv(
    glue("data/generated/honesty_{dversion}_participants.csv"), 
    show_col_types = FALSE
  ) %>%
    mutate(
      experiment = factor(ifelse(
        experiment == "fhonesty",
        CONDITIONS[2], CONDITIONS[1]
      ), CONDITIONS),
      cc1_passed = as.integer(comprehension_check1 == 1),
      cc2_passed = as.integer(comprehension_check2 == 1)
    )
  
  hpart <<- hrounds %>%
    group_by(experiment, session_code, player_id) %>%
    summarise(
      sum_honesty = 1 - sum(reported_amount - true_amount)/sum(6000 - true_amount),
      truthful = as.integer(sum_honesty == 1),
      .groups = "drop"
    ) %>% left_join(hparticipants, by = c("experiment", "session_code", "player_id")) %>%
    mutate(
      all_slack = sum_honesty == 0,
      passed_cc = as.integer(comprehension_check1 == 1 & comprehension_check2 == 1),
      classified_as_human = as.integer(human_check == 1)
    )
  reason_file <- glue("data/exp_runs/honesty_{dversion}_rounds_classified.csv")
  if (file.exists(reason_file)) {
    hreasons <<- read_csv(reason_file, show_col_types = FALSE) %>%
      rename(participant_code = player_id) %>%
      mutate(
        experiment = factor(ifelse(
          experiment == "fhonesty",
          CONDITIONS[2], CONDITIONS[1] 
        ), CONDITIONS),
        mentions_part = str_detect(tolower(reported_amount_reason), "participant"),
        mentions_firm = str_detect(tolower(reported_amount_reason), "firm"),
        mentions_other = pmin(mentions_part + mentions_firm, 1),
        mentions_payoff = 1*str_detect(tolower(reported_amount_reason), "payoff")
      )
  }
}

giftex_read_exp_data <- function(
  dversion = "2024-06-18", limit_to_part_that_pass_pre_cc = F
) {
  grounds <<- read_csv(
    glue("data/generated/giftex_{dversion}_rounds.csv"), 
    show_col_types = FALSE
  ) %>%
    mutate(
      experiment = factor(ifelse(
        experiment == "fgiftex",
        CONDITIONS[2], CONDITIONS[1]
      ), CONDITIONS),
      payoff_employer = (100 - wage)*effort,
      payoff_employee = wage - cost(effort),
      payoff_total = payoff_employer + payoff_employee
    )
  
  gparticipants <<- read_csv(
    glue("data/generated/giftex_{dversion}_participants.csv"), 
    show_col_types = FALSE
  ) %>%
    mutate(
      experiment = factor(ifelse(
        experiment == "fgiftex",
        CONDITIONS[2], CONDITIONS[1]
      ), CONDITIONS),
    )
  
  if (limit_to_part_that_pass_pre_cc) {
    gparticipants <<- gparticipants %>% 
      filter(comprehension_check_pre1 == 27 & comprehension_check_pre2 == 8)
    
    valid_dyads <- gparticipants %>% select(session_code, group_id) %>%
      group_by(session_code, group_id) %>%
      filter(n() == 2) %>%
      ungroup() %>%
      distinct()
    
    grounds <<- inner_join(grounds, valid_dyads, by = c("session_code", "group_id")) 
  }
  
  grounds_role <- grounds %>%
    group_by(experiment, session_code, group_id) %>%
    mutate(
      payoff_1 = payoff_employer,
      payoff_2 = payoff_employee
    ) %>%
    pivot_longer(
      c(payoff_1, payoff_2), values_to = "payoff", names_to = "player_id",
      names_prefix = "payoff_", names_transform = as.integer
    ) %>%
    mutate(role = ifelse(player_id == 1, "Employer", "Employee")) 
  
  gpart <<- grounds_role %>%
    group_by(
      experiment, session_code, group_id, player_id
    ) %>%
    summarise(
      payoff = sum(payoff),
      .groups = "drop"
    ) %>%
    left_join(
      gparticipants,
      by = join_by(experiment, session_code, group_id, player_id)
    ) %>%
    mutate(
      role = ifelse(player_id == 1, "Employer", "Employee"),
      cc_pre_passed = as.integer(
        comprehension_check_pre1 == 27 & comprehension_check_pre2 == 8
      ),
      cc_post_passed = as.integer(
        comprehension_check_post1 == 1 & comprehension_check_post2 == 2
      ),
      cc_post1_passed = as.integer(comprehension_check_post1 == 1),
      # The below is uninformative for exp data prior 2024-10-20
      # because of a bug in the oTree code.
      cc_post2_passed = as.integer(comprehension_check_post2 == 2)
    )
  
  gdyads <<- gpart %>%
    group_by(experiment, session_code, group_id) %>%
    summarise(mn_payoff_combined = mean(payoff),.groups = "drop") %>%
    left_join(
      gpart %>%
        filter(player_id == 1) %>%
        group_by(experiment, session_code, group_id) %>%
        summarise(mn_payoff_firm = mean(payoff), .groups = "drop"),
      by = c("experiment", "session_code", "group_id")
    ) %>%
    left_join(
      gpart %>%
        filter(player_id == 2) %>%
        group_by(experiment, session_code, group_id) %>%
        summarise(mn_payoff_manager = sum(payoff), .groups = "drop"),
      by = c("experiment", "session_code", "group_id")
    )
  reason_file <- glue("data/exp_runs/giftex_{dversion}_rounds_classified.csv")
  if (file.exists(reason_file)) {
    greasons <<- read_csv(reason_file, show_col_types = FALSE) %>%
      mutate(
        experiment = factor(ifelse(
          experiment == "fgiftex",
          CONDITIONS[2], CONDITIONS[1] 
        ), CONDITIONS),
        wage_mentions_part = str_detect(tolower(wage_reason), "participant"),
        wage_mentions_manager = str_detect(tolower(wage_reason), "manager"),
        wage_mentions_other = pmin(wage_mentions_part + wage_mentions_manager, 1),
        wage_mentions_payoff = 1*str_detect(tolower(wage_reason), "payoff"),
        effort_mentions_part = str_detect(tolower(effort_reason), "participant"),
        effort_mentions_firm = str_detect(tolower(effort_reason), "firm"),
        effort_mentions_other = pmin(effort_mentions_part + effort_mentions_firm, 1),
        effort_mentions_payoff = 1*str_detect(tolower(effort_reason), "payoff")
      )
  }
}

trust_read_exp_data <- function(dversion = "2024-06-18") {
  trounds <<- read_csv(
    glue("data/generated/trust_{dversion}_rounds.csv"),  show_col_types = FALSE
  ) %>%
    mutate(
      experiment = factor(ifelse(
        experiment == "ftrust",
        CONDITIONS[2], CONDITIONS[1]
      ), CONDITIONS),
      pct_returned = sent_back_amount/(3*sent_amount),
      payoff_inv = 100 - sent_amount + sent_back_amount,
      payoff_man = 3*sent_amount - sent_back_amount,
      payoff_total = payoff_inv + payoff_man
    )
  
  tparticipants <<- read_csv(
    glue("data/generated/trust_{dversion}_participants.csv"),  show_col_types = FALSE
  ) %>%
    mutate(
      experiment = factor(ifelse(
        experiment == "ftrust",
        CONDITIONS[2], CONDITIONS[1] 
      ), CONDITIONS),
      role = ifelse(role_in_group == 1, "Sender", "Receiver"),
      cc_passed = as.integer(comprehension_check == 3),
      mc_passed = as.integer(manipulation_check == role_in_group)
    )
  
  
  tdyads <<- tparticipants %>%
    group_by(experiment, session_code, group_id) %>%
    summarise(mn_payoff_combined = mean(payoff), .groups = "drop") %>%
    left_join(
      tparticipants %>%
        filter(role_in_group == 1) %>%
        group_by(experiment, session_code, group_id) %>%
        summarise(mn_payoff_inv = mean(payoff), .groups = "drop"),
      by = c("experiment", "session_code", "group_id")
    ) %>%
    left_join(
      tparticipants %>%
        filter(role_in_group == 2) %>%
        group_by(experiment, session_code, group_id) %>%
        summarise(mn_payoff_man = mean(payoff), .groups = "drop"),
      by = c("experiment", "session_code", "group_id")
    )
  
  reason_file <- glue("data/exp_runs/trust_{dversion}_rounds_classified.csv")
  if (file.exists(reason_file)) {
    treasons <<- read_csv(reason_file, show_col_types = FALSE) %>%
      mutate(
        experiment = factor(ifelse(
          experiment == "ftrust",
          CONDITIONS[2], CONDITIONS[1] 
        ), CONDITIONS),
        sent_mentions_part = str_detect(tolower(sent_reason), "participant"),
        sent_mentions_manager = str_detect(tolower(sent_reason), "manager"),
        sent_mentions_other = pmin(sent_mentions_part + sent_mentions_manager, 1),
        sent_mentions_payoff = 1*str_detect(tolower(sent_reason), "payoff"),
        back_mentions_part = str_detect(tolower(sent_back_reason), "participant"),
        back_mentions_investor = str_detect(tolower(sent_back_reason), "investor"),
        back_mentions_other = pmin(back_mentions_part + back_mentions_investor, 1),
        back_mentions_payoff = 1*str_detect(tolower(sent_back_reason), "payoff")
      )
  }
  
}
  
  
