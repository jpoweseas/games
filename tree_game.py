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

class TreeGame:
    WIN_VALUE = 10000
    LOSE_VALUE = -10000
    TIE_VALUE = 0

    def old_generate_tree(curr_depth):
        print('generate_tree broken')
        if random.random() < (curr_depth - 2) * 0.2:
            return { 'type' : 'Terminal', 'winner' : choice(['A', 'B', 'tie']), 'hash' : randint(0, 2147483647)}
        else:
            children = [TreeGame.generate_tree(curr_depth + 1) for _ in range(randint(2, 8))]
            return { 'type' : choice(['A', 'B']), 'score' : randint(-100, 100), 'children' : children, 'hash' : randint(0, 2147483647) }

    # old nodes look like:
    # { type : 'A', score : 3, children : [] }
    # ...
    # { type : 'Terminal', winner = 'A' }
    # new nodes look like:
    # { 0 : { type : 'A', score : 3, children : [1] },
    #   1 : { type : 'Terminal', winner = 'A' },
    #   ...
    # }
    def __init__(self, tree=None, root=None, seed=None):
        if tree is not None:
            self.tree = tree
            if root is None:
                print('need to pass root with tree')
                assert False
            self.current_node = root
        else:
            if seed:
                random.seed(seed)
            else:
                assert False
            assert False
            self.tree = TreeGame.generate_tree(curr_depth=0)

    def get_node(self, node_id):
        return self.tree[node_id]

    def get_current_node(self):
        return self.get_node(self.current_node)

    def next_node(self):
        node = self.get_current_node()
        node_type = node['type']
        if node_type == 'A':
            return 'A', {str(i) : i for i in node['children']}
        elif node_type == 'B':
            return 'B', {str(i) : i for i in node['children']}
        elif node_type == 'Terminal':
            return 'Terminal', node['winner']
        else:
            assert False

    def resolve_choice(self, node_id):
        return TreeGame(tree=self.tree, root=node_id)

    def winner(self):
        node = self.get_current_node()
        if node['type'] == 'Terminal':
            return node['winner']
        else:
            return None

    def evaluate(self):
        node = self.get_current_node()
        if node['type'] == 'Terminal':
            return (TreeGame.WIN_VALUE if node['winner'] == 'A' else
                    TreeGame.LOSE_VALUE if node['winner'] == 'B' else
                    0 if node['winner'] == 'tie' else '!!!'
                    )
        else:
            return node['score']

    def hash(self):
        return self.current_node

    # stupid
    def to_reversible_format(self):
        node = self.get_current_node()
        return f'{node["type"]}{self.current_node}'

    def __repr__(self):
        return f'current_node: {self.current_node}\n' + \
        '\n'.join([f'{i}: {str(node)}' for i, node in self.tree.items()])

    def print_for_human_input(self):
        print('', node)
