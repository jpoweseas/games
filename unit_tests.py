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
            elif node_type == 'Terminal':
                pass
            else:
                print(f'encountered node type {node_type}')
            queue.extend([(s, depth - 1) for s in children][::-1])
        f(state)

def remove_this_create_tree(l, curr='A', hash_idx=[0]):
    if isinstance(l, str):
        hash_idx[0] += 1
        return { 'type' : 'Terminal', 'winner' : l, 'hash' : hash_idx[0] }
    else:
        next_ = 'B' if curr == 'A' else 'A'
        children = [create_tree(i, curr=next_, hash_idx=hash_idx) for i in l[1:]]
        hash_idx[0] += 1
        return { 'type' : curr, 'score' : l[0], 'children' : children, 'hash' : hash_idx[0] }

def has_loop(tree, root):
    nodes_visited = []
    queue = [0]
    for idx in queue:
        if idx in nodes_visited:
            print(tree)
            print(idx)
            assert False

        nodes_visited.append(idx)

        if 'children' in tree[idx]:
            queue.extend(tree[idx]['children'])

    for idx in tree.keys():
        if idx not in nodes_visited:
            print(tree)
            print(idx)
            assert False

    return False

def create_tree(l):
    tree = []

    def loop(l, curr):
        if isinstance(l, str):
            tree.append({ 'type' : 'Terminal', 'winner' : l })
            return len(tree) - 1
        else:
            next_ = 'B' if curr == 'A' else 'A'
            idx = len(tree)
            node = tree.append({ 'type' : curr, 'score' : l[0], 'children' : None })
            children = [loop(i, next_) for i in l[1:]]
            tree[idx]['children'] = children
            return idx

    loop(l, 'A')
    tree = { i : node for i, node in enumerate(tree)}

    has_loop(tree, 0)

    return TreeGame(tree=tree, root=0)

class BasicTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_trivial(self):
        state = create_tree('A')
        score = ai.negamax(state, alpha=None, beta=None, depth_limit=100)

        self.assertEqual(score, TreeGame.WIN_VALUE)

    def test_simple(self):
        state = create_tree([0, [-1, 'A', 'B'], [1, 'A', 'A']])
        score = ai.negamax(state, alpha=None, beta=None, depth_limit=100)

        self.assertEqual(score, TreeGame.WIN_VALUE)

    def test_limited_depth(self):
        state = create_tree([0, [-1, 'A', 'B'], [1, 'A', 'A']])
        score = ai.negamax(state, alpha=None, beta=None, depth_limit=1)

        self.assertEqual(score, 1)

    def test_depth_two(self):
        state = create_tree([0, [-1, [-2, 'B', 'B'], 'B'], [1, [1, 'B', 'A'], [2, 'A', 'B']]])
        score = ai.negamax(state, alpha=None, beta=None, depth_limit=3)

        self.assertEqual(score, TreeGame.WIN_VALUE)

    def test_possible_cutoff(self):
        state = create_tree([0, 'tie', [-10, [-100, 'B'], [-10, 'A', 'B']]])
        result = ai.negamax(state, alpha=None, beta=None, depth_limit=3)
        score = result

        self.assertEqual(score, 0)

    def test_megadeath(self):
        tree = {
            0 : { 'type' : 'A', 'score' : 0, 'children' : [1, 2] },
            1 : { 'type' : 'B', 'score' : 1, 'children' : [3, 4] },
            2 : { 'type' : 'B', 'score' : -1, 'children' : [4] },
            3 : { 'type' : 'Terminal', 'winner' : 'B' },
            4 : { 'type' : 'A', 'score' : 2, 'children' : [8] },
            5 : { 'type' : 'Terminal', 'winner' : 'tie' },
            6 : { 'type' : 'B', 'score' : -2, 'children' : [7] },
            7 : { 'type' : 'Terminal', 'winner' : 'A' },
            8 : { 'type' : 'A', 'score': -3, 'children' : [5, 6] },
        }

        state = TreeGame(tree=tree, root=0)
        node_type, choices = state.next_node()
        result = ai.negamax(state, alpha=None, beta=None, depth_limit=100)
        score = result

        self.assertEqual(score, 10000)

    # def test_first_four_levels(self):
    #     def compare_ai_against_reference(state):
    #         to_play = state.get_player_to_play()
    #         score = ai.negamax(state, alpha=None, beta=None, depth_limit=6)
    #         ref_score = reference_ai.negamax(state, depth_limit=6)
    #         self.assertEqual(score, ref_score, msg='\n'+str(state))

    #     for_each_state(TicTacToe(), compare_ai_against_reference, 7)

if __name__ == '__main__':
    unittest.main()
    # test_first_four_levels()

    # tree = {
    #     0 : { 'type' : 'A', 'score' : 0, 'children' : [1, 2] },
    #     1 : { 'type' : 'B', 'score' : 1, 'children' : [3, 4] },
    #     2 : { 'type' : 'B', 'score' : -1, 'children' : [4] },
    #     3 : { 'type' : 'Terminal', 'winner' : 'B' },
    #     4 : { 'type' : 'A', 'score' : 2, 'children' : [8] },
    #     5 : { 'type' : 'Terminal', 'winner' : 'tie' },
    #     6 : { 'type' : 'B', 'score' : -2, 'children' : [7] },
    #     7 : { 'type' : 'Terminal', 'winner' : 'A' },
    #     8 : { 'type' : 'A', 'score': -3, 'children' : [5, 6] },
    # }

    # state = TreeGame(tree=tree, root=0)
    # node_type, choices = state.next_node()
    # player = ai.AIPlayer('A')
    # player.choose_move(choices, state, debug_mode=True)
