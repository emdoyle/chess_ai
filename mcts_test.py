import mcts
import chess

tree = mcts.MCTS()
tree.build()
tree.print_tree()