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

"""Example use of the CFR algorithm on Kuhn Poker."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import app
from absl import flags

from open_spiel.python.algorithms import cfr
from open_spiel.python.algorithms import exploitability
import pyspiel
from matplotlib import pyplot as plt
import numpy as np

FLAGS = flags.FLAGS

flags.DEFINE_integer("iterations", 2, "Number of iterations")
flags.DEFINE_string("kuhn_game", "kuhn_poker", "Name of the game")
flags.DEFINE_string("leduc_game", "leduc_poker", "Name of the game")
flags.DEFINE_integer("players", 2, "Number of players")
flags.DEFINE_integer("print_freq", 10, "How often to print the exploitability")


def main(_):
  game = pyspiel.load_game(FLAGS.kuhn_game,
                           {"players": pyspiel.GameParameter(FLAGS.players)})
  cfr_solver = cfr.CFRSolver(game) 
  expl_kuhn = []
  nash_kuhn = []
  x_kuhn = []
  for i in range(FLAGS.iterations):
    print(i)
    cfr_solver.evaluate_and_update_policy()
    expl = exploitability.exploitability(game, cfr_solver.average_policy())
    expl_kuhn.append(expl)
    conv = exploitability.nash_conv(game, cfr_solver.average_policy())
    nash_kuhn.append(conv)
    x_kuhn.append(i)
    
  game = pyspiel.load_game(FLAGS.leduc_game,
                           {"players": pyspiel.GameParameter(FLAGS.players)})
  cfr_solver = cfr.CFRSolver(game) 
  expl_leduc = []
  nash_leduc = []
  for i in range(FLAGS.iterations):
    print(i)
    cfr_solver.evaluate_and_update_policy()
    expl = exploitability.exploitability(game, cfr_solver.average_policy())
    expl_leduc.append(expl)
    conv = exploitability.nash_conv(game, cfr_solver.average_policy())
    nash_leduc.append(conv)  
    

  nash_kuhn = np.array(nash_kuhn)  
  expl_kuhn = np.array(expl_kuhn)
  x_kuhn = np.array(x_kuhn) 
  expl_leduc = np.array(expl_leduc) 
  nash_leduc = np.array(nash_leduc)
  

  x_leduc = np.array(x_kuhn)
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
