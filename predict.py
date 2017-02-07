#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np

# Similarly to the example in: https://www.tensorflow.org/tutorials/tflearn/
# we create a model and test on our own TSA Baggage Claims data.

# separated train and test files from MapR-FS
TRAIN = "/mapr/demo.mapr.com/cd/claims_train.csv"
TEST = "/mapr/demo.mapr.com/cd/claims_test.csv"
MODEL_DIR = "/mapr/demo.mapr.com/cd/model"

# load the data sets
training_set = tf.contrib.learn.datasets.base.load_csv_with_header(
    filename=TRAIN,
    target_dtype=np.int,
    features_dtype=np.float32)
test_set = tf.contrib.learn.datasets.base.load_csv_with_header(
    filename=TEST,
    target_dtype=np.int,
    features_dtype=np.float32)

dim = len(training_set.data[0])
feature_columns = [tf.contrib.layers.real_valued_column("", dimension=dim)]

# make a 3-layer DNN 
classifier = tf.contrib.learn.DNNClassifier(feature_columns=feature_columns,
                                            hidden_units=[512, 256, 128], 
                                            n_classes=2,
                                            model_dir=MODEL_DIR)

# fit the model on the training data
classifier.fit(x=training_set.data,
               y=training_set.target,
               steps=100)
 
# print an accuracy report
acc = classifier.evaluate(x=test_set.data,
                          y=test_set.target)['accuracy']
print('accuracy: %2.2f' % acc)
