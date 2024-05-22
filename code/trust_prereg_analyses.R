suppressMessages({
  library(tidyverse)
  library(fixest)
})

trounds <- read_csv(
  "data/generated/trust_rounds.csv", show_col_types = FALSE
) %>%
  mutate(
    experiment = factor(ifelse(
      experiment == "ftrust",
      "Business Framing", "Neutral Framing"
    ), c("Neutral Framing", "Business Framing")),
    pct_returned = sent_back_amount/(3*sent_amount)
  )

tparticipants <- read_csv(
  "data/generated/trust_participants.csv", show_col_types = FALSE
) %>%
  mutate(
    experiment = factor(ifelse(
      experiment == "ftrust",
      "Business Framing", "Neutral Framing"
    ), c("Neutral Framing", "Business Framing"))
  )

dyads <- tparticipants %>%
  group_by(experiment, session_code, group_id) %>%
  summarise(sum_payoff = sum(payoff),.groups = "drop")

# --- Pre-Registered Tests: Trust Experiment -----------------------------------

# RQ T-1: Does business framing affect the trust of the sender?

# Trust Level

mod_trust_sent_fe <- feols(
  sent_amount ~ experiment | round, 
  cluster = c("round", "session_code^group_id"), data = trounds
)
summary(mod_trust_sent_fe)

# Trust increase over rounds

mod_trust_sent <- feols(
  sent_amount ~ experiment*round, 
  cluster = c("round", "session_code^group_id"), data = trounds
)
summary(mod_trust_sent)
# Test coefficient is the interaction 
confint(mod_trust_sent)[4,]


# RQ T-2: Does business framing affect reciprocative behavior of the receiver?

# Reciprocate Level

mod_trust_pct_returned_fe <- feols(
  pct_returned ~ experiment | round, 
  cluster = c("round", "session_code^group_id"), data = trounds
)
summary(mod_trust_pct_returned_fe)

# Reciprocate increase over rounds

mod_trust_pct_returned <- feols(
  pct_returned ~ round*experiment, 
  cluster = c("round", "session_code^group_id"), data = trounds
)
summary(mod_trust_pct_returned)
# Test coefficient is the interaction 
confint(mod_trust_pct_returned)[4,]


# RQ T-3: Does the business framing affect overall payoffs? 

# Participant Level

t.test(payoff ~ experiment, data = tparticipants)
wilcox.test(payoff ~ experiment, data = tparticipants)

t.test(payoff ~ experiment, data = tparticipants %>% filter(role_in_group == 1))
wilcox.test(payoff ~ experiment, data = tparticipants %>% filter(role_in_group == 1))

t.test(payoff ~ experiment, data = tparticipants %>% filter(role_in_group == 2))
wilcox.test(payoff ~ experiment, data = tparticipants %>% filter(role_in_group == 2))

# Dyad Level

t.test(sum_payoff ~ experiment, data = dyads)
wilcox.test(sum_payoff ~ experiment, data = dyads)
