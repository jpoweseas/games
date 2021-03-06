import sys, random, unittest

from ai import AIPlayer
from reference_ai import SimpleAIPlayer

LINES = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 4, 8], [2, 4, 6], [0, 3, 6], [1, 4, 7], [2, 5, 8]]
INVERSE_LINES = [[i for (i, line) in enumerate(LINES) if x in line] for x in range(9)]
SYMMETRIES = [
    [2, 1, 0, 5, 4, 3, 8, 7, 6],
    [6, 7, 8, 3, 4, 5, 0, 1, 2],
    [0, 3, 6, 1, 4, 7, 2, 5, 8],
    [8, 5, 2, 7, 4, 1, 6, 3, 0],
    [6, 3, 0, 7, 4, 1, 8, 5, 2],
    [8, 7, 6, 5, 4, 3, 2, 1, 0],
    [2, 5, 8, 1, 4, 7, 0, 3, 6]
]

class TicTacToe:
    WIN_VALUE = 10000
    LOSE_VALUE = -10000
    TIE_VALUE = 0

    LINES = LINES
    INVERSE_LINES = INVERSE_LINES
    SYMMETRIES = SYMMETRIES

    def __init__(self, board=None, a_turn = True, memory = None):
        board = board if board else [None for _ in range(9)]
        self.board = board

        self.a_turn = a_turn

        if not memory:
            num_as = [0 for _ in LINES]
            num_bs = [0 for _ in LINES]

            self.memory = { 'num_as' : num_as, 'num_bs' : num_bs, 'winner' : None, 'hash' : 0, 'sym_hashes' : [0 for _ in range(7)] }
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
            memory['sym_hashes'] = memory['sym_hashes'].copy()
            memory['hash'] = (3 ** space) + memory['hash']
            for sym_idx, sym in enumerate(TicTacToe.SYMMETRIES):
                memory['sym_hashes'][sym_idx] = (3 ** sym[space]) + memory['sym_hashes'][sym_idx]
            for line_idx in TicTacToe.INVERSE_LINES[space]:
                memory['num_as'][line_idx] += 1
                if memory['num_as'][line_idx] == 3:
                    memory['winner'] = 'A'
        elif player_to_play == 'B':
            memory['num_bs'] = memory['num_bs'].copy()
            memory['hash'] = 2 * (3 ** space) + memory['hash']
            for sym_idx, sym in enumerate(TicTacToe.SYMMETRIES):
                memory['sym_hashes'][sym_idx] = 2 * (3 ** sym[space]) + memory['sym_hashes'][sym_idx]
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

    def winner_score(self):
        winner = self.winner()
        if not winner:
            return None
        elif winner == 'A':
            return TicTacToe.WIN_VALUE
        elif winner == 'B':
            return TicTacToe.LOSE_VALUE
        elif winner == 'tie':
            return TicTacToe.TIE_VALUE
        else:
            assert False

    # assumes no winner
    # TODO: we now assume that this does do winners properly
    def old_evaluate(self):
        winner_score = self.winner_score()
        if winner_score:
            return winner_score
        return self.open_lines('A') - self.open_lines('B')

    # assumes no winner
    # TODO: Test it's the same
    def evaluate(self):
        winner_score = self.winner_score()
        if winner_score:
            return winner_score
        return self.memory['num_bs'].count(0) - self.memory['num_as'].count(0)

    # TODO: make this faster, make this version to_reversible_format
    def old_hash(self):
        return sum([(0 if self.board[i] is None else 1 if self.board[i] == 'A' else 2) * (3 ** i) for i in range(9)])

    def hash(self):
        return self.memory['hash']

    def old_symmetric_hashes(self):
        out = [self.hash()]
        for sym in TicTacToe.SYMMETRIES:
            out.append(sum([(0 if self.board[sym[i]] is None else 1 if self.board[sym[i]] == 'A' else 2) * (3 ** i) for i in range(9)]))
        return out

    def symmetric_hashes(self):
        return self.memory['sym_hashes']

    def unique_hash(self):
        hashes = self.symmetric_hashes()
        return min(hashes)

    def to_reversible_format(self):
        return str(self.hash())

    def from_reversible_format(fmt):
        fmt = int(fmt)
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

    def test_hash(self):
        init_state = TicTacToe()

        # TODO: rewrite to use for_each_state
        states_to_check = [init_state]
        while len(states_to_check) > 0:
            state = states_to_check.pop()

            node_type, node = state.next_node()
            if node_type == 'Terminal':
                continue

            self.assertEqual(state.old_hash(), state.hash())
            states_to_check.extend([state.resolve_choice(choice) for choice in node.values()])

if __name__ == '__main__':
    unittest.main()
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        pass
    elif len(sys.argv) > 1 and sys.argv[1] == 'sym':
        state = TicTacToe()
        for move in [4, 1, 0, 8]:
            state = state.add_new_mark_and_flip_turn(move)
        print(state)
        for sym_hash in state.symmetric_hashes():
            # Uses the fact that hash = rev format for TicTacToe
            new_state = TicTacToe.from_reversible_format(sym_hash)
            print(new_state)

    elif len(sys.argv) > 1 and sys.argv[1] == 'ref':
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
        ai.choose_move(choices, state, debug_mode=True, depth_limit=6)
