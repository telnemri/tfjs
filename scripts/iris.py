# Copyright 2018 Google LLC
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
# =============================================================================
"""Train a simple model for the Iris dataset; Export the model and weights."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import json
import os

import h5py
import keras
import numpy as np

from scripts import iris_data
from scripts import h5_conversion


def train(epochs,
          model_json_path,
          weights_json_path,
          merged_json_path,
          sequential=False):
  """Train a Keras model for Iris data classification and save result as JSON.

  Args:
    epochs: Number of epochs to traing the Keras model for.
    model_json_path: Path to save the JSON configuration of the trained Keras
      model at.
    weights_json_path: Path to save the JSON serialization of the weights in the
      trained Keras model at.
    merged_json_path: Path to save the JSON serialization of the model + weights
      in the trained Keras model at.
    sequential: Whether to use a Keras Sequential model, instead of the default
      functional model.

  Returns:
    Final classification accuracy on the training set.
  """
  data_x, data_y = iris_data.load()

  if sequential:
    model = keras.models.Sequential()
    model.add(keras.layers.Dense(
        10, input_shape=[data_x.shape[1]], use_bias=True, activation='sigmoid',
        name='Dense1'))
    model.add(keras.layers.Dense(
        3, use_bias=True, activation='softmax', name='Dense2'))
  else:
    iris_x = keras.layers.Input((4,))
    dense1 = keras.layers.Dense(
        10, use_bias=True, name='Dense1', activation='sigmoid')(iris_x)
    dense2 = keras.layers.Dense(
        3, use_bias=True, name='Dense2', activation='softmax')(dense1)
    # pylint:disable=redefined-variable-type
    model = keras.models.Model(inputs=[iris_x], outputs=[dense2])
    # pylint:enable=redefined-variable-type
  model.compile(loss='categorical_crossentropy', optimizer='adam')

  model.fit(data_x, data_y, batch_size=8, epochs=epochs)

  # Run prediction on the training set.
  pred_ys = np.argmax(model.predict(data_x), axis=1)
  true_ys = np.argmax(data_y, axis=1)
  final_train_accuracy = np.mean((pred_ys == true_ys).astype(np.float32))
  print('Accuracy on the training set: %g' % final_train_accuracy)

  merged_model_h5_path = merged_json_path + '.h5'
  keras.models.save_model(model, merged_model_h5_path)
  with open(merged_json_path, 'wt') as f:
    f.write(json.dumps(
        h5_conversion.HDF5Converter().h5_merged_saved_model_to_json(
            merged_model_h5_path)))
  os.remove(merged_model_h5_path)
  print('Saved save_model (model + weights) at %s' % merged_json_path)

  with open(model_json_path, 'wt') as f:
    f.write(model.to_json())
  print('Saved topology at: %s' % model_json_path)

  weights_h5_path = weights_json_path + '.h5'
  model.save_weights(weights_h5_path)
  with open(weights_json_path, 'wt') as f:
    f.write(json.dumps(
        h5_conversion.HDF5Converter().h5_weights_to_json(
            h5py.File(weights_h5_path))))
  os.remove(weights_h5_path)
  print('Saved weights at: %s' % weights_json_path)

  return final_train_accuracy


def main():
  train(FLAGS.epochs,
        FLAGS.model_json_path,
        FLAGS.weights_json_path,
        FLAGS.merged_json_path,
        sequential=FLAGS.sequential)


if __name__ == '__main__':
  parser = argparse.ArgumentParser('Iris model training and serialization')
  parser.add_argument(
      '--sequential',
      action='store_true',
      help='Use a Keras Sequential model, instead of the default functional '
      'model.')
  parser.add_argument(
      '--epochs',
      type=int,
      default=100,
      help='Number of epochs to train the Keras model for.')
  parser.add_argument(
      '--model_json_path',
      type=str,
      default='/tmp/iris.keras.model.json',
      help='Local path for the Keras model definition JSON file.')
  parser.add_argument(
      '--weights_json_path',
      type=str,
      default='/tmp/iris.keras.weights.json',
      help='Local path for the Keras model weights JSON file.')
  parser.add_argument(
      '--merged_json_path',
      type=str,
      default='/tmp/iris.keras.merged.json',
      help='Local path for the Keras model topology & weights JSON file.')

  FLAGS, _ = parser.parse_known_args()
  main()
