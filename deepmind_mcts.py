# I absolutely hate this sys path stuff
import sys
sys.path.append(sys.path[0] + "/..")

import chess
import math
import numpy as np
import argparse
import datetime
import operator
import random
import copy
import pychess_utils as util

from random import choice
from chess import pgn, uci
from collections import defaultdict
from rpc_client import PredictClient

DRAW = 'draw'
# This constant should change exploration tendencies
CPUCT = 1.5

# These caches don't kick in until second game but are vital to performance at that point
# This delay is because initially all selected leaves are compulsory misses :(
prediction_cache = {}
value_cache = {}

class Edge:

	def __init__(self, node, move, prob, simulations=0, total_action_value=0, action_value=0):
		self.node = node
		self.prob = prob
		self.total_action_value = total_action_value
		self.action_value = action_value
		self.simulations = simulations
		self.move = move

	@property
	def move(self):
		return self.__move

	@move.setter
	def move(self, move):
		self.__move = move if type(move) == chess.Move else None

	@property
	def prob(self):
		return self.__prob

	@prob.setter
	def prob(self, prob):
		self.__prob = prob if prob >= 0 else 0

	@property
	def simulations(self):
		return self.__simulations

	@simulations.setter
	def simulations(self, sims):
		self.__simulations = sims if sims >=0 else 0

	def get_siblings(self):
		return [y for x, y in self.node.children if y != self]

	def total_sims_at_depth(self):
		sims = self.simulations
		for sibling in self.get_siblings():
			sims += sibling.simulations
		return sims

	def get_confidence(self):
		term1 = CPUCT*self.prob
		term2 = math.sqrt(self.total_sims_at_depth())/(1 + self.simulations)
		return term1*term2


class Node:

	def __init__(self, color, parent=None, position=None):
		self.position = position
		self.color = color
		self.parent = parent
		self.children = []

	@property
	def position(self):
		return self.__position

	@position.setter
	def position(self, position):
		self.__position = position if type(position) == chess.Board else None

	@property
	def children(self):
		return self.__children

	@children.setter
	def children(self, children):
		self.__children = children

	@property
	def parent(self):
		return self.__parent

	@parent.setter
	def parent(self, parent):
		self.__parent = parent



class MCTS:

	# 1600 Iterations is simply too intense for this machine...
	# Need to look into splitting into threads, queuing requests and cloud resources
	ITERATIONS_PER_BUILD = 1600
	ITER_TIME = 15

	def __init__(self, startpos=chess.Board(), iterations=None, iter_time=None,
		prev_mcts=None, temperature=True, version=util.latest_version(), startcolor=True):
		self.version = version
		# gRPC client to query the trained model at localhost:9000
		# SERVER MUST BE RUNNING LOCALLY
		self.__client = PredictClient('127.0.0.1', 9000, 'default', int(self.version))

		self.startpos = startpos
		if prev_mcts:
			# This saves the statistics about this startpos from the prev_mcts
			self.__root = prev_mcts.child_matching(self.startpos)
			if not self.__root:
				print("Could not find move in previous tree.")
				self.__root = Node(startcolor, position=self.startpos)
		else:
			self.__root = Node(startcolor, position=self.startpos)

		self.iterations = iterations if iterations else self.ITERATIONS_PER_BUILD
		self.iter_time = iter_time if iter_time else self.ITER_TIME

		self.temperature = temperature

	def child_matching(self, position):
		if not self.__root.children:
			return None
		for child, edge in self.__root.children:
			if child.position == position:
				return child
		return None

	def max_action_val_child(self, root):
		max_val = -1*float("inf")
		max_child = None
		max_edge = None
		for child, edge in root.children:
			if edge.action_value + edge.get_confidence() >= max_val:
				max_child = child
				max_edge = edge
				max_val = edge.action_value + edge.get_confidence()
		return (max_child, max_edge)

	def most_visited_child(self, root):
		max_visits = 0
		max_edge = None
		for child, edge in root.children:
			if edge.simulations >= max_visits:
				max_edge = edge
		return max_edge

	def total_child_visits(self, root):
		visits = 0
		for child, edge in root.children:
			visits += edge.simulations
		return visits

	@property
	def iterations(self):
		return self.__iterations

	@iterations.setter
	def iterations(self, iters):
		self.__iterations = max(0, min(iters, 3200))

	@property
	def startpos(self):
		return self.__startpos

	@startpos.setter
	def startpos(self, startpos):
		self.__startpos = startpos if type(startpos) == chess.Board else chess.Board()

	@property
	def iter_time(self):
		return self.__iter_time

	@iter_time.setter
	def iter_time(self, time):
		self.__iter_time = time if time > 0 else 100

	def search(self):
		leaf = self.select_leaf(self.__root)
		self.expand_tree(leaf)
		if not value_cache.get(leaf.position.fen()):
			try:
				value_cache[leaf.position.fen()] = self.__client.predict(util.expand_position(leaf.position))[0]
			except:
				print("Prediction error, retrying...")
				value_cache[leaf.position.fen()] = self.__client.predict(util.expand_position(leaf.position))[0]
		self.backprop(leaf, value_cache[leaf.position.fen()])

	def build(self, timed=False):
		if timed == True:
			begin = datetime.datetime.utcnow()
			while datetime.datetime.utcnow() - begin < datetime.timedelta(seconds=self.iter_time):
				self.search()
		else:
			for iteration in range(self.iterations):
				self.search()

	def select_leaf(self, root):
		while root:
			if not root.children:
				return root
			root = self.max_action_val_child(root)[0]
		print("Shouldn't hit this point.")
		return Node(True)

	def expand_tree(self, leaf):
		if leaf.position:
			new_leaves = []
			board = leaf.position
			if not prediction_cache.get(board.fen()):
				try:
					prediction_cache[board.fen()] = self.__client.predict(util.expand_position(board), 'policy')
				except:
					print("Prediction error, retrying...")
					prediction_cache[board.fen()] = self.__client.predict(util.expand_position(board), 'policy')
			moves = list(board.legal_moves)
			if len(moves) == 0:
				print("No moves from position: " + board.fen() + "\n")
			for selected_move in moves:
				new_board = copy.deepcopy(board)
				new_edge = Edge(leaf, selected_move,
						util.logit_to_prob(prediction_cache[board.fen()][(selected_move.from_square*64)+selected_move.to_square])
						)
				new_board.push(selected_move)
				new_node = Node(not leaf.color, parent=leaf, position=new_board)
				leaf.children.append((new_node, new_edge))
				new_leaves.append(new_node)
			return new_leaves
		else:
			print("MCTS tried to expand with empty position.")

	def backprop(self, leaf, value):
		leaf = leaf.parent
		while leaf:
			path_edge = self.max_action_val_child(leaf)[1]
			path_edge.simulations += 1
			path_edge.total_action_value += value
			path_edge.action_value = path_edge.total_action_value/path_edge.simulations
			leaf = leaf.parent

	def get_policy_string(self):
		policy = []
		total_vists = self.total_child_visits(self.__root)
		for child, edge in self.__root.children:
			prob = edge.simulations/total_vists
			if prob == 1:
				policy.append("("+str(edge.move.from_square)+"!"+str(edge.move.to_square)+":"+str(1000)+")")
			else:
				policy.append("("+str(edge.move.from_square)+"!"+str(edge.move.to_square)+":"+str(util.prob_to_logit(prob))+")")
		return '-'.join(policy)

	def best_move(self):
		if self.temperature:
			choices = []
			chances = defaultdict(int)
			for child, edge in self.__root.children:
				choices += [edge.move]*edge.simulations
				chances[edge.move.uci()] = edge.simulations
			# This does a weighted random selection based on simulations
			choice = random.choice(choices)
			print(choice.uci() + " was chosen with chance: " + str(chances[choice.uci()]/len(choices)) + " out of " + str(len(self.__root.children)) + " options.")
			return choice
		else:
			return self.most_visited_child(self.__root).move
