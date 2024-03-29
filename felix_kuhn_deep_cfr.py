# Copyright 2019 DeepMind Technologies Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Python Deep CFR example."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import app
from absl import flags
from absl import logging
import six

import tensorflow.compat.v1 as tf

from open_spiel.python import policy
from open_spiel.python.algorithms import felix_deep_cfr as deep_cfr
from open_spiel.python.algorithms import expected_game_score
from open_spiel.python.algorithms import exploitability
import pyspiel
from matplotlib import pyplot as plt
import numpy as np

# Temporarily disable TF2 behavior until we update the code.
tf.disable_v2_behavior()

FLAGS = flags.FLAGS
#TODO: always let the number of iterations be a multiple of 10!
flags.DEFINE_integer("num_iterations", 20, "Number of iterations")
flags.DEFINE_integer("num_traversals", 40, "Number of traversals/games")
flags.DEFINE_string("kuhn_game_name", "kuhn_poker", "Name of the game")
flags.DEFINE_string("leduc_game_name", "leduc_poker", "Name of the game")

def main(unused_argv):
  logging.info("Loading %s", FLAGS.kuhn_game_name)
  game = pyspiel.load_game(FLAGS.kuhn_game_name)
  with tf.Session() as sess:
    deep_cfr_solver = deep_cfr.DeepCFRSolver(
        sess,
        game,
        policy_network_layers=(16,),
        advantage_network_layers=(16,),
        num_iterations=FLAGS.num_iterations,
        num_traversals=FLAGS.num_traversals,
        learning_rate=1e-3,
        batch_size_advantage=128,
        batch_size_strategy=1024,
        memory_capacity=1e7,
        policy_network_train_steps=400,
        advantage_network_train_steps=20,
        reinitialize_advantage_networks=False)
    sess.run(tf.global_variables_initializer())
    _, advantage_losses, policy_loss, nash_kuhn, expl_kuhn = deep_cfr_solver.solve()
    for player, losses in six.iteritems(advantage_losses):
      logging.info("Advantage for player %d: %s", player,
                   losses[:2] + ["..."] + losses[-2:])
      logging.info("Advantage Buffer Size for player %s: '%s'", player,
                   len(deep_cfr_solver.advantage_buffers[player]))
    logging.info("Strategy Buffer Size: '%s'",
                 len(deep_cfr_solver.strategy_buffer))
    logging.info("Final policy loss: '%s'", policy_loss)

    average_policy = policy.tabular_policy_from_callable(
        game, deep_cfr_solver.action_probabilities)
    conv = exploitability.nash_conv(game, average_policy)
    logging.info("Deep CFR in '%s' - NashConv: %s", FLAGS.kuhn_game_name, conv)

    average_policy_values = expected_game_score.policy_value(
        game.new_initial_state(), [average_policy] * 2)





  logging.info("Loading %s", FLAGS.leduc_game_name)
  game = pyspiel.load_game(FLAGS.leduc_game_name)
  with tf.Session() as sess:
    deep_cfr_solver = deep_cfr.DeepCFRSolver(
        sess,
        game,
        policy_network_layers=(16,),
        advantage_network_layers=(16,),
        num_iterations=FLAGS.num_iterations,
        num_traversals=FLAGS.num_traversals,
        learning_rate=1e-3,
        batch_size_advantage=128,
        batch_size_strategy=1024,
        memory_capacity=1e7,
        policy_network_train_steps=400,
        advantage_network_train_steps=20,
        reinitialize_advantage_networks=False)
    sess.run(tf.global_variables_initializer())
    _, advantage_losses, policy_loss, nash_leduc, expl_leduc = deep_cfr_solver.solve()
    for player, losses in six.iteritems(advantage_losses):
      logging.info("Advantage for player %d: %s", player,
                   losses[:2] + ["..."] + losses[-2:])
      logging.info("Advantage Buffer Size for player %s: '%s'", player,
                   len(deep_cfr_solver.advantage_buffers[player]))
    logging.info("Strategy Buffer Size: '%s'",
                 len(deep_cfr_solver.strategy_buffer))
    logging.info("Final policy loss: '%s'", policy_loss)

    average_policy = policy.tabular_policy_from_callable(
        game, deep_cfr_solver.action_probabilities)
    conv = exploitability.nash_conv(game, average_policy)
    logging.info("Deep CFR in '%s' - NashConv: %s", FLAGS.leduc_game_name, conv)

    average_policy_values = expected_game_score.policy_value(
        game.new_initial_state(), [average_policy] * 2)
  
 
  nash_kuhn = np.array(nash_kuhn)
  expl_kuhn = np.array(expl_kuhn)
  nash_leduc = np.array(nash_leduc)
  expl_leduc = np.array(expl_leduc)
  x_kuhn = np.arange(start=0, stop=len(nash_kuhn)*10, step=10)
  x_leduc = np.arange(start=0, stop=len(nash_leduc)*10, step=10)
  fig=plt.figure()
  plt.xlabel("Iteration")
  plt.ylabel("NashConv")
  plt.title('NashConv of deep_cfr for Kuhn and Leduc Poker')
  ax=fig.add_subplot(111)
 
  ax.plot(x_kuhn,expl_kuhn,label='Exploitability Kuhn Poker')
  ax.plot(x_leduc,expl_leduc,label='Exploitability Leduc Poker')
  ax.plot(x_kuhn,nash_kuhn,label='NashConv Kuhn Poker', linestyle='dashed')
  ax.plot(x_leduc,nash_leduc,label='NashConv Leduc Poker', linestyle='dashed')
  plt.legend(loc=2)
  plt.show()

if __name__ == "__main__":
  app.run(main)
