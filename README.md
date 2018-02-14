# AlphaChess Zero
### Re-Implementing AlphaGo Zero for Chess

[This paper from Google DeepMind](https://www.nature.com/articles/nature24270.epdf?author_access_token=VJXbVjaSHxFoctQQ4p2k4tRgN0jAjWel9jnR3ZoTv0PVW4gB86EEpGqTRDtpIz-2rmo8-KG06gqVobU5NSCFeHILHcVFUeMsbvwS-lxjqQGg98faovwjxeTUgZAUMnRQ) details the methods used in creating the world champion Go AI 
"AlphaGo Zero".  AGZ uses exclusively self-play reinforcement learning (not
requiring any existing games to learn from) by cleverly combining a guided 
Monte Carlo Tree Search with a Deep Convolutional Neural Network.

The key components of AlphaGo Zero are arranged in a 3 stage pipeline, with
each component feeding into the next.  These components are:

1. Self-Play Data Generation
2. Neural Network Training
3. Player Evaluation

First, the best performing Neural Network seen so far powers an MCTS player
which plays itself thousands of times and generates training data.  Then,
the current NN is trained on the data using the statistics of the MCTS as ground
truth labels.  This new iteration of the NN plays against the current best NN.
After playing 400 matches, if the new NN wins over 55% of the matches, it will
become the new best player and will be used for future self-play data generation.

I am using the paper's explanation to guide me in re-implementing this approach
for Chess instead of Go.  While if one had access to the code of AlphaGo Zero my
modifications would be easy to implement, my goal in recreating the entire pipeline
is to become familiar with the process of constructing a production-grade machine-learning
algorithm.

### Using this repository

Requirements:
  - You must use [TensorFlow Serving](https://www.tensorflow.org/serving/serving_basic) to serve the model
  - You'll need the python-chess and tensorflow packages installed
  
Configuration:
  - Specify the address and port number at which the ACZ model is being served in `address.txt` and `port.txt`
  - Run `python scripts/init_self_play.py` to create your `self_play.csv` file with header for training
  - Set `GAME_BATCH_SIZE` in `self_play.py` to the number of games you want to play per run of the file
  - Set the number of training steps to run in `train.py`

Usage:
  
```
// Runs GAME_BATCH_SIZE games between ACZ and itself, records the training data in ACZData/self_play.csv
python self_play.py
// Runs your specified number of training steps on the data and exports the model to a new version
python train.py
```
  
After `train.py` exports a new version, you can potentially run `player_eval.py`.
  
This will require:
  - The current best known model number in `best_version.txt`
  - Two models being served simultaneously: the best known model version and the latest model version
    
Then, you can run:
```
python player_eval.py
```
  
This will pit the best version vs. the latest version of ACZ and update `best_version.txt` to the latest's model number
if and only if the latest wins 55% of the games.
  
And repeat!
  
### HUGE Disclaimer

This model is very large. The input layer is 13 layers of chess boards (1 for each piece on each team plus a constant plane
of 1s or 0s to indicate the turn, so 8x8x13 total input nodes), and the output layer is every possible move from every
possible square, including pawn (under-)promotions (this is 8x8x73 nodes). There are many layers between, and in fact I have
reduced the number of residual layers from 19 as described in the original paper to only 2 (this can be changed in
`models/version2.py`).

For this reason, I have never been able to train this model to any noticeable increase over baseline :(

Pretty lame, but I did get a fancy GTX 1080 to run on instead of a Macbook, so maybe there is hope. If you have access to
lots of computing power then give it a go!
