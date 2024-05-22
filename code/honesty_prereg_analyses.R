suppressMessages({
  library(tidyverse)
  library(fixest)
})

hrounds <- read_csv(
  "data/generated/honesty_rounds.csv", show_col_types = FALSE
) %>%
  mutate(
    experiment = factor(ifelse(
      experiment == "fhonesty",
      "Business Framing", "Neutral Framing"
    ), c("Neutral Framing", "Business Framing")),
    slack = reported_amount - true_amount,
    pct_slack_claimed = (reported_amount - true_amount)/(6000 - true_amount)
  )

hparticipants <- read_csv(
  "data/generated/honesty_participants.csv", show_col_types = FALSE
) %>%
  mutate(
    experiment = factor(ifelse(
      experiment == "fhonesty",
      "Business Framing", "Neutral Framing"
    ), c("Neutral Framing", "Business Framing")),
  )

# --- Pre-Registered Tests: Honesty Experiment ---------------------------------

# RQ H-1: Does business framing affect the likelihood of truth telling?

h1_table <- table(hrounds$reported_amount == hrounds$true_amount, hrounds$experiment)
h1_table
h1_test <- prop.test(h1_table[2,], colSums(h1_table))
h1_test
h1_test$conf.int

# RQ H-2: Does business framing affect lying intensity?

# Round Level

mod_honesty_slack_claimed_fe <- feols(
  pct_slack_claimed ~ experiment | round, 
  cluster = c("round", "session_code^player_id"), 
  data = hrounds %>% filter(reported_amount != true_amount)
)
summary(mod_honesty_slack_claimed_fe)

mod_honesty_slack_claimed <- feols(
  pct_slack_claimed ~ experiment*round, 
  cluster = c("round", "session_code^player_id"), 
  data = hrounds %>% filter(reported_amount != true_amount)
)
summary(mod_honesty_slack_claimed)
# Test coefficient is the interaction 
confint(mod_honesty_slack_claimed)[4,]


# Participant Level

hpart <- hrounds %>%
  group_by(experiment, session_code, player_id) %>%
  summarise(
    pct_slack_claimed = sum(reported_amount - true_amount)/sum(6000 - true_amount),
    .groups = "drop"
  )

h3_table <- table(hpart$pct_slack_claimed == 0, hpart$experiment)
h3_table
h3_test <- prop.test(h3_table[2,], colSums(h3_table))
h3_test
h3_test$conf.int
                  
t.test(pct_slack_claimed ~ experiment, data = hpart %>% filter(pct_slack_claimed > 0))
wilcox.test(pct_slack_claimed ~ experiment, data = hpart %>% filter(pct_slack_claimed > 0))
