# If you are new to Makefiles: https://makefiletutorial.com


# Commands

RSCRIPT := Rscript --encoding=UTF-8
PYTHON := . venv/bin/activate; python

# Static Output

OUTPUT := static/presentation.pdf static/appendix_trust_example.pdf \
	static/eaadc24_talk.pdf

# Main targets

PRESENTATION := output/presentation.pdf
APPENDIX_TRUST_EXAMPLE := output/appendix_trust_example.pdf
EAADC24_TALK := output/eaadc24_talk.pdf

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
EAADC24_EXP_DATA := data/generated/eaadc24_participants.csv \
	data/generated/eaadc24_rounds.csv

# Experiment targets

EXP_RUN_APPENDIX := data/exp_runs/app_example.sqlite3


# All Targets besides experiment targets

ALL_TARGETS := $(OUTPUT) $(DATA_TARGETS)
	
# Phony targets

.phony: all clean distclean 

cleandb:
	rm -rf data/generated/botex_db.sqlite3
	rm -rf otree/db.sqlite3

all: $(OUTPUT)

clean:
	rm -f $(ALL_TARGETS)

distclean: clean
	rm -rf venv
	rm -rf output/*
	rm -rf data/generated/*
	rm -rf $(EXP_RUN_APPENDIX)

# oTree Dependencies

$(OTREE_TRUST): otree/trust/__init__.py \
	otree/trust/instructions.html \
	otree/trust/Introduction.html \
	otree/trust/Send.html \
	otree/trust/SendBack.html \
	otree/trust/Results.html \
	otree/trust/Thanks.html
	

# Recipes

$(VENV): requirements.txt 
	python3 -m venv venv
	. venv/bin/activate 
	pip install -r requirements.txt
	pip install --no-deps otree 
	pip install -e ../botex
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

$(EAADC24_EXP_DATA): $(VENV) code/extract_mftrust_exp_data.py \
	data/exp_runs/eaadc24_otree_2024-05-12.csv \
	data/exp_runs/eaadc24_botex_db_2024-05-12.sqlite3
	$(PYTHON) code/extract_mftrust_exp_data.py

$(EXP_RUN_APPENDIX): $(VENV) $(OTREE_TRUST) \
	code/run_appendix_trust_example.py
	$(PYTHON) code/run_appendix_trust_example.py
	
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
	
$(APPENDIX_TRUST_EXAMPLE): $(EXP_RUN_APPENDIX) \
	docs/appendix_trust_example.qmd
	quarto render docs/appendix_trust_example.qmd --quiet
	rm -rf output/appendix_trust_example_files

$(EAADC24_TALK): $(EAADC24_EXP_DATA) \
	docs/materials/beamer_theme_trr266_16x9.sty \
	docs/materials/trr266_logo.eps \
	docs/materials/eaadc24_otree_inst.jpeg \
	docs/materials/eaadc24_qrcode.jpeg \
	docs/materials/mei_xie_yuan_jackson_pnas_2024.jpeg \
	docs/materials/manning_zhu_horton_arxiv_2024.jpeg \
	docs/_quarto.yml \
	docs/eaadc24_talk.qmd
	quarto render docs/eaadc24_talk.qmd --quiet
	rm -rf output/eaadc24_talk_files


$(OUTPUT): $(PRESENTATION) $(APPENDIX_TRUST_EXAMPLE) $(EAADC24_TALK)
	cp $(PRESENTATION) static/
	cp $(APPENDIX_TRUST_EXAMPLE) static/
	cp $(EAADC24_TALK) static/
	
