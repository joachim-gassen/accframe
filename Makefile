# If you are new to Makefiles: https://makefiletutorial.com


# Commands

RSCRIPT := Rscript --encoding=UTF-8
PYTHON := python

# Static Output

OUTPUT := static/honesty_power_analysis.pdf \
	static/trust_power_analysis.pdf static/giftex_power_analysis.pdf \
	static/results_main.pdf static/results_rationales.pdf

# Main targets

HONESTY_POWER := output/honesty_power_analysis.pdf
TRUST_POWER := output/trust_power_analysis.pdf
GIFTEX_POWER := output/giftex_power_analysis.pdf
RESULTS_MAIN := output/results_main.pdf
RESULTS_RATIONALES := output/results_rationales.pdf

MAIN_TARGETS := $(HONESTY_POWER) $(TRUST_POWER) $(GIFTEX_POWER) \
	$(RESULTS_MAIN) $(RESULTS_RATIONALES)


# Data Targets

# True amounts for honesty experiment
HONESTY_TRUE_AMOUNTS := data/generated/honesty_true_amounts.csv

# Pre-Tests for Power analysis
PTVERSION_HONESTY = 2024-03-27
PTVERSION_GIFTEX = 2024-04-30
PTVERSION_TRUST = 2024-04-29

HONESTY_PT_DATA := data/generated/honesty_$(PTVERSION_HONESTY)_participants.csv \
	data/generated/honesty_$(PTVERSION_HONESTY)_rounds.csv
GIFTEX_PT_DATA := data/generated/giftex_$(PTVERSION_GIFTEX)_participants.csv \
	data/generated/giftex_$(PTVERSION_GIFTEX)_rounds.csv
TRUST_PT_DATA := data/generated/trust_$(PTVERSION_TRUST)_participants.csv \
	data/generated/trust_$(PTVERSION_TRUST)_rounds.csv

# Main Experiment Data
DVERSION_HONESTY = 2024-06-17
DVERSION_GIFTEX = 2024-06-18
DVERSION_TRUST = 2024-06-18

HONESTY_EXP_DATA := data/generated/honesty_$(DVERSION_HONESTY)_participants.csv \
	data/generated/honesty_$(DVERSION_HONESTY)_rounds.csv
GIFTEX_EXP_DATA := data/generated/giftex_$(DVERSION_GIFTEX)_participants.csv \
	data/generated/giftex_$(DVERSION_GIFTEX)_rounds.csv
TRUST_EXP_DATA := data/generated/trust_$(DVERSION_TRUST)_participants.csv \
	data/generated/trust_$(DVERSION_TRUST)_rounds.csv

HONESTY_RATIONALES_DATA := data/exp_runs/honesty_$(DVERSION_HONESTY)_rounds_classified.csv
GIFTEX_RATIONALES_DATA := data/exp_runs/giftex_$(DVERSION_GIFTEX)_rounds_classified.csv
TRUST_RATIONALES_DATA := data/exp_runs/trust_$(DVERSION_TRUST)_rounds_classified.csv

DATA_TARGETS := $(GIFTEX_TRUE_AMOUNTS) \
	$(HONESTY_PT_DATA) $(TRUST_PT_DATA) $(GIFTEX_PT_DATA) \
	$(HONESTY_EXP_DATA) $(TRUST_EXP_DATA) $(GIFTEX_EXP_DATA) \
	$(HONESTY_RATIONALES_DATA) $(GIFTEX_RATIONALES_DATA) $(TRUST_RATIONALES_DATA)

# All Targets besides experiment targets

ALL_TARGETS := $(OUTPUT) $(DATA_TARGETS)
	
# Phony targets

.phony: all clean distclean 

cleandb:
	rm -rf data/generated/botex_db.sqlite3
	rm -rf otree/db.sqlite3

all: $(OUTPUT)

clean:
	rm -f $(MAIN_TARGETS) $(OUTPUT)

distclean: clean
	rm -rf output/*
	rm -rf data/generated/*
 

# Recipes

$(HONESTY_TRUE_AMOUNTS): $(VENV) code/honesty_gen_true_amounts.R
	$(RSCRIPT) code/honesty_gen_true_amounts.R

$(HONESTY_PT_DATA): $(VENV) code/honesty_extract_exp_data.py \
	data/exp_runs/honesty_otree_$(PTVERSION_HONESTY).csv \
	data/exp_runs/honesty_botex_db_$(PTVERSION_HONESTY).sqlite3
	$(PYTHON) code/honesty_extract_exp_data.py $(PTVERSION_HONESTY)

$(GIFTEX_PT_DATA): $(VENV) code/giftex_extract_exp_data.py \
	data/exp_runs/giftex_otree_$(PTVERSION_GIFTEX).csv \
	data/exp_runs/giftex_botex_db_$(PTVERSION_GIFTEX).sqlite3
	$(PYTHON) code/giftex_extract_exp_data.py $(PTVERSION_GIFTEX)

$(TRUST_PT_DATA): $(VENV) code/trust_extract_exp_data.py \
	data/exp_runs/trust_otree_$(PTVERSION_TRUST).csv \
	data/exp_runs/trust_botex_db_$(PTVERSION_TRUST).sqlite3
	$(PYTHON) code/trust_extract_exp_data.py $(PTVERSION_TRUST)

$(HONESTY_EXP_DATA): $(VENV) code/honesty_extract_exp_data.py \
	data/exp_runs/honesty_otree_$(DVERSION_HONESTY).csv \
	data/exp_runs/honesty_botex_db_$(DVERSION_HONESTY).sqlite3
	$(PYTHON) code/honesty_extract_exp_data.py

$(GIFTEX_EXP_DATA): $(VENV) code/giftex_extract_exp_data.py \
	data/exp_runs/giftex_otree_$(DVERSION_GIFTEX).csv \
	data/exp_runs/giftex_botex_db_$(DVERSION_GIFTEX).sqlite3
	$(PYTHON) code/giftex_extract_exp_data.py

$(TRUST_EXP_DATA): $(VENV) code/trust_extract_exp_data.py \
	data/exp_runs/trust_otree_$(DVERSION_TRUST).csv \
	data/exp_runs/trust_botex_db_$(DVERSION_TRUST).sqlite3
	$(PYTHON) code/trust_extract_exp_data.py

$(HONESTY_RATIONALES_DATA): $(VENV) code/honesty_classify_rationales.py \
	$(HONESTY_EXP_DATA)
	$(PYTHON) code/honesty_classify_rationales.py

$(GIFTEX_RATIONALES_DATA): $(VENV) code/giftex_classify_rationales.py \
	$(GIFTEX_EXP_DATA)
	$(PYTHON) code/giftex_classify_rationales.py

$(TRUST_RATIONALES_DATA): $(VENV) code/trust_classify_rationales.py \
	$(TRUST_EXP_DATA)
	$(PYTHON) code/trust_classify_rationales.py

$(HONESTY_POWER): $(HONESTY_PT_DATA) $(HONESTY_TRUE_AMOUNTS) \
	docs/_quarto.yml \
	docs/honesty_power_analysis.qmd
	quarto render docs/honesty_power_analysis.qmd --quiet
	rm -rf output/honesty_power_analysis_files

$(GIFTEX_POWER): $(GIFTEX_PT_DATA) \
	docs/_quarto.yml \
	docs/giftex_power_analysis.qmd
	quarto render docs/giftex_power_analysis.qmd --quiet
	rm -rf output/giftex_power_analysis_files

$(TRUST_POWER): $(TRUST_PT_DATA) \
	docs/_quarto.yml \
	docs/trust_power_analysis.qmd
	quarto render docs/trust_power_analysis.qmd --quiet
	rm -rf output/trust_power_analysis_files

$(RESULTS_MAIN): $(HONESTY_EXP_DATA) $(TRUST_EXP_DATA) $(GIFTEX_EXP_DATA) \
	docs/_quarto.yml \
	docs/results_main.qmd
	quarto render docs/results_main.qmd --quiet
	rm -rf output/results_main_files

$(RESULTS_RATIONALES): $(HONESTY_RATIONALES_DATA) $(GIFTEX_RATIONALES_DATA) \
	$(TRUST_RATIONALES_DATA)  \
	docs/_quarto.yml \
	docs/results_rationales.qmd
	quarto render docs/results_rationales.qmd --quiet
	rm -rf output/results_rationales_files

$(OUTPUT): $(HONESTY_POWER) $(TRUST_POWER) $(GIFTEX_POWER) \
	$(RESULTS_MAIN) $(RESULTS_RATIONALES)
	cp $(HONESTY_POWER) static/
	cp $(TRUST_POWER) static/
	cp $(GIFTEX_POWER) static/
	cp $(RESULTS_MAIN) static/
	cp $(RESULTS_RATIONALES) static/

	
