# Copyright 2018 Google LLC
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
# =============================================================================
"""Test for the MNIST model."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os
import shutil
import tempfile
import unittest

import numpy as np

from scripts import mnist


class MnistTest(unittest.TestCase):

  def setUp(self):
    self._tmp_dir = tempfile.mkdtemp()
    super(MnistTest, self).setUp()

  def tearDown(self):
    if os.path.isdir(self._tmp_dir):
      shutil.rmtree(self._tmp_dir)
    super(MnistTest, self).tearDown()

  def _getFakeMnistData(self):
    """Generate some fake MNIST data for testing."""
    input_shape = (28, 28, 1)
    x_train = np.random.rand(100, 28, 28, 1)
    y_train = np.random.rand(100, 10)
    x_test = np.random.rand(10, 28, 28, 1)
    y_test = np.random.rand(10, 10)
    return input_shape, x_train, y_train, x_test, y_test

  def testTrainWithFakeDataAndSave(self):
    model_json_path = os.path.join(self._tmp_dir, 'mnist.keras.model.json')
    weights_json_path = os.path.join(self._tmp_dir, 'mnist.keras.weights.json')
    merged_json_path = os.path.join(self._tmp_dir, 'mnist.keras.merged.json')
    input_shape, x_train, y_train, x_test, y_test = self._getFakeMnistData()
    mnist.train(
        input_shape, x_train, y_train, x_test, y_test, 2, 5,
        model_json_path, weights_json_path, merged_json_path)

    # Check that the model json file is created.
    json.load(open(model_json_path, 'rt'))

    # Check that the weights json file is created.
    json.load(open(weights_json_path, 'rt'))

    # Check that the merged json file is created.
    json.load(open(merged_json_path, 'rt'))


if __name__ == '__main__':
  unittest.main()
