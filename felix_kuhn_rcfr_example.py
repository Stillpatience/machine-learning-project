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

"""Example use of the RCFR algorithm on Kuhn Poker."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import app
from absl import flags
import tensorflow.compat.v1 as tf
import numpy as np

from matplotlib import pyplot as plt
from open_spiel.python.algorithms import rcfr
import pyspiel

tf.enable_eager_execution()

FLAGS = flags.FLAGS

flags.DEFINE_integer("iterations", 5, "Number of iterations")
flags.DEFINE_string("kuhn_poker_game", "kuhn_poker", "Name of the game")
flags.DEFINE_integer("players", 2, "Number of players")
flags.DEFINE_integer("print_freq", 1, "How often to print the exploitability")
flags.DEFINE_boolean("bootstrap", False,
                     "Whether or not to use bootstrap targets")
flags.DEFINE_boolean("truncate_negative", False,
                     "Whether or not to truncate negative targets to zero")
flags.DEFINE_integer(
    "buffer_size", -1,
    "A reservoir buffer size. A non-positive size implies an effectively "
    "infinite buffer.")
flags.DEFINE_integer("num_hidden_layers", 1,
                     "The number of hidden layers in the regret model.")
flags.DEFINE_integer("num_hidden_units", 13,
                     "The number of hidden layers in the regret model.")
flags.DEFINE_integer(
    "num_hidden_factors", 8,
    "The number of factors in each hidden layer in the regret model.")
flags.DEFINE_boolean(
    "use_skip_connections", True,
    "Whether or not to use skip connections in the regret model.")
flags.DEFINE_integer(
    "num_epochs", 200,
    "The number of epochs to run between each iterations to update the regret "
    "models.")
flags.DEFINE_integer("batch_size", 100, "The regret model training batch size.")
flags.DEFINE_float("step_size", 0.01, "The ADAM (AMSGrad) optimizer step size.")


def main(_):
  game = pyspiel.load_game(FLAGS.kuhn_poker_game,
                           {"players": pyspiel.GameParameter(FLAGS.players)})

  models = []
  for _ in range(game.num_players()):
    models.append(
        rcfr.DeepRcfrModel(
            game,
            num_hidden_layers=FLAGS.num_hidden_layers,
            num_hidden_units=FLAGS.num_hidden_units,
            num_hidden_factors=FLAGS.num_hidden_factors,
            use_skip_connections=FLAGS.use_skip_connections))

  if FLAGS.buffer_size > 0:
    solver = rcfr.ReservoirRcfrSolver(
        game,
        models,
        FLAGS.buffer_size,
        truncate_negative=FLAGS.truncate_negative)
  else:
    solver = rcfr.RcfrSolver(
        game,
        models,
        truncate_negative=FLAGS.truncate_negative,
        bootstrap=FLAGS.bootstrap)

  def _train_fn(model, data):
    """Train `model` on `data`."""
    data = data.shuffle(FLAGS.batch_size * 10)
    data = data.batch(FLAGS.batch_size)
    data = data.repeat(FLAGS.num_epochs)

    optimizer = tf.keras.optimizers.Adam(lr=FLAGS.step_size, amsgrad=True)

    @tf.function
    def _train():
      for x, y in data:
        optimizer.minimize(
            lambda: tf.losses.huber_loss(y, model(x), delta=0.01),  # pylint: disable=cell-var-from-loop
            model.trainable_variables)

    _train()

  # End of _train_fn
  expl_kuhn = []
  nash_kuhn = []
  x_kuhn = []
  for i in range(FLAGS.iterations):
    solver.evaluate_and_update_policy(_train_fn)
    if i % FLAGS.print_freq == 0:
      print(i)
      expl = pyspiel.exploitability(game, solver.average_policy())
      conv = pyspiel.nash_conv(game, solver.average_policy())
      #print("Iteration {} exploitability {}".format(i, conv))
      expl_kuhn.append(expl)
      nash_kuhn.append(conv)
      x_kuhn.append(i)
  
  
  flags.DEFINE_string("leduc_poker_game", "leduc_poker", "Name of the game")
  
  game = pyspiel.load_game(FLAGS.leduc_poker_game,
                           {"players": pyspiel.GameParameter(FLAGS.players)})

  models = []
  for _ in range(game.num_players()):
    models.append(
        rcfr.DeepRcfrModel(
            game,
            num_hidden_layers=FLAGS.num_hidden_layers,
            num_hidden_units=FLAGS.num_hidden_units,
            num_hidden_factors=FLAGS.num_hidden_factors,
            use_skip_connections=FLAGS.use_skip_connections))

  if FLAGS.buffer_size > 0:
    solver = rcfr.ReservoirRcfrSolver(
        game,
        models,
        FLAGS.buffer_size,
        truncate_negative=FLAGS.truncate_negative)
  else:
    solver = rcfr.RcfrSolver(
        game,
        models,
        truncate_negative=FLAGS.truncate_negative,
        bootstrap=FLAGS.bootstrap)

  expl_leduc = []
  x_leduc = []
  nash_leduc = []
  for i in range(FLAGS.iterations):
    solver.evaluate_and_update_policy(_train_fn)
    if i % FLAGS.print_freq == 0:
      print(i)
      expl = pyspiel.exploitability(game, solver.average_policy())
      conv = pyspiel.nash_conv(game, solver.average_policy())
      #print("Iteration {} exploitability {}".format(i, conv))
      expl_leduc.append(expl)
      nash_leduc.append(conv)
      x_leduc.append(i)
  expl_leduc = np.array(expl_leduc)
  x_leduc = np.array(x_leduc)
  
  fig=plt.figure()
  plt.xlabel("Iteration")
  plt.ylabel("NashConv")
  plt.title('NashConv of rcfr for Kuhn and Leduc Poker')
  ax=fig.add_subplot(111)
 
  ax.plot(x_kuhn,expl_kuhn,label='Exploitability Kuhn Poker')
  ax.plot(x_leduc,expl_leduc,label='Exploitability Leduc Poker')
  ax.plot(x_kuhn,nash_kuhn,label='NashConv Kuhn Poker', linestyle='dashed')
  ax.plot(x_leduc,nash_leduc,label='NashConv Leduc Poker', linestyle='dashed')
  plt.legend(loc=2)
  plt.show()

if __name__ == "__main__":
  app.run(main)
