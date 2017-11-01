import chess
import math
import numpy as np
import argparse
import datetime
import operator
import random
import copy
from chess import pgn, uci
from collections import defaultdict

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
		self.color = color
		self.wins = 0
		self.simulations = 0
		self.color = True
		self.parent = parent
		self.children = []
		self.position = position

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

	def __init__(self, iter_time=2):
		self.__startpos = chess.Board()
		self.__root = Node(True, position=chess.Board())
		self.iter_time = iter_time
		self.__states = []

	def add_state(self, state):
		if type(state) == chess.Board:
			self.__states.append(state)

	@property
	def iter_time(self):
		return self.__iter_time

	@iter_time.setter
	def iter_time(self, time):
		self.__iter_time = time if time > 0 else 2

	def build(self):
		begin = datetime.datetime.utcnow()
		while datetime.datetime.utcnow() - begin < datetime.timedelta(seconds=self.iter_time):
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
				node_scores[child] = selection_formula(child)
			else:
				temp = self.select_leaf(child)
				node_scores[temp] = selection_formula(temp)

		# 0-index first time to get top score, second time to get node from (node, score)
		return sorted(node_scores.items(), key=operator.itemgetter(1), reverse=True)[0][0]

	def expand_tree(self, leaf):
		if leaf.position:
			board = leaf.position
			moves = list(board.legal_moves)
			if len(moves) == 0:
				print("No moves from position: " + board.fen() + "\n")
			if len(moves) > 1:
				rnum = random.randint(0, len(moves)-1)
				selected_move = moves[rnum]
			else:
				selected_move = moves[0]
			board.push(selected_move)
			new_board = copy.deepcopy(board)
			new_node = Node(not leaf.color, parent=leaf, position=new_board)
			leaf.children.append(new_node)
			return new_node
		else:
			print("MCTS has invalid start position.")

	def decode(self, result):
		if result == '1-0':
			print("White Wins!")
			return True
		elif result == '0-1':
			print("Black Wins!")
			return False
		else:
			return DRAW

	def playout(self, leaf):
		board = leaf.position
		while not board.is_game_over(claim_draw=True):
			moves = list(board.legal_moves)
			rnum = random.randint(0, len(moves)-1)
			selected_move = moves[rnum]

			board.push(selected_move)
		return self.decode(board.result(claim_draw=True))

	def backprop(self, leaf, result):
		while leaf:
			if leaf.color == result:
				leaf.wins += 1
			elif result == DRAW:
				leaf.wins += 0.5
			leaf.simulations += 1
			leaf = leaf.parent

	def recurs_print(self, node, file_handle):
		string_set = "{ "
		for child in node.children:
			string_set += str(id(child)) + " [label=\"sims" + str(child.simulations) + "wins" + str(child.wins) + "\"] "
		string_set += "}"
		file_handle.write(str(id(node)) + " [label=\"sims" + str(node.simulations) + "wins" + str(node.wins) + '\"];')
		file_handle.write(str(id(node)) + ' -> ' + string_set + ';\n')
		for child in node.children:
			self.recurs_print(child, file_handle)


	def print_tree(self):
		node = self.__root
		with open("/Users/evanmdoyle/Programming/ChessAI/MCTS.dot", 'w') as f:
			f.write("digraph G { \n")
			self.recurs_print(node, f)
			f.write("}\n")

