suppressMessages({
  library(tidyverse)
  library(fixest)
})

grounds <- read_csv(
  "data/generated/gift_rounds.csv", show_col_types = FALSE
) %>%
  mutate(
    experiment = factor(ifelse(
      experiment == "fgift",
      "Business Framing", "Neutral Framing"
    ), c("Neutral Framing", "Business Framing")),
  )

gparticipants <- read_csv(
  "data/generated/gift_participants.csv", show_col_types = FALSE
) %>%
  mutate(
    experiment = factor(ifelse(
      experiment == "fgift",
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
