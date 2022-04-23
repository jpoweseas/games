from tree_game import TreeGame
from tictactoe import TicTacToe
import ai, reference_ai

import unittest

def for_each_state(root, f, depth_limit):
    queue = [(root, depth_limit)]
    while len(queue) > 0:
        state, depth = queue.pop()
        if depth > 0:
            node_type, node = state.next_node()
            if node_type == 'A' or node_type == 'B':
                children = [state.resolve_choice(choice) for choice in node.values()]
            else:
                print(f'encountered node type {node_type}')
            queue.extend([(s, depth - 1) for s in children][::-1])
        f(state)

def create_tree(l, curr='A', hash_idx=[0]):
    if isinstance(l, str):
        hash_idx[0] += 1
        return { 'type' : 'Terminal', 'winner' : l, 'hash' : hash_idx[0] }
    else:
        next_ = 'B' if curr == 'A' else 'A'
        children = [create_tree(i, curr=next_, hash_idx=hash_idx) for i in l[1:]]
        hash_idx[0] += 1
        return { 'type' : curr, 'score' : l[0], 'children' : children, 'hash' : hash_idx[0] }

class BasicTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_trivial(self):
        tree = create_tree('A')
        state = TreeGame(tree=tree)
        score = ai.negamax(state, alpha=None, beta=None, depth_limit=100)['score']

        self.assertEqual(score, ai.WIN_VALUE)

    def test_simple(self):
        tree = create_tree([0, [-1, 'A', 'B'], [1, 'A', 'A']])
        state = TreeGame(tree=tree)
        score = ai.negamax(state, alpha=None, beta=None, depth_limit=100)['score']

        self.assertEqual(score, ai.WIN_VALUE)

    def test_limited_depth(self):
        tree = create_tree([0, [-1, 'A', 'B'], [1, 'A', 'A']])
        state = TreeGame(tree=tree)
        score = ai.negamax(state, alpha=None, beta=None, depth_limit=1)['score']

        self.assertEqual(score, 1)

    def test_depth_two(self):
        tree = create_tree([0, [-1, [-2, 'B', 'B'], 'B'], [1, [1, 'B', 'A'], [2, 'A', 'B']]])
        state = TreeGame(tree=tree)
        score = ai.negamax(state, alpha=None, beta=None, depth_limit=3)['score']

        self.assertEqual(score, ai.WIN_VALUE)

    def test_possible_cutoff(self):
        tree = create_tree([0, 'tie', [-10, [-100, 'B'], [-10, 'A', 'B']]])
        state = TreeGame(tree=tree)
        result = ai.negamax(state, alpha=None, beta=None, depth_limit=3)
        score = result['score']

        self.assertEqual(score, 0)

    def test_first_four_levels(self):
        def compare_ai_against_reference(state):
            to_play = state.get_player_to_play()
            score = ai.negamax(state, alpha=None, beta=None, depth_limit=100)['score']
            ref_score = reference_ai.negamax(state, depth_limit=100)
            self.assertEqual(score, ref_score, msg='\n'+str(state))

        for_each_state(TicTacToe(), compare_ai_against_reference, 4)

if __name__ == '__main__':
    state = TicTacToe()
    for move in [4, 1, 0]:
        state = state.add_new_mark_and_flip_turn(move)

    ref_score = reference_ai.negamax(state, depth_limit=100, debug_mode=True)

if __name__ == '__main__':
    unittest.main()
    test_first_four_levels()
