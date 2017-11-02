import chess
import sys
import math
import numpy as np
import argparse
import datetime
import operator
import random
from random import choice
import copy
from chess import pgn, uci
from collections import defaultdict

DRAW = 'draw'
# This constant should change exploration tendencies
CPUCT = 1.5

# NN = network.load()

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
		return [y for x, y in self.node.parent.children if y != self]

	def total_sims_at_depth(self):
		sims = self.simulations
		for sibling in self.get_siblings():
			sims += sibling.simulations
		return sims

	def get_confidence(self):
		term1 = CPUCT*self.prob
		term2 = math.sqrt(self.total_sims_at_depth)/(1 + self.simulations)
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

	TEMPERATURE = True

	def __init__(self, startpos=chess.Board(), iter_time=100):
		self.startpos = startpos
		self.__root = Node(True, position=chess.Board())
		self.iter_time = iter_time

	def max_action_val_child(root):
		max_val = 0
		max_child = None
		max_edge = None
		for child, edge in root.children:
			if edge.action_value + edge.get_confidence() > max_val:
				max_child = child
				max_edge = edge
		return (max_child, max_edge)

	def most_visited_child(root):
		max_visits = 0
		max_child = None
		for child, edge in root.children:
			if edge.simulations > max_visits:
				max_child = child
		return max_child

	def total_child_visits(root):
		visits = 0
		for child, edge in root.children:
			visits += edge.simulations
		return visits

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

	def build(self):
		begin = datetime.datetime.utcnow()
		while datetime.datetime.utcnow() - begin < datetime.timedelta(seconds=self.iter_time):
			leaf = self.select_leaf(self.__root)
			self.expand_tree(leaf)
			self.backprop(leaf, NN.value(leaf.position))

	def select_leaf(self, root):
		if not root.children:
			return root
		else:
			return select_leaf(max_action_val_child(root)[0])

	def expand_tree(self, leaf):
		if leaf.position:
			new_leaves = []
			board = leaf.position
			priors = NN.policy(board)
			moves = list(board.legal_moves)
			if len(moves) == 0:
				print("No moves from position: " + board.fen() + "\n")
			for selected_move in moves:
				new_board = copy.deepcopy(board)
				# Make sure you can index into priors with a UCI move
				new_edge = Edge(leaf, selected_move, priors[selected_move.uci()])
				new_board.push(selected_move)
				new_node = Node(not leaf.color, parent=leaf, position=new_board)
				leaf.children.append((leaf, new_edge))
				new_leaves.append(new_node)
			return new_leaves
		else:
			print("MCTS tried to expand with empty position.")

	def backprop(self, leaf, value):
		leaf = leaf.parent
		while leaf:
			path_edge = max_action_val_child(leaf)[1]
			path_edge.simulations += 1
			path_edge.total_action_value += value
			path_edge.action_value = path_edge.total_action_value/path_edge.simulations
			leaf = leaf.parent

	def best_move(self):
		# TODO totally different algorithm to pick a move
		node = self.__root
		child_scores = []
		for child, edge in node.children:
			# TODO fix this to use edges
			child_scores.append((child.move.uci(), (child.wins/child.simulations)))
		return sorted(child_scores, key=operator.itemgetter(1), reverse=True)[0][0]

	def recurs_print(self, node, file_handle):
		# Fully broken, need to fix DOT to label edges and use them to traverse here
		string_set = "{ "
		for child, edge in node.children:
			string_set += str(id(child)) + " [label=\"sims" + str(child.simulations) + "wins" + str(child.wins) + "color" + str(child.color) + "\"] "
		string_set += "}"
		file_handle.write(str(id(node)) + " [label=\"sims" + str(node.simulations) + "wins" + str(node.wins) + "color" + str(node.color) + '\"];')
		file_handle.write(str(id(node)) + ' -> ' + string_set + ';\n')
		for child, edge in node.children:
			self.recurs_print(child, file_handle)


	def print_tree(self):
		# Fully broken, see recurs_print
		node = self.__root
		with open("/Users/evanmdoyle/Programming/ChessAI/MCTS.dot", 'w') as f:
			f.write("digraph G { \n")
			self.recurs_print(node, f)
			f.write("}\n")

