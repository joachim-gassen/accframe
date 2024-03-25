# accframe: Exploring Accounting Framing Effects with Large Language Models

## Idea

We study how large language models (LLMs) react on accounting context framing in classic accounting experiments. Similar to other applied fields, experiments in the area of accounting, while building on economic or psychological theories, regularly feature context framing, often without hypothesizing or even discussing its effects on the experimental findings. As an emerging literature indicates that LLMs are very sensitive to framing, we use these models to assess the context framing effects in seminal accounting studies. Our findings show that these framing effects are often predictable based on common perceptions of the accounting profession and can be large in magnitude. We hypothesize that the observed LLM framing effects are more descriptive for human behavior of general participants, which have perceptions about accountants that are relatively close to those reflected in LLMs, relative to specialized participants with an accounting background, as these participants have perceptions on the accounting profession that only partly overlap with the general public.

## Setup

This repository contains the code to run the LLM-based experiments outlined in the paper and also the experimental data collected from these runs. The 'botex' python package that facilitates the use of LLMs as oTree participants is [here](https://github.com/joachim-gassen/botex). 

The oTree experiments conducted are in `otree` and the raw data of the experimental runs are in `data/exp_runs`. The current output of the code is available in the `static` folder of this repo.

If you are interested in reproducing these output documents (currently only a short presentation) and have [quarto](https://quarto.org), Python, R, and a make environment installed, you might be able to produce the output by running `make all` in the project's root directory. The output will be generated in the `output` folder.

## Todos

- [ ] Decide on accounting studies to LLM-replicate with and without context framing.
- [ ] Submit a proposal to the [ENEAR conference](https://sites.google.com/view/enearonline/2024-conference)
- [ ] Write a short and potentially more technical draft not containing any human experiments before the workshop so that we can take this public.  
