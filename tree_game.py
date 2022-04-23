# regression testing of core logic:
# - always (?) compare to basic negamax implementation
# - build random game trees and test that both come up with the same outcome
#   - need to build random game trees
#   - run standard AIs on these
#   - test same output
# - also some unit tests for specific changes
#   - build specific game trees

# - where do custom evaluation functions happen?

import random
from random import randint, choice

WIN_VALUE = 10000
LOSE_VALUE = -10000

class TreeGame:
    def generate_tree(curr_depth):
        if random.random() < (curr_depth - 2) * 0.2:
            return { 'type' : 'Terminal', 'winner' : choice(['A', 'B', 'tie']), 'hash' : randint(0, 2147483647)}
        else:
            children = [TreeGame.generate_tree(curr_depth + 1) for _ in range(randint(2, 8))]
            return { 'type' : choice(['A', 'B']), 'score' : randint(-100, 100), 'children' : children, 'hash' : randint(0, 2147483647) }

    # nodes look like:
    # { type : 'A', score : 3, children : [] }
    # ...
    # { type : 'Terminal', winner = 'A' }
    def __init__(self, tree=None, seed=None):
        if tree:
            self.tree = tree
        else:
            if seed:
                random.seed(seed)
            else:
                assert False
            self.tree = TreeGame.generate_tree(curr_depth=0)

    def next_node(self):
        node_type = self.tree['type']
        if node_type == 'A':
            return 'A', {str(i) : i for i in range(len(self.tree['children']))}
        elif node_type == 'B':
            return 'B', {str(i) : i for i in range(len(self.tree['children']))}
        elif node_type == 'Terminal':
            return 'Terminal', self.tree['winner']
        else:
            assert False

    def resolve_choice(self, i):
        return TreeGame(tree = self.tree['children'][i].copy())

    def winner(self):
        if self.tree['type'] == 'Terminal':
            return self.tree['winner']
        else:
            return None

    def evaluate(self):
        if self.tree['type'] == 'Terminal':
            return (WIN_VALUE if self.tree['winner'] == 'A' else
                    LOSE_VALUE if self.tree['winner'] == 'B' else
                    0 if self.tree['winner'] == 'tie' else '!!!'
                    )
        else:
            return self.tree['score']

    def hash(self):
        return self.tree['hash']

    def __repr__(self):
        return str(self.tree)

    def print_for_human_input(self):
        print('', self.tree)

