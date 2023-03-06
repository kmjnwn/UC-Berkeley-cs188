# myAgents.py
# ---------------
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

from multiprocessing.dummy import current_process
from queue import Empty
from typing import Any
from game import Agent
from searchProblems import PositionSearchProblem

import util
import time
import search

"""
IMPORTANT
`agent` defines which agent you will use. By default, it is set to ClosestDotAgent,
but when you're ready to test your own agent, replace it with MyAgent
"""
def createAgents(num_pacmen, agent='ClosestDotAgent'):
    return [eval(agent)(index=i) for i in range(num_pacmen)]


class MyAgent(Agent):
    """
    Implementation of your agent.
    """

    def getAction(self, state):
        """
        Returns the next action the agent will take
        """

        "*** YOUR CODE HERE ***"
        problem = AnyFoodSearchProblem(state, self.index)
        foods = state.getFood()
        
        global goal_pos, ans_path, path_i
        index = self.index
        
        if goal_pos[index] != [-1,-1] and foods[goal_pos[index][0]][goal_pos[index][1]] == True and path_i[index] >= len(ans_path[index]) :
            fringe = util.Queue()
            current = (problem.getStartState(), [])
            fringe.push(current)
            closed = []
            
            while not fringe.isEmpty():
                node, path = fringe.pop()
                
                if problem.isGoalState(node):
                    goal_pos[index] = node
                    break
                    
                if not node in closed:
                    closed.append(node)
                    for coord, move, cost in problem.getSuccessors(node):
                        fringe.push((coord, path + [move]))
                
                ans_path[index] = path.copy()
                path_i[index] = 1
            
            return path[0]

        else :
            path_i[index] += 1
            return ans_path[index][path_i[index] - 1]

    def initialize(self):
        """
        Intialize anything you want to here. This function is called
        when the agent is first created. If you don't need to use it, then
        leave it blank
        """

        "*** YOUR CODE HERE"
        global ans_path
        ans_path = [[0,] for i in range(20)]
        global path_i
        path_i = [100000 for i in range(20)]
        global goal_pos
        goal_pos = [[-1,-1] for i in range(20)]

"""
Put any other SearchProblems or search methods below. You may also import classes/methods in
search.py and searchProblems.py. (ClosestDotAgent as an example below)
"""

class ClosestDotAgent(Agent):

    def getAction(self, state):
        """
        Returns the next action the agent will take
        """

        "*** YOUR CODE HERE ***"
        problem = AnyFoodSearchProblem(state, self.index)
        path = search.bfs(problem)
        return path[0]

class AnyFoodSearchProblem(PositionSearchProblem):
    """
    A search problem for finding a path to any food.

    This search problem is just like the PositionSearchProblem, but has a
    different goal test, which you need to fill in below.  The state space and
    successor function do not need to be changed.

    The class definition above, AnyFoodSearchProblem(PositionSearchProblem),
    inherits the methods of the PositionSearchProblem.

    You can use this search problem to help you fill in the findPathToClosestDot
    method.
    """

    def __init__(self, gameState, agentIndex):
        "Stores information from the gameState.  You don't need to change this."
        # Store the food for later reference
        self.food = gameState.getFood()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition(agentIndex)
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def isGoalState(self, state):
        """
        The state is Pacman's position. Fill this in with a goal test that will
        complete the problem definition.
        """
        x,y = state
        if self.food[x][y] == True:
            return True
        return False

