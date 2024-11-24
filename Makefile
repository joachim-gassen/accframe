# If you are new to Makefiles: https://makefiletutorial.com

# Commands

RSCRIPT := Rscript --encoding=UTF-8
PYTHON := python
PDFLATEX := pdflatex --interaction=batchmode 
INKSCAPE := inkscape -n 1

# Code dependencies

RESULT_OBJECTS_CODE := code/utils.R \
	code/honesty_create_result_objects.R \
	code/giftex_create_result_objects.R \
	code/trust_create_result_objects.R \
	
# Output targets

HONESTY_POWER := output/honesty_power_analysis.pdf
TRUST_POWER := output/trust_power_analysis.pdf
GIFTEX_POWER := output/giftex_power_analysis.pdf
RESULTS_MAIN := output/results_main.pdf
PRESENTATION := output/presentation.pdf
RESULTS_RATIONALES := output/results_rationales.pdf
EVANS_COMPARISON := output/evans_et_al_comparison.pdf
OA_TRUST_EXAMPLE := output/online_appendix_trust_example.docx
TEX_FIGURES := output/figure1a_otree.svg \
	output/figure1b_mixed.svg \
	output/figure1c_botex.svg 
R_FIGURES := output/figure2_honesty_pct_honest.svg \
	output/figure3_giftex_effort_on_wage.svg \
	output/figure4_trust_investment.svg 
FIGURES :=  $(TEX_FIGURES) $(R_FIGURES)
	
OUTPUT := $(HONESTY_POWER) $(TRUST_POWER) $(GIFTEX_POWER) \
	$(RESULTS_MAIN) $(PRESENTATION) \
	$(RESULTS_RATIONALES) $(EVANS_COMPARISON) $(OA_TRUST_EXAMPLE) $(FIGURES)

# Static Output

STATIC := static/results_main.pdf static/presentation.pdf

# Data Targets

# True amounts for honesty experiment
HONESTY_TRUE_AMOUNTS := data/static/honesty_true_amounts.csv

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

HONESTY_RATIONALES_DATA := data/static/honesty_$(DVERSION_HONESTY)_rounds_classified.csv
GIFTEX_RATIONALES_DATA := data/static/giftex_$(DVERSION_GIFTEX)_rounds_classified.csv
TRUST_RATIONALES_DATA := data/static/trust_$(DVERSION_TRUST)_rounds_classified.csv

# sim results for power analysis are created by doc code if missing
STATIC_DATA_TARGETS :=  $(GIFTEX_TRUE_AMOUNTS) \
	$(HONESTY_RATIONALES_DATA) $(GIFTEX_RATIONALES_DATA) $(TRUST_RATIONALES_DATA)

TEMP_DATA_TARGETS := \
	$(HONESTY_PT_DATA) $(TRUST_PT_DATA) $(GIFTEX_PT_DATA) \
	$(HONESTY_EXP_DATA) $(TRUST_EXP_DATA) $(GIFTEX_EXP_DATA) 


# All Targets

ALL_TARGETS := $(OUTPUT) $(STATIC) 
	
# Phony targets

.phony: all clean distclean 

cleandb:
	rm -rf data/generated/botex_db.sqlite3
	rm -rf otree/db.sqlite3

all: $(ALL_TARGETS)

clean:
	rm -f $(ALL_TARGETS)

distclean: clean
	rm -f $(TEMP_DATA_TARGETS)
	rm -rf output/*
	rm -rf static/*
	rm -rf data/generated/*
	rm -rf data/static/*
	rm -rf otree/db.sqlite3

# Recipes

# --- Data recipes -------------------------------------------------------------

$(HONESTY_TRUE_AMOUNTS): code/honesty_gen_true_amounts.R
	$(RSCRIPT) code/honesty_gen_true_amounts.R

$(HONESTY_PT_DATA): code/honesty_extract_exp_data.py \
	data/exp_runs/honesty_otree_$(PTVERSION_HONESTY).csv \
	data/exp_runs/honesty_botex_db_$(PTVERSION_HONESTY).sqlite3
	$(PYTHON) code/honesty_extract_exp_data.py $(PTVERSION_HONESTY)

$(GIFTEX_PT_DATA): code/giftex_extract_exp_data.py \
	data/exp_runs/giftex_otree_$(PTVERSION_GIFTEX).csv \
	data/exp_runs/giftex_botex_db_$(PTVERSION_GIFTEX).sqlite3
	$(PYTHON) code/giftex_extract_exp_data.py $(PTVERSION_GIFTEX)

$(TRUST_PT_DATA): code/trust_extract_exp_data.py \
	data/exp_runs/trust_otree_$(PTVERSION_TRUST).csv \
	data/exp_runs/trust_botex_db_$(PTVERSION_TRUST).sqlite3
	$(PYTHON) code/trust_extract_exp_data.py $(PTVERSION_TRUST)

$(HONESTY_EXP_DATA): code/honesty_extract_exp_data.py \
	data/exp_runs/honesty_otree_$(DVERSION_HONESTY).csv \
	data/exp_runs/honesty_botex_db_$(DVERSION_HONESTY).sqlite3
	$(PYTHON) code/honesty_extract_exp_data.py

$(GIFTEX_EXP_DATA): code/giftex_extract_exp_data.py \
	data/exp_runs/giftex_otree_$(DVERSION_GIFTEX).csv \
	data/exp_runs/giftex_botex_db_$(DVERSION_GIFTEX).sqlite3
	$(PYTHON) code/giftex_extract_exp_data.py

$(TRUST_EXP_DATA): code/trust_extract_exp_data.py \
	data/exp_runs/trust_otree_$(DVERSION_TRUST).csv \
	data/exp_runs/trust_botex_db_$(DVERSION_TRUST).sqlite3
	$(PYTHON) code/trust_extract_exp_data.py

# The following three recipes are costly to run as they call the
# OpenAI API to classify their data. Also, their results are not
# fully reproducible as they use a non-zero temperature on their 
# calls. 

# Thus, their output is stored in 'static' so that it is committed
# to GitHub. Also, while they depend on .._EXP_DATA,  their recipes 
# are written to depend on the raw experimental data and the data 
# extratction code to avoid that they are triggered after make clean.

$(HONESTY_RATIONALES_DATA): code/honesty_classify_rationales.py \
	code/honesty_extract_exp_data.py \
	data/exp_runs/honesty_otree_$(DVERSION_HONESTY).csv \
	data/exp_runs/honesty_botex_db_$(DVERSION_HONESTY).sqlite3
	$(PYTHON) code/honesty_classify_rationales.py

$(GIFTEX_RATIONALES_DATA): code/giftex_classify_rationales.py \
	code/giftex_extract_exp_data.py \
	data/exp_runs/giftex_otree_$(DVERSION_TRUST).csv \
	data/exp_runs/giftex_botex_db_$(DVERSION_TRUST).sqlite3
	$(PYTHON) code/giftex_classify_rationales.py

$(TRUST_RATIONALES_DATA): code/trust_classify_rationales.py \
	code/trust_extract_exp_data.py \
	data/exp_runs/trust_otree_$(DVERSION_TRUST).csv \
	data/exp_runs/trust_botex_db_$(DVERSION_TRUST).sqlite3
	$(PYTHON) code/trust_classify_rationales.py


# --- Output recipes -----------------------------------------------------------

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
	$(RESULT_OBJECTS_CODE) \
	docs/_quarto.yml \
	docs/results_main.qmd
	quarto render docs/results_main.qmd --quiet
	rm -rf output/results_main_files

$(PRESENTATION):  $(HONESTY_EXP_DATA) $(TRUST_EXP_DATA) $(GIFTEX_EXP_DATA) \
	$(RESULT_OBJECTS_CODE) \
	docs/_quarto.yml \
	docs/presentation.qmd
	quarto render docs/presentation.qmd --quiet
	rm -rf output/presentation_files

$(RESULTS_RATIONALES): $(HONESTY_RATIONALES_DATA) $(GIFTEX_RATIONALES_DATA) \
	$(TRUST_RATIONALES_DATA)  \
	docs/_quarto.yml \
	docs/results_rationales.qmd
	quarto render docs/results_rationales.qmd --quiet
	rm -rf output/results_rationales_files

$(EVANS_COMPARISON): $(HONESTY_EXP_DATA) data/external/evans_et_al_plot.csv \
	code/honesty_create_result_objects.R \
	docs/_quarto.yml \
	docs/evans_et_al_comparison.qmd
	quarto render docs/evans_et_al_comparison.qmd --quiet
	rm -rf output/evans_et_al_comparison_files

$(OA_TRUST_EXAMPLE): data/exp_runs/trust_appendix_example.sqlite3 \
	docs/_quarto.yml \
	docs/materials/word_reference_doc.docx \
	docs/online_appendix_trust_example.qmd
	quarto render docs/online_appendix_trust_example.qmd --quiet
	rm -rf output/online_appendix_trust_example_files
	
$(R_FIGURES): $(HONESTY_EXP_DATA) $(GIFTEX_EXP_DATA) $(TRUST_EXP_DATA) \
	$(RESULT_OBJECTS_CODE) code/render_figures.R
	$(RSCRIPT) code/render_figures.R

# Pattern rule to render tex figures to svg
output/%.svg: docs/%.tex
	$(PDFLATEX) -output-directory=output $< >/dev/null
	$(INKSCAPE) --export-type=svg output/$*.pdf
	rm -f output/$*.pdf output/$*.aux output/$*.log output/$*.synctex.gz


# --- Export recipes -----------------------------------------------------------

$(STATIC): $(RESULTS_MAIN) $(PRESENTATION)
	cp $(RESULTS_MAIN) static/
	cp $(PRESENTATION) static/

	
