# accframe: Exploring the Effects of Contextualization in Economics-Based Accounting Experiments with Large Language Models

## Idea

We study how large language models (LLMs) react on business context framing in classic economics-based accounting experiments. Similar to other applied fields, experiments in the area of accounting, while building on economic or psychological theories, regularly feature context framing, often without hypothesizing or even discussing its effects on the experimental findings. As an emerging literature indicates that LLMs show behavior in experimental settings that is similar to humans while being sensitive to framing, we use these models to assess the context framing effects in seminal economics-based accounting studies. 


## Setup

This repository contains the code to run the LLM-based experiments outlined in the paper and also the experimental data collected from these runs. The 'botex' python package that facilitates the use of LLMs as oTree participants is [here](https://github.com/joachim-gassen/botex). 

The oTree experiments conducted are implemented by using oTree and the raw data of the experimental runs are in `data/exp_runs`. The current output of the code is available in the `static` folder of this repo.

If you are interested in reproducing these output documents your best bet would be to use [GitHub Codespaces](https://github.com/features/codespaces). These are the steps that you need to take:

1. Create a GitHub codespace on main.
2. Run `git clone https://github.com/joachim-gassen/botex ../botex` in the terminal to clone the botex repo locally. 
3. Copy `_secrets.env` to `secrets.env` and add your OpenAI key 
4. Run `make all` to create the output. Rendering the appendix also requires running a one-round two players trust game involving two bots. You can observe this process by monitoring the console logging during the make process.


## Running the Experiments

To replicate our experiments, you need to follow these steps:

1. Make sure that you have provided your OpenAI key in the `secrets.env` file.
2. The code to run the experiments is in the files `run_{honesty|trust|giftex}_exp.py`. You can adjust the number of participants for each condition in these files.
3. Prior to sourcing any of these files, make sure that you do not have a local oTree server running as the code will start a new one.
4. Run `make cleandb` to remove the existing oTree and botex databases (backup your data first if need be).
5. Source the respective code file to run the experiments. While it runs, you can monitor the progress in the console output and by accessing your local oTree instance at http://localhost:8000. After the experiment has finished, you can find the botex data in the `data/exp_runs` folder.
7. Export the oTree data by selecting `Data/All Apps/Plain` in the oTree admin interface. Move the downloaded file to the `data/exp_runs` folder, following the naming convention `{honesty|trust|giftex}_otree_yyyy-mm-dd.csv`.
8. After adjusting the raw data file names in the code. source the file `code/extract_{honesty|trust|giftex}_data.py` to extract the data from the botex and oTree databases. The extracted data will be stored in the `data/generated` folder.
9. You can now run the preregistered analyses by sourcing `code/{honesty|trust|giftex}_prereg_analysis.py`.  
