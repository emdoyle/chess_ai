import mcts
import chess

tree = mcts.MCTS()
tree.build()
print(tree.best_move())
tree.print_tree()