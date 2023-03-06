# baselineTeam.py
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


# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions, Actions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveAgent', second = 'OffensiveAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.

  """
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def registerInitialState(self, gameState):
    self.foodnum = 0
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    values = [self.evaluate(gameState, a) for a in actions]

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    next_action = random.choice(bestActions)
    nextGameState = self.getSuccessor(gameState, next_action)
    nextPos = nextGameState.getAgentState(self.index).getPosition()
    
    food = self.getFood(gameState)
    
    foodLeft = len(self.getFood(gameState).asList())

    if not nextGameState.getAgentState(self.index).isPacman:
      self.foodnum = 0

    if food[int(nextPos[0])][int(nextPos[1])] is True:
          self.foodnum += 1

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist

      return bestAction

    return next_action

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

class OffensiveAgent(DummyAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
            
  def getFeatures(self, gameState, action):
    global foodList
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    curfoodList = self.getFood(gameState)
    foodList = self.getFood(successor).asList()
    myState = successor.getAgentState(self.index)
    myPos = successor.getAgentState(self.index).getPosition()
    wall = gameState.getWalls()
    score = 0
    
    if curfoodList[int(myPos[0])][int(myPos[1])]:
          score += 200

    enems = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invs = [a for a in enems if a.isPacman and a.getPosition() != None]
    non_invs = [a for a in enems if not a.isPacman and a.getPosition() != None]

    if len(foodList) > 0 and self.foodnum == 0 and len(invs) == 0:
      minFoodDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['mindistFood'] = minFoodDistance

    gdis_min = wall.height + wall.width
    
    if myState.isPacman :
          sight = 6
    else :
          sight = 3
    
    if len(non_invs) > 0:
      for ghost in non_invs:
        if ghost.scaredTimer == 0:
          gdis_min = min(self.getMazeDistance(myPos, ghost.getPosition()), gdis_min)
      if gdis_min < sight:
            score -= 20 ** (sight + 1 - gdis_min)
    
    features['successorScore'] = score
    
    if self.foodnum > 0:
      minHomeDistance = min([self.getMazeDistance(myPos, self.start)])
      features['back'] = minHomeDistance

    if action == Directions.STOP: features['stop'] = 1
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 1, 'mindistFood': -10, 'back': -30, 'stop': -100}

class DefensiveAgent(DummyAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    curfoodList = self.getFood(gameState)
    foodList = self.getFood(successor).asList()
    myState = successor.getAgentState(self.index)
    myPos = successor.getAgentState(self.index).getPosition()
    wall = gameState.getWalls()
    score = 0
    
    if curfoodList[int(myPos[0])][int(myPos[1])]:
          score += 50

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invs = [a for a in enemies if a.isPacman and a.getPosition() != None]
    non_invs = [a for a in enemies if not a.isPacman and a.getPosition() != None]


    if len(foodList) > 0 and self.foodnum == 0 and len(invs) == 0:
      minFoodDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['mindistFood'] = minFoodDistance

    gdis_min = wall.height + wall.width
    
    if myState.isPacman :
          sight = 6
    else :
          sight = 3
    
    if len(non_invs) > 0:
      for ghost in non_invs:
        if ghost.scaredTimer == 0:
          gdis_min = min(self.getMazeDistance(myPos, ghost.getPosition()), gdis_min)
      if gdis_min < sight:
            score -= 50 ** (sight + 1 - gdis_min)
      
    
    features['successorScore'] = int(score)
    
    if self.foodnum > 0:
      minHomeDistance = min([self.getMazeDistance(myPos, self.start)])
      features['back'] = minHomeDistance

    if len(invs) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invs]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 1, 'mindistFood': -1, 'back': -10, 'invaderDistance': -20, 'stop': -100}
