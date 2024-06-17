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
    honesty = 1 - (reported_amount - true_amount)/(6000 - true_amount)
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
  honesty ~ experiment | round, 
  cluster = c("round", "session_code^player_id"), 
  data = hrounds %>% filter(reported_amount != true_amount)
)
summary(mod_honesty_slack_claimed_fe)

mod_honesty_slack_claimed <- feols(
  honesty ~ experiment*round, 
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
    honesty = 1 - sum(reported_amount - true_amount)/sum(6000 - true_amount),
    .groups = "drop"
  )

h3_table <- table(hpart$honesty == 1, hpart$experiment)
h3_table
h3_test <- prop.test(h3_table[2,], colSums(h3_table))
h3_test
h3_test$conf.int
                  
t.test(honesty ~ experiment, data = hpart %>% filter(honesty < 1))
wilcox.test(honesty ~ experiment, data = hpart %>% filter(honesty < 1))
