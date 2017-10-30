# I absolutely hate this sys path stuff
import sys
sys.path.append(sys.path[0] + "/..")

import chess
import os
import numpy as np
import pandas as pd
import tensorflow as tf
import pychess_utils as util
from tensorflow.contrib.learn.python.learn.datasets import base

# Less Verbose Output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.logging.set_verbosity(tf.logging.ERROR)

DATA_DIR = "/Users/evanmdoyle/Programming/ChessAI/DerivedData/complete/full_dataset/csv"

feature_columns = []

def gen_feature_columns():
	for x in range(64):
		feature_columns[x] = tf.feature_column.numeric_column("o_h_"+str(x))
	for y in range(64):
		feature_columns[64+y] = tf.feature_column.numeric_column("d_h_"+str(y))
	return feature_columns

def input_fn(data_file, target="label", num_epochs, feature_columns, batch_size=30, shuffle=False, num_threads=4):
	dataset = pd.read_csv(
        tf.gfile.Open(data_file),
        header=0,
        usecols=feature_columns + [target],
        skipinitialspace=True,
        engine="python")
    # Drop NaN entries
    dataset.dropna(how="any", axis=0)

    # Init empty dataframe, add column for each of targets
    labels = pd.DataFrame(columns=[target])

    # TODO: This is where I need to process the labels, depends completely on expected output
    labels[target] = dataset[target].apply(lambda x: x in constants.USER).astype(int)
    dataset.pop(target)
    
    return tf.estimator.inputs.numpy_input_fn(
        x={"x": np.array(dataset)},
        # TODO: Here I used one_hot from utils for classification, now depends also on expected output
        y=np.array(labels[target]),
        batch_size=batch_size,
        num_epochs=num_epochs,
        shuffle=shuffle,
        num_threads=1)

# NOTE: This is a hacky solution due to the following issue:
# the tf.layers weights are called dense_[number]/kernel:0
# but while tf.GraphKeys.TRAINABLE_VARIABLES records dense/kernel:0, dense_1/kernel:0...
# layer.name for some reason records dense/kernel:0, dense_2/kernel:0...
# So I need to decrement the number on the end of 'dense' if there is one.
def extract_weights(layer):
    name = os.path.split(layer.name)[0]
    if '_' in name:
        number = str(int(name[name.find('_')+1:]) - 1)
        name = name[:name.find('_')] + '_' + number
    for variable in tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES):
        if variable.name == name + '/kernel:0':
            return variable
    return None

def model_fn(features, labels, mode, params):
    
    # 1. Configure the model via TensorFlow operations
    input_layer = tf.cast(features["x"], tf.float32)
    
    beta = params["beta"]
    layer_sizes = params["hidden_layers"]
    current_tensor = input_layer
    regularizer = tf.contrib.layers.l2_regularizer(beta)
    weights = []
    for nodes in layer_sizes:
        current_tensor = tf.layers.dense(current_tensor, nodes, activation=tf.nn.tanh,
            kernel_regularizer=regularizer)
        weights.append(extract_weights(current_tensor))


    # TODO: the output layer determines a bunch of other stuff 
    output_layer = tf.layers.dense(current_tensor, 2, activation=tf.nn.tanh)

    # 4. Generate predictions
    predictions = output_layer

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(
            mode=mode,
            predictions={"move": predictions})
    
    # 2. Define the loss function for training/evaluation
    # TODO: the loss function is dependent on the output layer
    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=predictions, labels=labels))
    reg_variables = tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES)
    reg_term = tf.contrib.layers.apply_regularization(regularizer, reg_variables)
    loss += reg_term
    loss = tf.divide(loss, tf.constant(len(params["hidden_layers"]), tf.float32))

    eval_metric_ops = {
        "rmse": tf.metrics.root_mean_squared_error(tf.cast(labels,tf.float64), tf.cast(predictions,tf.float64)),
        "accuracy": tf.metrics.accuracy(
            tf.cast(tf.argmax(labels,1), tf.float64), tf.cast(tf.argmax(predictions,1), tf.float64))
    }
    
    # 3. Define the training operation/optimizer
    # Decaying learning rate might be unnecessary unless a local minima is found quickly
    decay_steps = 100000
    learning_rate = tf.train.polynomial_decay(params["start_learn"], tf.train.get_global_step(),
                                          decay_steps, params["end_learn"],
                                          power=0.5)
    optimizer=tf.train.GradientDescentOptimizer(
        learning_rate=learning_rate)
    train_op = optimizer.minimize(loss=loss, global_step=tf.train.get_global_step())
    
    # 5. Return predictions/loss/train_op/eval_metric_ops in EstimatorSpec object
    return tf.estimator.EstimatorSpec(mode, predictions, loss, train_op, eval_metric_ops)


