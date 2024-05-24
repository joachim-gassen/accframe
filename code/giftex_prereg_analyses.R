suppressMessages({
  library(tidyverse)
  library(fixest)
})

grounds <- read_csv(
  "data/generated/gift_rounds.csv", show_col_types = FALSE
) %>%
  mutate(
    experiment = factor(ifelse(
      experiment == "fgiftex",
      "Business Framing", "Neutral Framing"
    ), c("Neutral Framing", "Business Framing")),
  )

gparticipants <- read_csv(
  "data/generated/gift_participants.csv", show_col_types = FALSE
) %>%
  mutate(
    experiment = factor(ifelse(
      experiment == "fgiftex",
      "Business Framing", "Neutral Framing"
    ), c("Neutral Framing", "Business Framing")),
  )


# --- Pre-Registered Tests: Gift Exchange Experiment ---------------------------

# RQ G-1: Does business framing affect the generosity of the sender?

mod_wage_fe <- feols(
  wage ~ experiment | round, 
  cluster = c("round", "session_code^group_id"), data = grounds
)
summary(mod_wage_fe)
mod_wage <- feols(
  wage ~ experiment*round, 
  cluster = c("round", "session_code^group_id"), data = grounds
)
summary(mod_wage)
# Test coefficient is the interaction 
confint(mod_wage)[4,]

# RQ G-2: Does business framing affect the effort of the receiver?

mod_effort_fe <- feols(
  effort ~ experiment | round, 
  cluster = c("round", "session_code^group_id"), data = grounds
)
summary(mod_effort_fe)
mod_effort <- feols(
  effort ~ experiment*round, 
  cluster = c("round", "session_code^group_id"), data = grounds
)
summary(mod_effort)
# Test coefficient is the interaction 
confint(mod_effort)[4,]

# RQ G-3: Does business framing affect the sensitivity of receiver effort?

mod_effort_sensitivity_fe <- feols(
  effort ~ wage*experiment | round, 
  cluster = c("round", "session_code^group_id"), data = grounds
)
summary(mod_effort_sensitivity_fe)
# Test coefficient is the interaction 
confint(mod_effort_sensitivity_fe)[3,]


# Participant Level

cost <- function(e) {
  case_when(
    e == 0.1 ~ 0,
    e == 0.2 ~ 1,
    e == 0.3 ~ 2,
    e == 0.4 ~ 4,
    e == 0.5 ~ 6,
    e == 0.6 ~ 8,
    e == 0.7 ~ 10,
    e == 0.8 ~ 12,
    e == 0.9 ~ 15,
    e == 1.0 ~ 28,
    TRUE ~ NA
  )
}

part <- grounds %>%
  group_by(experiment, session_code, group_id) %>%
  summarise(
    payoff_1 = sum((100 - wage)*effort),
    payoff_2 = sum(wage - cost(effort)),
    .groups = "drop"
  ) %>%
  pivot_longer(
    c(payoff_1, payoff_2), values_to = "payoff", names_to = "player_id",
    names_prefix = "payoff_", names_transform = as.integer
  ) %>%
  mutate(role = ifelse(player_id == 1, "Employer", "Employee"))

feols(payoff ~ experiment*role, data = part)

t.test(payoff ~ experiment, data = part)
wilcox.test(payoff ~ experiment, data = part)

t.test(payoff ~ experiment, data = part %>% filter(role == "Employer"))
wilcox.test(payoff ~ experiment, data = part %>% filter(role == "Employer"))

t.test(payoff ~ experiment, data = part %>% filter(role == "Employee"))
wilcox.test(payoff ~ experiment, data = part %>% filter(role == "Employee"))

dyads <- part %>%
  group_by(experiment, session_code, group_id) %>%
  summarise(sum_payoff = sum(payoff),.groups = "drop")

t.test(sum_payoff ~ experiment, data = dyads)
wilcox.test(sum_payoff ~ experiment, data = dyads)

