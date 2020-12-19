# README #

## The Problem ##

Scientific data collection is expensive and time consuming.  How can AI help scientists collect data more efficiently?  In this repository we present a framework where AI systems work together with human scientists to ensure data collection is directed more efficiently to scientifically interesting regions.


## What's Here ##

This repo contains the source code for simulating our proposed Human-in-the-Loop data collection process.

Specifically, the codebase contains three main entities that interact in the context of a one-dimensional scientific data collection problem.  First, an **AI agent**, which selects x-values at which to gather samples: we include several algorithms, from simple round-robin baselines to more complex approaches.  Next a stochastic **environment**, which stochastically generates y-values for each chosen x-value, we consider several different environments based on real-world data drawn from the domains of cognitive psychology, behavioral economics, and mental health.  Finally, a **simulated human user**, which places keypoints to indicate  to the AI what regions are scientifically interesting, we consider several different simulated users, such as users looking for values close to some target, users looking for critical points, etc.


  Further details can be found in the following paper:  ["AI-Assisted Scientific Data Collection with Iterative Human Feedback"](http://datadrivengame.science/aaai21).

  If you find this code useful, please cite our paper:
  ```
  @inproceedings{mandel2021ai,
      title={AI-Assisted Scientific Data Collection with Iterative Human Feedback},
      author={Mandel, Travis and Boyd, James and Carter, Sebastian J and Tanaka, Randall H and Nammoto, Taishi},
      booktitle={AAAI},
      year={2021}
    }
  ```


### Visualizing The Graphs ###

The repo is set up to allow you to recreate the simulation results from our paper and display the associated simulation graphs.

If you just want to generate the graphs from the saved `allResults.json` data that is already in this repo, please run this command:

`python3.7 graphsFromSave.py`

### Running the Simulations ###

To run the full simulation and regenerate `allResults.json` (note: takes 6-8 hours):

`python3.7 graphs.py`

* Once it's done, run `python3.7 graphsFromSave.py` to generate the graphs.


### Specifications ###

* numpy version '1.18.5'
* matplotlib version '3.2.1'
* python version 3.7+

### Brief File Descriptions  ###

* `graphs.py` This is the core logic which runs all the simulations and generates an `allResults.json` file which can be visualized using `graphsFromSave.py`.
* `allResults.json` contains sample results from running graphs.py to completion, which can take 6-8 hours.
* `graphsFromSave.py` This file loads the `allResults.json` file generated by `graphs.py` and generates the graph files
* `aiSampler.py` This contains code for all the AIs, such as TESA, epsilon-greedy, etc.
* `humanSampler.py` This contains code for all the simulated users, specifying various methods of keypoint placement, etc.
* `environments.py` This contains code that loads the preprocessed data (from the Data/ folder) and represents it as an environment with which the AI can interact
* `evaluators.py` This contains code used to evaluate the various algorithms.
* `visualizers.py` This contains code used to generate the three visualization functions from data.
* `distributions.py` This contains helper code for various probability distributions
* `statsTrack.py` This contains helper code to efficiently track statistics during the run of the simulations
* `cheater.py` A simple interface to clearly declare which AIs get to see the true info and which must learn
* `utilities.py` Miscellaneous utilities, often used in multiple places throughout the code
* `Data/` This folder contains a subfolder for each of the three domains listed in the paper. For each one we provide the raw dataset, the python file used to process it, and the processed JSON dataset.

### Data Sources ###

* [Economics](https://www.kaggle.com/neuromusic/avocado-prices)
* [Mental Health](https://www.kaggle.com/osmi/mental-health-in-tech-2016)
* [Cognitive psychology](https://www.psychdata.de/index.php?main=search&sub=browse&id=pdpr99ve20&lang=eng)



