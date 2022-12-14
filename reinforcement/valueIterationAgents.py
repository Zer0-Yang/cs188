# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).
import random

# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        for i in range(0, self.iterations):
            values = util.Counter()
            policy = {}
            states = self.mdp.getStates()
            for state in states:
                policy[state] = self.getPolicy(state)
                values[state] = self.getQValue(state, policy[state])
            self.values = values

    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        if self.mdp.isTerminal(state):
            return 0
        nstate_probs = self.mdp.getTransitionStatesAndProbs(state, action)
        q_value = 0
        for state_prob in nstate_probs:
            next_state = state_prob[0]
            prob = state_prob[1]
            q_value += (self.mdp.getReward(state, action, next_state)
                        + self.discount * self.values[next_state]) * prob
        return q_value

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        actions = self.mdp.getPossibleActions(state)
        if not actions:
            return None
        m_action = actions[0]
        m_q_value = float("-inf")
        for action in actions:
            q_value = self.computeQValueFromValues(state, action)
            if q_value > m_q_value:
                m_q_value = q_value
                m_action = action
        return m_action

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        i = 0
        states = self.mdp.getStates()
        while i < self.iterations:
            for state in states:
                policy = self.getPolicy(state)
                self.values[state] = self.getQValue(state, policy)
                i += 1
                if i >= self.iterations:
                    break


class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        predecessors = self.calcu_predecessors()
        priority_queue = util.PriorityQueue()
        states = self.mdp.getStates()
        for state in states:
            if not self.mdp.isTerminal(state):
                diff = abs(self.calcu_m_QValue(state) - self.values[state])
                priority_queue.push(state, -diff)
        for i in range(0, self.iterations):
            if priority_queue.isEmpty():
                break
            state = priority_queue.pop()
            self.values[state] = self.calcu_m_QValue(state)
            predecessor = predecessors[state]
            for p in predecessor:
                diff = abs(self.calcu_m_QValue(p) - self.values[p])
                if diff > self.theta:
                    priority_queue.update(p, -diff)

    def calcu_m_QValue(self, state):
        return self.computeQValueFromValues(state, self.computeActionFromValues(state))

    def calcu_predecessors(self):
        states = self.mdp.getStates()
        if not states:
            return None
        predecessors = {states[0]: []}
        for state in states:
            actions = self.mdp.getPossibleActions(state)
            next_states = set()
            for action in actions:
                nstate_props = self.mdp.getTransitionStatesAndProbs(state, action)
                for nstate_prop in nstate_props:
                    next_states.add(nstate_prop[0])
            for next_state in next_states:
                if next_state not in predecessors:
                    predecessors.update({next_state: []})
                predecessors[next_state].append(state)
        return predecessors
