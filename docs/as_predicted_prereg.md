# ACCFRAME: Exploring Contextualization in Accounting Experiments using LLMs

(AsPredicted #179630)

Created:       06/17/2024 03:02 AM (PT)

Author(s)
Fikir Worku Edossa (Humboldt-Universität zu Berlin) - fikir.worku.edossa@hu-berlin.de
Joachim Gassen (Humboldt-Universität zu Berlin) - gassen@wiwi.hu-berlin.de
Victor Maas (University of Amsterdam) - V.S.Maas@uva.nl


1) Have any data been collected for this study already?
It's complicated. We have already collected some data but explain in Question 8 why readers may consider this a valid pre-registration nevertheless.

2) What's the main question being asked or hypothesis being tested in this study?
Does contextualization affect the outcome of classic economic games used in the accounting literature when these games are played by LLM participants?

3) Describe the key dependent variable(s) specifying how they will be measured.
We conduct three different experiments. Each experiment will be run in two variants (see Q4) and over 10 rounds. 

Honesty Game (Evans, Hannan, Krishnan, Moser, TAR 2001): The dependent variables are whether the participant miss-reports and if so, the percent of budget slack claimed, both at the round and the participant level.
Trust Game (Berg, Dickhaut, McCabe, GEB1995): The dependent variables are the amount sent and the percentage returned, both at the round and at the participant level.
Gift exchange Game (Fehr, Kirchsteiger, Riedl, QJE 1993): The dependent variables are the wage paid and the effort level chosen, both at the round and at the participant level.

All research materials are available in the Github repository: https://github.com/joachim-gassen/accframe. The repository is currently private but will be tagged prior to the experimental runs and made public when the working paper is released.

4) How many and which conditions will participants be assigned to?
For each experiment, we will run a condition without any contextualization and a condition where we contextualize the experiment in a business setting. We will assign each participating LLM bot to only one condition.

5) Specify exactly which analyses you will conduct to examine the main question/hypothesis.
We use OLS regressions with round fixed effects as well as with our treatment indicator interacted with a round variable to estimate the respective treatment effects. Standard errors will be clustered by dyad (trust and gift exchange) or participant level (honesty) as well as at the round level (all experiments, two-way clustering). The effect of the conditions on the probability of truthful reporting will be tested based on a univariate Chi-square test. At the participant level, we will use simple t-tests or Chi-square tests to provide corroborative evidence but we caution that our participant level results will be affected by limited power.

All planned analyses are included in the respective code files in our repository mentioned above.

6) Describe exactly how outliers will be defined and handled, and your precise rule(s) for excluding observations.
While we include comprehension checks in a short post-experimental questionnaire, we will not exclude any observations from our main analysis. We will also include incomplete experimental runs, should any technical issues arise during the execution of the experiment. Also, as our dependent variables are bounded by experimental design, we will not employ any outlier treatment.

7) How many observations will be collected or what will determine sample size?
No need to justify decision, but be precise about exactly how the number will be determined.
Based on our power analyses (included in the GitHub repository), we plan to run the trust and gift exchange experiments with 50 dyads (100 participants) per condition. The honesty game will be run with 100 participants.

8) Anything else you would like to pre-register? 
(e.g., secondary analyses, variables collected for exploratory purposes, unusual analyses planned?)
All participants will be "played" by using the current version of the 'botex' package and the gpt-4o-2024-05-13 model of OpenAI. We will use the standard temperature of the chat completion endpoint (1.0) and also all other parameters are at the standard level.

PLEASE NOTE: This pre-registration is a rerun of a pre-registered experiment (https://aspredicted.org/J6H_Y3R) as we identified some inconsistencies in our three sets of experimental materials. To rule out that these have affected our findings, we will run the three experiments again using the updated materials. All materials, data and results from the experimental runs of our first pre-registration are available in our GitHub repository.

9) Give a title for this AsPredicted pre-registration
ACCFRAME: Exploring Contextualization in Accounting Experiments using LLMs

10) Type of study
Experiment

11) Data Source
Other: LLMs (see answer to Q8)