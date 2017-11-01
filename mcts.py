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
		self.move = None
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
		self.__move = move if type(move) == chess.Move else None

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

	def __init__(self, startpos=chess.Board(), iter_time=100):
		self.startpos = startpos
		self.__root = Node(True, position=chess.Board())
		self.iter_time = iter_time
		self.__states = []

	@property
	def startpos(self):
		return self.__startpos

	@startpos.setter
	def startpos(self, startpos):
		self.__startpos = startpos if type(startpos) == chess.Board else chess.Board()

	def add_state(self, state):
		if type(state) == chess.Board:
			self.__states.append(state)

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
			leaves = self.expand_tree(leaf)
			winners = []
			for new_leaf in leaves:
				winners.append((new_leaf, self.playout(new_leaf)))
			self.backprop(winners)


	def select_leaf(self, root):
		curr_node = root
		if not curr_node.children:
			return root

		node_scores = defaultdict(int)
		for child in curr_node.children:
			if not child.children:
				if not child.position.is_game_over(claim_draw=True):
					node_scores[child] = selection_formula(child)
			else:
				temp = self.select_leaf(child)
				if not temp.position.is_game_over(claim_draw=True):
					node_scores[temp] = selection_formula(temp)

		# 0-index first time to get top score, second time to get node from (node, score)
		return sorted(node_scores.items(), key=operator.itemgetter(1), reverse=True)[0][0]

	def expand_tree(self, leaf):
		if leaf.position:
			new_leaves = []
			board = leaf.position
			moves = list(board.legal_moves)
			if len(moves) == 0:
				print("No moves from position: " + board.fen() + "\n")
			for selected_move in moves:
				new_board = copy.deepcopy(board)
				new_board.push(selected_move)
				new_node = Node(not leaf.color, parent=leaf, position=new_board)
				new_node.move = selected_move
				leaf.children.append(new_node)
				new_leaves.append(new_node)
			return new_leaves
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
		board = copy.deepcopy(leaf.position)
		while not board.is_game_over(claim_draw=True):
			moves = list(board.legal_moves)
			selected_move = choice(moves)
			board.push(selected_move)
		return self.decode(board.result(claim_draw=True))

	def backprop(self, winners):
		for leaf, result in winners:
			while leaf:
				if leaf.color == result:
					leaf.wins += 1
				elif result == DRAW:
					leaf.wins += 0.5
				leaf.simulations += 1
				leaf = leaf.parent

	def best_move(self):
		node = self.__root
		child_scores = []
		for child in node.children:
			child_scores.append((child.move.uci(), (child.wins/child.simulations)))
		return sorted(child_scores, key=operator.itemgetter(1), reverse=True)[0][0]

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

