# AlphaChess Zero

[This paper](https://www.nature.com/articles/nature24270.epdf?author_access_token=VJXbVjaSHxFoctQQ4p2k4tRgN0jAjWel9jnR3ZoTv0PVW4gB86EEpGqTRDtpIz-2rmo8-KG06gqVobU5NSCFeHILHcVFUeMsbvwS-lxjqQGg98faovwjxeTUgZAUMnRQ) details the methods used in creating the world champion Go AI 
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
