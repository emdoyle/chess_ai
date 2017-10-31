import chess
import math
import numpy as np
import argparse
import time
import operator
import random
from chess import pgn, uci

global_id = 0

DRAW = 'draw'

def total_sims_at_depth(node):
	sims = node.simulations
	parent = node.parent
	for child in parent.children:
		if child != node:
			sims += child.simulations
	return sims


def selection_formula(node):
	w = node.wins
	n = node.simulations
	N = total_sims_at_depth(node)
	c = math.sqrt(2)
	term1 = float(w/n)
	term2 = c*math.sqrt(math.log(N)/n)
	return term1 + term2

class Node:

	def __init__(self, color, parent=None, position=None):
		self.gen_id()
		self.color = color
		self.wins = 0
		self.simulations = 0
		self.color = True
		self.parent = parent
		self.children = []
		self.position = position

	def gen_id(self):
		global_id += 1
		self.__id = global_id

	def id(self):
		return self.__id

	@property
	def position(self):
		return self.__position

	@position.setter
	def position(self, position):
		self.__position = position if type(position) == chess.Board else None

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
		self.__root = Node(True, position=chess.Board())
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
			if (winner == DRAW):
				winner = 0.5
			self.backprop(leaf, float(winner))


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
		if leaf.parent.position:
			board = leaf.parent.position
			moves = list(board.legal_moves)
			rnum = randint(0, len(moves))
			selected_move = moves[rnum]
			
			board.push(selected_move)
			new_node = Node(not leaf.color, parent=leaf, position=board)
		else:
			print("MCTS has invalid start position.")

	def decode(self, result):
		if result == '1-0':
			return True
		elif result == '0-1':
			return False
		else:
			return DRAW

	def playout(self, leaf):
		board = leaf.position
		while not board.is_game_over(claim_draw=True):
			moves = list(board.legal_moves)
			rnum = randint(0, len(moves))
			selected_move = moves[rnum]

			board.push(selected_move)

		return self.decode(board.result(claim_draw=True))

	def backprop(self, leaf, result):
		while leaf.parent:
			leaf.wins += result
			leaf.simulations += 1
			leaf = leaf.parent

