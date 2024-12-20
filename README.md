# accframe: Using Large Language Models to Explore Contextualization Effects in Economics-Based Accounting Experiments

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/joachim-gassen/accframe)
[![Open in VS Code Dev Container](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/joachim-gassen/accframe)


This is the code and data repository to the paper:

> Fikir Worku Edossa, Joachim Gassen, and Victor S. Maas (2024): Using Large Language Models to Explore Contextualization Effects in Economics-Based Accounting Experiments. [SSRN Working Paper](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4891763).

## Idea

We study how large language models (LLMs) react on business context framing in classic economics-based accounting experiments. Similar to other applied fields, experiments in the area of accounting, while building on economic or psychological theories, regularly feature context framing, often without hypothesizing or even discussing its effects on the experimental findings. As an emerging literature indicates that LLMs show behavior in experimental settings that is similar to humans while being sensitive to framing, we use these models to assess the context framing effects in seminal economics-based accounting studies. 


## Setup

This repository contains the code to run the LLM-based experiments outlined in the paper and also the experimental data collected from these runs. The 'botex' python package that facilitates the use of LLMs as oTree participants is [here](https://github.com/joachim-gassen/botex). A walk-through for the package, documenting how you can use it on your own oTree exercises, is available [here](https://github.com/botex_experiments/).

The oTree experiments conducted are implemented by using oTree and the raw data of the experimental runs are in `data/exp_runs`. The current output of the code is available in the `static` folder of this repo.

## Reproducing the results of the paper

To reproduce the results of the paper, you need to follow these steps:

1. Start a GitHub Codespace by clicking on the badge at the top of this README. You can do this if you have a GitHub account. This will open a Cloud-based computing environment with all the necessary files and packages installed. If you would rather use local containerized development environment, you can click on the second badge to open the repository in a VS Code Dev Container.
2. Open a terminal in whatever environment you chose and run the following commands:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -v "botex==0.1.0"
# ignore the warning of dependency missmatch
make all
```

3. The `make all` will create the pretest power analyses and all analyses presented in the paper. The main output files will be stored in the `static` folder and additional output files can be found in the `output` folder.

## Running the Experiments

To replicate our experiments, you need to follow these steps in a local development environment:

1. Set up a virtual environment and install the required packages with something like

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# If you want to reproduce our results, 
# you need to install the 0.1.0 version of the botex package
pip install -v "botex==0.1.0"
# otherwise, you can install the botex package from its repository
pip install git+https://github.com/joachim-gassen/botex.git
# if you have cloned the botex repository, you can also install it locally
pip install -e ../botex
# You might run into some dependency issues as oTree has some older dependencies.
# It seems to work regardless, though.
```

2. Make sure that you have provided your OpenAI key in the `secrets.env` file.
3. The code to run the experiments is in the files `run_{honesty|trust|giftex}_exp.py`. You can adjust the number of participants for each condition in these files.
4. Prior to sourcing any of these files, make sure that you do not have a local oTree server running as the code will start a new one.
5. Run `make cleandb` to remove the existing oTree and botex databases (backup your data first if need be).
6. Source the respective code file to run the experiments. While it runs, you can monitor the progress in the console output and by accessing your local oTree instance at http://localhost:8000. After the experiment has finished, you can find the botex data in the `data/exp_runs` folder.
7. Export the oTree data by selecting `Data/All Apps/Plain` in the oTree admin interface. Move the downloaded file to the `data/exp_runs` folder, following the naming convention `{honesty|trust|giftex}_otree_yyyy-mm-dd.csv`.
8. After adjusting the raw data file names in the code. source the file `code/extract_{honesty|trust|giftex}_data.py` to extract the data from the botex and oTree databases. The extracted data will be stored in the `data/generated` folder.
9. You can now run the preregistered analyses by sourcing `code/{honesty|trust|giftex}_prereg_analysis.py`.  
