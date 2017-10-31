import chess
import math
import numpy as np
import argparse
import time
import operator
import random
from chess import pgn, uci

global_id = 0

def total_sims_at_depth(node):
	# TODO

def selection_formula(node):
	# TODO

class Node:

	def __init__(self, color, parent=None, position=None):
		self.gen_id()
		self.color = color
		self.wins = 0
		self.simulations = 0
		self.color = True
		self.parent = parent
		self.children = []

	def gen_id(self):
		global_id += 1
		self.__id = global_id

	def id(self):
		return self.__id

	@property
	def move(self):
		return self.__move

	@move.setter
	def move(self, move):
		self.__move 

	@property
	def wins(self):
		return self.__wins

	@wins.setter
	def wins(self, wins):
		self.__wins = wins if wins >= 0 else 0

	@property
	def simulations(self):
		return self.__simulations

	@simulations.setter
	def simulations(self, sims):
		self.__simulations = sims if sims >=0 else 0

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

	def add_child(node):
		self.__children.append(node)



class MCTS:

	def __init__(self, startpos, iterations=50):
		self.__startpos = startpos if type(startpos) = chess.Board else None
		self.__root = Node(True)
		self.iterations = iterations

	@property
	def iterations(self):
		return self.__iterations

	@iterations.setter
	def iterations(self, iters):
		self.__iterations = iters if iters > 0 else 1

	def build(self):
		for i in range(self.iterations):
			leaf = self.select_leaf(self.__root)
			leaf = self.expand_tree(leaf)
			winner = self.playout(leaf)
			self.backprop(leaf, winner)


	def select_leaf(self, root):
		curr_node = root
		if not curr_node.children:
			return root

		node_scores = defaultdict(int)
		for child in curr_node.children:
			if not child.children:
				node_scores[child.id] = selection_formula(child)
			else:
				temp = select_leaf(child)
				node_scores[temp.id] = selection_formula(temp)

		# 0-index first time to get top score, second time to get node from (node, score)
		return sorted(node_scores.items(), key=operator.itemgetter[1], reverse=True)[0][0]

	def expand_tree(self, leaf):
		if self.__startpos:
			board = self.__startpos
			moves = list(board.legal_moves)
			rnum = randint(0, len(moves))
			selected_move = moves[rnum]
			# TODO
		else:
			print("MCTS has invalid start position.")

	def playout(self, leaf):
		# TODO
	def backprop(self, leaf, result):
		# TODO
