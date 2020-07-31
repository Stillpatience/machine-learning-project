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

"""Example use of the C++ MCCFR algorithms on Kuhn Poker.

This examples calls the underlying C++ implementations via the Python bindings.
Note that there are some pure Python implementations of some of these algorithms
in python/algorithms as well.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import app
from absl import flags

import pyspiel

FLAGS = flags.FLAGS

flags.DEFINE_enum(
    "sampling",
    "external",
    ["external", "outcome"],
    "Sampling for the MCCFR solver",
)
flags.DEFINE_integer("iterations", 50, "Number of iterations")
flags.DEFINE_string("kuhn_game", "kuhn_poker", "Name of the game")
flags.DEFINE_integer("players", 2, "Number of players")
flags.DEFINE_string("leduc_game", "leduc_poker", "Name of the game")

def main(_):
  game = pyspiel.load_game(
      FLAGS.kuhn_game,
      {"players": pyspiel.GameParameter(FLAGS.players)},
  )

  if FLAGS.sampling == "external":
    solver = pyspiel.ExternalSamplingMCCFRSolver(
        game,
        avg_type=pyspiel.MCCFRAverageType.FULL,
    )
  elif FLAGS.sampling == "outcome":
    solver = pyspiel.OutcomeSamplingMCCFRSolver(game)
  expl_kuhn = []
  conv_kuhn = []
  for i in range(FLAGS.iterations):
    solver.run_iteration()
    expl_kuhn.append(pyspiel.exploitability(game, solver.average_policy()))
    conv_kuhn.append(pyspiel.nash_conv(game, solver.average_policy()))
    #print("Iteration {} exploitability: {:.6f}".format(
    #    i, pyspiel.exploitability(game, solver.average_policy())))
        
  game = pyspiel.load_game(
      FLAGS.leduc_game,
      {"players": pyspiel.GameParameter(FLAGS.players)},
  )

  if FLAGS.sampling == "external":
    solver = pyspiel.ExternalSamplingMCCFRSolver(
        game,
        avg_type=pyspiel.MCCFRAverageType.FULL,
    )
  elif FLAGS.sampling == "outcome":
    solver = pyspiel.OutcomeSamplingMCCFRSolver(game)
  expl_leduc = []
  conv_leduc = []
  for i in range(FLAGS.iterations):
    solver.run_iteration()
    expl_leduc.append(pyspiel.exploitability(game, solver.average_policy()))
    conv_leduc.append(pyspiel.nash_conv(game, solver.average_policy()))
    #print("Iteration {} exploitability: {:.6f}".format(
    #    i, pyspiel.exploitability(game, solver.average_policy())))


  nash_kuhn = np.array(nash_kuhn)
  expl_kuhn = np.array(expl_kuhn)
  nash_leduc = np.array(nash_leduc)
  expl_leduc = np.array(expl_leduc)
  x_kuhn = np.arange(start=0, stop=len(nash_kuhn), step=1)
  x_leduc = np.arange(start=0, stop=len(nash_leduc), step=1)
  
    
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
