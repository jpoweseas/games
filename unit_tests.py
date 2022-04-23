from tree_game import TreeGame
from games import AIPlayer
from ai import negamax, WIN_VALUE

import unittest

def create_tree(l, curr='A'):
    if isinstance(l, str):
        return { 'type' : 'Terminal', 'winner' : l }
    else:
        next_ = 'B' if curr == 'A' else 'A'
        children = [create_tree(i, curr=next_) for i in l[1:]]
        return { 'type' : curr, 'score' : l[0], 'children' : children }


class BasicTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_trivial(self):
        tree = create_tree('A')
        state = TreeGame(tree=tree)
        score = negamax(state, alpha=None, beta=None, depth_limit=100)['score']

        self.assertEqual(score, WIN_VALUE)

    def test_simple(self):
        tree = create_tree([0, [-1, 'A', 'B'], [1, 'A', 'A']])
        state = TreeGame(tree=tree)
        score = negamax(state, alpha=None, beta=None, depth_limit=100)['score']

        self.assertEqual(score, WIN_VALUE)

    def test_limited_depth(self):
        tree = create_tree([0, [-1, 'A', 'B'], [1, 'A', 'A']])
        state = TreeGame(tree=tree)
        score = negamax(state, alpha=None, beta=None, depth_limit=1)['score']

        self.assertEqual(score, 1)

    def test_depth_two(self):
        tree = create_tree([0, [-1, [-2, 'B', 'B'], 'B'], [1, [1, 'B', 'A'], [2, 'A', 'B']]])
        state = TreeGame(tree=tree)
        score = negamax(state, alpha=None, beta=None, depth_limit=3)['score']

        self.assertEqual(score, WIN_VALUE)

    def test_possible_cutoff(self):
        tree = create_tree([0, 'tie', [-10, [-100, 'B'], [-10, 'A', 'B']]])
        state = TreeGame(tree=tree)
        result = negamax(state, alpha=None, beta=None, depth_limit=3)
        score = result['score']

        self.assertEqual(score, 0)

    # def test_dumb_bug(self):
    #     tree = create_tree([0])

if __name__ == '__main__':
    unittest.main()
