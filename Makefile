# If you are new to Makefiles: https://makefiletutorial.com


# Commands

RSCRIPT := Rscript --encoding=UTF-8
PYTHON := . venv/bin/activate; python

# Static Output

OUTPUT := static/presentation.pdf

# Main targets

PRESENTATION := output/presentation.pdf

# Setup targets

VENV := venv/touchfile

# Data Targets

TRUST_EXP_DATA := data/generated/trust_participants.csv \
	data/generated/trust_rounds.csv
DECEPTION_EXP_DATA := data/generated/deception_participants.csv \
	data/generated/deception_rounds.csv
HONESTY_EXP_DATA := data/generated/honesty_participants.csv \
	data/generated/honesty_rounds.csv
GIFT_EXP_DATA := data/generated/gift_participants.csv \
	data/generated/gift_rounds.csv

ALL_TARGETS := $(PRESENTATION) $(TRUST_EXP_DATA) \
	$(DECEPTION_EXP_DATA) $(HONESTY_EXP_DATA) $(GIFT_EXP_DATA)
	
# Phony targets

.phony: all clean distclean 


all: $(OUTPUT)

clean:
	rm -f $(ALL_TARGETS)

distclean: clean
	rm -rf venv
	rm -rf output/*
	rm -rf data/generated/*

# Recipes

$(VENV): requirements.txt 
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	touch $(VENV)

$(TRUST_EXP_DATA): $(VENV) code/extract_trust_exp_data.py \
	data/exp_runs/trust_otree_2024-03-19.csv \
	data/exp_runs/trust_botex_db_2024-03-19.sqlite3
	$(PYTHON) code/extract_trust_exp_data.py

$(DECEPTION_EXP_DATA): $(VENV) code/extract_deception_exp_data.py \
	data/exp_runs/deception_otree_1_2024-03-24.csv \
	data/exp_runs/deception_otree_2_2024-03-24.csv \
	data/exp_runs/deception_otree_3_2024-03-24.csv \
	data/exp_runs/deception_botex_db_2024-03-24.sqlite3
	$(PYTHON) code/extract_deception_exp_data.py

$(HONESTY_EXP_DATA): $(VENV) code/extract_honesty_exp_data.py \
	data/exp_runs/honesty_otree_2024-03-27.csv \
	data/exp_runs/honesty_botex_db_2024-03-27.sqlite3
	$(PYTHON) code/extract_honesty_exp_data.py

$(GIFT_EXP_DATA): $(VENV) code/extract_gift_exp_data.py \
	data/exp_runs/gift_otree_2024-03-29.csv \
	data/exp_runs/gift_botex_db_2024-03-29.sqlite3
	$(PYTHON) code/extract_gift_exp_data.py

$(PRESENTATION): $(TRUST_EXP_DATA) $(DECEPTION_EXP_DATA) \
	$(HONESTY_EXP_DATA) $(GIFT_EXP_DATA) \
	docs/materials/beamer_theme_trr266_16x9.sty \
	docs/materials/trr266_logo.eps \
	docs/materials/trust_otree_inst.jpeg \
	docs/materials/ftrust_otree_inst.jpeg \
	docs/_quarto.yml \
	docs/presentation.qmd
	quarto render docs/presentation.qmd --quiet
	rm -rf output/presentation_files

$(OUTPUT): $(PRESENTATION)
	cp $(PRESENTATION) $(OUTPUT)
	
