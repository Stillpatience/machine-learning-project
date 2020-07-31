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

"""Python spiel example."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random
from absl import app
from absl import flags
import numpy as np

import pyspiel

FLAGS = flags.FLAGS

flags.DEFINE_string("game", "kuhn_poker", "Name of the game")
flags.DEFINE_integer("players", 2, "Number of players")
flags.DEFINE_string("load_state", None,
                    "A file containing a string to load a specific state")
flags.DEFINE_integer("num_episodes", 10, "Number of episodes.")
flags.DEFINE_integer("iterations", 1000, "Number of iterations")


def main(_):
  games_list = pyspiel.registered_games()
  #print("Registered games:")
  #print(games_list)

  action_string = None

  print("Creating game: " + FLAGS.game)
  if FLAGS.players is not None:
    game = pyspiel.load_game(FLAGS.game,
                             {"players": pyspiel.GameParameter(FLAGS.players)})
  else:
    game = pyspiel.load_game(FLAGS.game)
 # print(dir(game))
  #print(game.num_players())
  # Get a new state
  if FLAGS.load_state is not None:
    # Load a specific state
    state_string = ""
    with open(FLAGS.load_state, encoding="utf-8") as input_file:
      for line in input_file:
        state_string += line
    state_string = state_string.rstrip()
    print("Loading state:")
    print(state_string)
    print("")
    state = game.deserialize_state(state_string)
  else:
    state = game.new_initial_state()
 # print("Initial state: " + str(state))
  history = []
  max_iterations = 1
  i = 0

  while i < max_iterations:
    state = game.new_initial_state()
    i += 1
    while not state.is_terminal():
    # The state can be three different types: chance node,
    # simultaneous node, or decision node
      observation = state.legal_actions_mask

      if state.is_chance_node():
        # Chance node: sample an outcome
        outcomes = state.chance_outcomes()
        num_actions = len(outcomes)
        print("Chance node, got " + str(num_actions) + " outcomes")
        action_list, prob_list = zip(*outcomes)
        action = np.random.choice(action_list, p=prob_list)
        print("Sampled outcome: ",
              state.action_to_string(state.current_player(), action))
        state.apply_action(action)

      elif state.is_simultaneous_node():
        # Simultaneous node: sample actions for all players.
        chosen_actions = [
            random.choice(state.legal_actions(pid))
            for pid in range(game.num_players())
        ]
        print("Chosen actions: ", [
            state.action_to_string(pid, action)
            for pid, action in enumerate(chosen_actions)
        ])
        state.apply_actions(chosen_actions)

      else:
        # Decision node: sample action for the single current player
        action = random.choice(state.legal_actions(state.current_player()))
        action_string = state.action_to_string(state.current_player(), action)
        print("Player ", state.current_player(), ", randomly sampled action: ",
              action_string)
        state.apply_action(action)
      print("STAAAAAAAAAAAAAAAAAATE")
      for function in dir(state):
        print(function)
        try:
          print("Function result: ")
          print(getattr(state, function)())
        except:
          print("Unable to load")
      if state.current_player() >= 0:
        if state.private_observation_string(1) == "":
          print("It is None")
        print("Private observation string " + state.private_observation_string(1))
        print("Private observation string " + state.private_observation_string(0))
        print("Public observation string " + state.public_observation_string())
        print(state.private_observation_string(state.current_player()))

      print("GAAAAAAAAAAAME")
      for function in dir(game):
        print(function)
        try:
          print(getattr(game,function)())
        except:
          print("Unable to load")

    history.append([state, action])
  #  print(str(state))

  # Game is now done. Print utilities for each player
    returns = state.returns()
    for pid in range(game.num_players()):
      print("Utility for player {} is {}".format(pid, returns[pid]))
  #for h in history:
  #  print(h[0].returns())
   # print(h[0].action_to_string(h[0].current_player(), h[1]))

if __name__ == "__main__":
  app.run(main)
