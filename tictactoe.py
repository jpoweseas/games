import sys, random, unittest

from ai import AIPlayer
from reference_ai import SimpleAIPlayer

LINES = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 4, 8], [2, 4, 6], [0, 3, 6], [1, 4, 7], [2, 5, 8]]
INVERSE_LINES = [[i for (i, line) in enumerate(LINES) if x in line] for x in range(9)]

class TicTacToe:
    LINES = LINES
    INVERSE_LINES = INVERSE_LINES

    def __init__(self, board=None, a_turn = True, memory = None):
        board = board if board else [None for _ in range(9)]
        self.board = board

        self.a_turn = a_turn

        if not memory:
            num_as = [0 for _ in LINES]
            num_bs = [0 for _ in LINES]

            self.memory = { 'num_as' : num_as, 'num_bs' : num_bs, 'winner' : None }
        else:
            self.memory = memory

    def get_player_to_play(self):
        return 'A' if self.a_turn else 'B'

    def old_winner(self):
        for line in TicTacToe.LINES:
            board_line = [self.board[i] for i in line]
            if board_line[0] is not None and board_line[0] == board_line[1] and board_line[1] == board_line[2]:
                return board_line[0]

        if None not in self.board:
            return 'tie'

    def winner(self):
        winner = self.memory['winner']
        if winner:
            return winner
        elif None not in self.board:
            return 'tie'
        else:
            return None

    # assumes space is valid
    def add_new_mark_and_flip_turn(self, space):
        board = self.board.copy()
        player_to_play = self.get_player_to_play()
        board[space] = self.get_player_to_play()

        memory = self.memory.copy()
        if player_to_play == 'A':
            memory['num_as'] = memory['num_as'].copy()
            for line_idx in TicTacToe.INVERSE_LINES[space]:
                memory['num_as'][line_idx] += 1
                if memory['num_as'][line_idx] == 3:
                    memory['winner'] = 'A'
        elif player_to_play == 'B':
            memory['num_bs'] = memory['num_bs'].copy()
            for line_idx in TicTacToe.INVERSE_LINES[space]:
                memory['num_bs'][line_idx] += 1
                if memory['num_bs'][line_idx] == 3:
                    memory['winner'] = 'B'

        return TicTacToe(board, a_turn = not self.a_turn, memory = memory)

    def next_node(self):
        open_spaces = [i for i in range(9) if self.board[i] is None]

        winner = self.winner()
        if winner is not None:
            return 'Terminal', winner
        elif self.a_turn:
            return 'A', {str(i) : i for i in open_spaces}
        else:
            return 'B', {str(i) : i for i in open_spaces}

    def resolve_choice(self, choice):
        space = choice
        return self.add_new_mark_and_flip_turn(space)

    def other_player(player):
        if player == 'A':
            return 'B'
        elif player == 'B':
            return 'A'
        else:
            assert False

    def open_lines(self, player):
        open_lines = 0
        other_player = TicTacToe.other_player(player)

        for line in TicTacToe.LINES:
            board_line = [self.board[i] for i in line]
            if other_player not in board_line:
                open_lines += 1

        return open_lines

    # assumes no winner
    def old_evaluate(self):
        return self.open_lines('A') - self.open_lines('B')

    # assumes no winner
    # TODO: Test it's the same
    def evaluate(self):
        return self.memory['num_bs'].count(0) - self.memory['num_as'].count(0)

    # TODO: make this faster, make this version to_reversible_format
    def hash(self):
        return sum([(0 if self.board[i] is None else 1 if self.board[i] == 'A' else 2) * (3 ** i) for i in range(9)])

    def to_reversible_format(self):
        return str(self.hash())

    def from_reversible_format(fmt):
        board = []

        num_pieces = 0
        for i in range(9):
            value = fmt % 3
            fmt = fmt // 3

            if value == 0:
                board.append(None)
            elif value == 1:
                board.append('A')
                num_pieces += 1
            elif value == 2:
                board.append('B')
                num_pieces += 1

        assert (fmt == 0)

        return TicTacToe(board=board, a_turn=(num_pieces % 2 == 0))

    def __repr__(self):
        def print_cell(x):
            if x is None:
                return ' '
            elif x == 'A':
                return 'X'
            elif x == 'B':
                return 'O'
            else:
                assert False

        return '\n-----\n'.join([('|'.join([print_cell(x) for x in self.board[(3 * i):(3 * i + 3)]])) for i in range(3)])

    def print_for_human_input(self):
        def print_cell(x, i):
            if x is None:
                return f'{i}'
            elif x == 'A':
                return 'X'
            elif x == 'B':
                return 'O'
            else:
                assert False

        print('\n-----\n'.join([('|'.join([print_cell(x, 3*i + j) for j, x in enumerate(self.board[(3 * i):(3 * i + 3)])])) for i in range(3)]))

# Unused
class RandomAIPlayer:
    def __init__(self, playing_as):
        pass

    def choose_move(self, choices, current_state, debug_mode=False, depth_limit=6):
        return random.choice(choices)

class Tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_reversible_format(self):
        init_state = TicTacToe()

        # TODO: rewrite to use for_each_state
        states_to_check = [init_state]
        while len(states_to_check) > 0:
            state = states_to_check.pop()

            node_type, node = state.next_node()
            if node_type == 'Terminal':
                continue

            self.assertEqual(state.board, TicTacToe.from_reversible_format(state.to_reversible_format()).board)
            states_to_check.extend([state.resolve_choice(choice) for choice in node.values()])

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        unittest.main()
    if len(sys.argv) > 1 and sys.argv[1] == 'ref':
        state = TicTacToe()
        for move in [4, 1, 0]:
            state = state.add_new_mark_and_flip_turn(move)

        ref_ai = SimpleAIPlayer(playing_as=True)
        node_type, choices = state.next_node()
        ref_ai.choose_move(choices, state, debug_mode=True, depth_limit=100)
    else:
        state = TicTacToe()
        # for move in [4, 1, 0]:
        #     state = state.add_new_mark_and_flip_turn(move)
        ai = AIPlayer(playing_as='A')
        node_type, choices = state.next_node()
        ai.choose_move(choices, state, debug_mode=True, depth_limit=100)
