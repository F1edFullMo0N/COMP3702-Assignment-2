import sys
import time
import numpy as np
from collections import deque

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
        self.vi_values = {}
        self.vi_previous_values = {}
        self.vi_states = []
        self.transition_cache = {}

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

        self.vi_previous_values = self.vi_values.copy()

        for state in self.vi_states:
            if self.game_env.is_game_over(state) or self.game_env.is_solved(state):
                self.vi_values[state] = 0.0
                continue

            best_value = float('-inf')

            for action in self.get_valid_actions(state):
                action_value = 0.0

                for next_state, transition_prob, reward in \
                        self.transition_outcomes(state, action):

                    action_value += transition_prob * (
                        reward
                        + self.game_env.gamma
                        * self.vi_values.get(next_state, 0.0)
                    )

                best_value = max(best_value, action_value)

            self.vi_values[state] = best_value


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
        
        if self.game_env.is_game_over(state) or self.game_env.is_solved(state):
                    return self.game_env.ACTIONS[0]
        
        best_action = None
        best_value = float('-inf')

        for action in self.get_valid_actions(state):
            action_value = 0.0
            for next_state, transition_prob, reward in self.transition_outcomes(state, action):
                action_value += transition_prob * (
                reward
                + self.game_env.gamma
                * self.vi_values.get(next_state, 0.0)
            )
            if action_value > best_value:
                best_value = action_value
                best_action = action

        return best_action if best_action is not None else self.game_env.ACTIONS[0]

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
        self.pi_states = self.build_vi_states()
        self.pi_values = {state: 0.0 for state in self.pi_states}
        self.pi_policy = {}
        self.pi_previous_policy = {}

        for state in self.pi_states:
            valid_actions = self.get_valid_actions(state)
            self.pi_policy[state] = valid_actions[0] if valid_actions else self.game_env.ACTIONS[0]

        self.pi_state_index = {
            state: i
            for i, state in enumerate(self.pi_states)
        }

        self.pi_action_index = {
            action: i
            for i, action in enumerate(self.game_env.ACTIONS)
        }

        # Keep this list for policy improvement, but policy evaluation below
        # uses the full state matrix (i.e. no matrix downscaling).
        self.pi_nonterminal_states = [
            state for state in self.pi_states
            if not self.game_env.is_game_over(state)
            and not self.game_env.is_solved(state)
        ]

        self.pi_valid_actions = {
            state: self.get_valid_actions(state)
            for state in self.pi_states
        }

        sa_states = []
        sa_actions = []
        sa_rewards = []
        tr_pair = []
        tr_next = []
        tr_prob = []

        pair_id = 0

        for state in self.pi_nonterminal_states:
            s = self.pi_state_index[state]
            for action in self.pi_valid_actions[state]:
                a = self.pi_action_index[action]

                sa_states.append(s)
                sa_actions.append(a)

                expected_reward = 0.0
                for next_state, prob, reward in self.transition_outcomes(state, action):
                    expected_reward += prob * reward

                    tr_pair.append(pair_id)
                    tr_next.append(self.pi_state_index[next_state])
                    tr_prob.append(prob)

                sa_rewards.append(expected_reward)
                pair_id += 1

        self.pi_sa_states = np.asarray(sa_states, dtype=np.int32)
        self.pi_sa_actions = np.asarray(sa_actions, dtype=np.int32)
        self.pi_sa_rewards = np.asarray(sa_rewards, dtype=np.float64)

        self.pi_tr_pair = np.asarray(tr_pair, dtype=np.int32)
        self.pi_tr_next = np.asarray(tr_next, dtype=np.int32)
        self.pi_tr_prob = np.asarray(tr_prob, dtype=np.float64)

        self.pi_value_array = np.zeros(
            len(self.pi_states),
            dtype=np.float64,
        )

        self.pi_values = {
            state: 0.0
            for state in self.pi_states
        }

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
        if not self.pi_states or not self.pi_policy:
            return False
        if not self.pi_previous_policy:
            return False

        for state in self.pi_states:
            if self.pi_previous_policy.get(state) != self.pi_policy.get(state):
                return False
        return True

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
        if not self.pi_states:
            return

        self.pi_previous_policy = self.pi_policy.copy()

        # Policy evaluation using the full |S| x |S| system.
        # Terminal-state rows remain as identity rows with b=0, so their value is 0.
        n = len(self.pi_states)

        A = np.eye(n)
        b = np.zeros(n)

        for state in self.pi_nonterminal_states:
            i = self.pi_state_index[state]
            action = self.pi_policy[state]

            for next_state, probability, reward in self.transition_outcomes(state, action):
                b[i] += probability * reward
                j = self.pi_state_index[next_state]
                A[i, j] -= self.game_env.gamma * probability

        values = np.linalg.solve(A, b)

        self.pi_value_array[:] = values

        for state, i in self.pi_state_index.items():
            self.pi_values[state] = self.pi_value_array[i]

        weighted_future = (
            self.pi_tr_prob
            * self.pi_value_array[self.pi_tr_next]
        )
        future_by_pair = np.bincount(
            self.pi_tr_pair,
            weights=weighted_future,
            minlength=len(self.pi_sa_rewards),
        )

        q_pairs = (
            self.pi_sa_rewards
            + self.game_env.gamma * future_by_pair
        )

        n_states = len(self.pi_states)
        n_actions = len(self.game_env.ACTIONS)
        q_matrix = np.full((n_states, n_actions), -np.inf)
        q_matrix[self.pi_sa_states, self.pi_sa_actions] = q_pairs

        best_actions = np.argmax(q_matrix, axis=1)

        improved_policy = {}
        for state in self.pi_nonterminal_states:
            i = self.pi_state_index[state]
            improved_policy[state] = self.game_env.ACTIONS[int(best_actions[i])]

        for state in self.pi_states:
            if self.game_env.is_game_over(state) or self.game_env.is_solved(state):
                improved_policy[state] = self.game_env.ACTIONS[0]

        self.pi_policy = improved_policy

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
        if self.game_env.is_game_over(state) or self.game_env.is_solved(state):
            return self.game_env.ACTIONS[0]

        action = self.pi_policy.get(state)
        if action is not None and action in self.get_valid_actions(state):
            return action

        valid_actions = self.get_valid_actions(state)
        return valid_actions[0] if valid_actions else self.game_env.ACTIONS[0]

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
        
        key = (state, action)
        if key in self.transition_cache:
            return self.transition_cache[key]
        
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
            transition_sequences.append(([drift_action], drift_step_probability * no_double_probability))
            transition_sequences.append(([drift_action, drift_action], drift_step_probability * double_probability))

        for sequence, sequence_probability in transition_sequences:
            if sequence_probability <= 0.0:
                continue
            self.expand_transition_sequence(state, sequence, sequence_probability, 0.0, outcomes)

        result = []
        for next_state, (probability_sum, weighted_reward_sum) in outcomes.items():
            if probability_sum <= 0.0:
                continue
            result.append((next_state, probability_sum, weighted_reward_sum / probability_sum))

        self.transition_cache[key] = result
        return result

    def build_vi_states(self):
        initial_state = self.game_env.get_init_state()

        visited = {initial_state}
        queue = deque([initial_state])
        states = []

        while queue:
            state = queue.popleft()
            states.append(state)

            if self.game_env.is_game_over(state) or self.game_env.is_solved(state):
                continue

            for action in self.get_valid_actions(state):
                for next_state, _, _ in self.transition_outcomes(state, action):
                    if next_state not in visited:
                        visited.add(next_state)
                        queue.append(next_state)

        return list(reversed(states))

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
            for move_distance, move_probability in enumerate(
                    self.game_env.boost_probabilities):

                if move_probability <= 0.0:
                    continue

                next_state, movement_reward, valid, terminal = \
                    self.deterministic_move(
                        state, movement, move_distance
                    )

                if not valid:
                    self.expand_transition_sequence(
                        state,
                        remaining,
                        probability * move_probability,
                        reward_so_far,
                        outcomes
                    )
                    continue

                if terminal:
                    if next_state not in outcomes:
                        outcomes[next_state] = [0.0, 0.0]

                    p = probability * move_probability
                    outcomes[next_state][0] += p
                    outcomes[next_state][1] += \
                        p * (reward_so_far + movement_reward)

                else:
                    self.expand_transition_sequence(
                        next_state,
                        remaining,
                        probability * move_probability,
                        reward_so_far + movement_reward,
                        outcomes
                    )
        else:
            next_state, movement_reward, valid, terminal = self.deterministic_move(state, movement, 1)
            if not valid:
                self.expand_transition_sequence(state, remaining, probability, reward_so_far, outcomes)
                return
            if terminal:
                if next_state not in outcomes:
                    outcomes[next_state] = [0.0, 0.0]
                outcomes[next_state][0] += probability
                outcomes[next_state][1] += probability * (reward_so_far + movement_reward)
            else:
                self.expand_transition_sequence(next_state, remaining, probability, reward_so_far + movement_reward, outcomes)

    def deterministic_move(self, state, action, move_distance):
        if self.game_env.is_game_over(state) or self.game_env.is_solved(state):
            return state, 0.0, False, True

        if action in self.game_env.JUMP_ACTIONS:
            if self.game_env.grid_data[state.row][state.col] != self.game_env.CRATER_TILE:
                return state, 0.0, False, False
        elif action in self.game_env.WALK_ACTIONS or action in self.game_env.BOOST_ACTIONS:
            if self.game_env.grid_data[state.row][state.col] == self.game_env.CRATER_TILE:
                return state, 0.0, False, False

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

        terminal = self.game_env.is_game_over(next_state) or self.game_env.is_solved(next_state)
        return next_state, reward, True, terminal

