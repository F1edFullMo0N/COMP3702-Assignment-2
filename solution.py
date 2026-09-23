import sys
import time

from game_env import GameEnv
from game_state import GameState
"""
solution.py

This file is a template you should use to implement your solution.

You should implement each of the method stubs below. You may add additional methods and/or classes to this file if you 
wish. You may also create additional source files and import to this file if you wish.

COMP3702 Assignment 2 "CrystalRover" Support Code

Last updated by vp 09/09/2026
"""


class Solver:

    STUDENT_NAME = "Zixiang Ji" # replace with your name
    STUDENT_ID = "49832853"  # replace with your student ID
    GITHUB_USERNAME = "F1edFullMo0N" # replace with your GitHub username

    def __init__(self, game_env: GameEnv):
        self.game_env = game_env
        #
        # TODO: Define any class instance variables you require (e.g. dictionary mapping state to VI value) here.
        #
        pass

    # TODO: next time, make this method external to the solver class
    @staticmethod
    def testcases_to_attempt():
        """
        Return a list of testcase numbers you want your solution to be evaluated for.
        """
        # TODO: modify below if desired (e.g. disable larger testcases if you're having problems with RAM usage, etc)
        return [1, 2, 3, 4, 5]

    # === Value Iteration ==============================================================================================

    def vi_initialise(self):
        """
        Initialise any variables required before the start of Value Iteration.
        """
        #
        # TODO: Implement any initialisation for Value Iteration (e.g. building a list of states) here. You should not
        #  perform value iteration in this method.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        self.vi_states = self.build_vi_states()
        self.vi_values = {state: 0.0 for state in self.vi_states}
        self.vi_previous_values = self.vi_values.copy()
    def vi_is_converged(self):
        """
        Check if Value Iteration has reached convergence.
        :return: True if converged, False otherwise
        """
        #
        # TODO: Implement code to check if Value Iteration has reached convergence here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        if not self.vi_values or not self.vi_previous_values:
            return False
        max_delta = 0.0
        for state in self.vi_values:
            max_delta = max(max_delta, abs(self.vi_values[state] 
                                            - self.vi_previous_values.get(state, 0.0)))
        return max_delta <= self.game_env.epsilon


    def vi_iteration(self):
        """
        Perform a single iteration of Value Iteration (i.e. loop over the state space once).
        """
        #
        # TODO: Implement code to perform a single iteration of Value Iteration here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #

        


    def vi_plan_offline(self):
        """
        Plan using Value Iteration.
        """
        # !!! In order to ensure compatibility with tester, you should not modify this method !!!
        self.vi_initialise()
        while True:
            self.vi_iteration()

            # NOTE: vi_iteration is always called before vi_is_converged
            if self.vi_is_converged():
                break

    def vi_get_state_value(self, state: GameState):
        """
        Retrieve V(s) for the given state.
        :param state: the current state
        :return: V(s)
        """
        #
        # TODO: Implement code to return the value V(s) for the given state (based on your stored VI values) here. If a
        #  value for V(s) has not yet been computed, this function should return 0.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        return self.vi_values.get(state, 0.0)

    def vi_select_action(self, state: GameState):
        """
        Retrieve the optimal action for the given state (based on values computed by Value Iteration).
        :param state: the current state
        :return: optimal action for the given state (element of ROBOT_ACTIONS)
        """
        #
        # TODO: Implement code to return the optimal action for the given state (based on your stored VI values) here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    # === Policy Iteration =============================================================================================

    def pi_initialise(self):
        """
        Initialise any variables required before the start of Policy Iteration.
        """
        #
        # TODO: Implement any initialisation for Policy Iteration (e.g. building a list of states) here. You should not
        #  perform policy iteration in this method. You should assume an initial policy of always move FORWARDS.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    def pi_is_converged(self):
        """
        Check if Policy Iteration has reached convergence.
        :return: True if converged, False otherwise
        """
        #
        # TODO: Implement code to check if Policy Iteration has reached convergence here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    def pi_iteration(self):
        """
        Perform a single iteration of Policy Iteration (i.e. perform one step of policy evaluation and one step of
        policy improvement).
        """
        #
        # TODO: Implement code to perform a single iteration of Policy Iteration (evaluation + improvement) here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    def pi_plan_offline(self):
        """
        Plan using Policy Iteration.
        """
        # !!! In order to ensure compatibility with tester, you should not modify this method !!!
        self.pi_initialise()
        while True:
            self.pi_iteration()

            # NOTE: pi_iteration is always called before pi_is_converged
            if self.pi_is_converged():
                break

    def pi_select_action(self, state: GameState):
        """
        Retrieve the optimal action for the given state (based on values computed by Value Iteration).
        :param state: the current state
        :return: optimal action for the given state (element of ROBOT_ACTIONS)
        """
        #
        # TODO: Implement code to return an action for the given state (based on your stored PI policy) here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    # === Helper Methods ===============================================================================================
    #
    #
    # TODO: Add any additional methods here
    #
    #
    def get_valid_actions(self, state):
        tile = self.game_env.grid_data[state.row][state.col]

        if tile == self.game_env.CRATER_TILE:
            return [
                action for action in self.game_env.ACTIONS
                if action in self.game_env.JUMP_ACTIONS
            ]
        else:
            return [
                action for action in self.game_env.ACTIONS
                if action in self.game_env.WALK_ACTIONS
                or action in self.game_env.BOOST_ACTIONS
            ]
        
    def transition_outcomes(self, state, action):
        if action not in self.game_env.ACTIONS:
            return []

        outcomes = {}
        drift_actions = self.game_env.PERPENDICULAR_ACTIONS.get(action, [])
        drift_probability = self.game_env.random_drift_prob
        double_probability = self.game_env.random_double_prob
        no_drift_probability = 1.0 - drift_probability
        no_double_probability = 1.0 - double_probability

        transition_sequences = [
            ([action], no_drift_probability * no_double_probability),
            ([action, action], no_drift_probability * double_probability),
        ]

        drift_step_probability = drift_probability / max(len(drift_actions), 1)
        for drift_action in drift_actions:
            transition_sequences.append(([drift_action], drift_step_probability 
                                            * no_double_probability))
            transition_sequences.append(([drift_action, drift_action],
                                            drift_step_probability * double_probability))

        for sequence, sequence_probability in transition_sequences:
            if sequence_probability <= 0.0:
                continue
            self.expand_transition_sequence(state, sequence, sequence_probability, 0.0, outcomes)

        return [
            (next_state, probability_sum, reward_sum)
            for next_state, (probability_sum, reward_sum) in outcomes.items()
        ]
    
    def build_vi_states(self):
        initial_state = self.game_env.get_init_state()
        visited = {initial_state}
        queue = [initial_state]

        while queue:
            state = queue.pop(0)
            for action in self.get_valid_actions(state):
                for next_state, _, _ in self.transition_outcomes(state, action):
                    if next_state not in visited:
                        visited.add(next_state)
                        queue.append(next_state)

        return list(visited)
    
    def expand_transition_sequence(self, state, sequence, probability, reward_so_far, outcomes):
            if not sequence:
                if state not in outcomes:
                    outcomes[state] = [0.0, 0.0]
                outcomes[state][0] += probability
                outcomes[state][1] += probability * reward_so_far
                return
    
            movement = sequence[0]
            remaining = sequence[1:]
    
            if movement in self.game_env.BOOST_ACTIONS:
                for move_distance, move_probability in enumerate(self.game_env.boost_probabilities):
                    if move_probability <= 0.0:
                        continue
                    next_state, movement_reward = self.deterministic_move(state, movement, move_distance)
                    self._expand_transition_sequence(next_state, remaining, probability * move_probability,
                                                    reward_so_far + movement_reward, outcomes)
            else:
                next_state, movement_reward = self.deterministic_move(state, movement, 1)
                self._expand_transition_sequence(next_state, remaining, probability, reward_so_far + movement_reward, outcomes)
    
    def deterministic_move(self, state, action, move_distance):
        reward = -1.0 * self.game_env.ACTION_COST[action]
        next_row, next_col = state.row, state.col
        direction = self.game_env._action_direction(action)

        deltas = {
            'LEFT': (0, -1),
            'RIGHT': (0, 1),
            'UP': (-1, 0),
            'DOWN': (1, 0),
        }
        delta_row, delta_col = deltas[direction]

        collision = False
        for _ in range(move_distance):
            candidate_row = next_row + delta_row
            candidate_col = next_col + delta_col
            if not (0 <= candidate_row < self.game_env.n_rows and 0 <= candidate_col < self.game_env.n_cols) or \
                    self.game_env.grid_data[candidate_row][candidate_col] == self.game_env.ROCK_TILE:
                reward -= self.game_env.collision_penalty
                collision = True
                break

            next_row, next_col = candidate_row, candidate_col

            if self.game_env.grid_data[next_row][next_col] == self.game_env.CRATER_TILE:
                break

            if self.game_env.grid_data[next_row][next_col] == self.game_env.LAVA_TILE:
                reward -= self.game_env.game_over_penalty
                break

        crystal_status = state.crystal_status
        if (next_row, next_col) in self.game_env.crystal_positions:
            crystal_index = self.game_env.crystal_positions.index((next_row, next_col))
            if crystal_status[crystal_index] == 0:
                crystal_status = list(crystal_status)
                crystal_status[crystal_index] = 1
                crystal_status = tuple(crystal_status)

        next_state = GameState(next_row, next_col, crystal_status)
        if not collision and self.game_env.is_game_over(next_state) and \
                self.game_env.grid_data[next_row][next_col] != self.game_env.LAVA_TILE:
            reward -= self.game_env.game_over_penalty

        return next_state, reward

