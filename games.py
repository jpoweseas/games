import copy

WIN_VALUE = 10000
LOSE_VALUE = -10000
TIE_VALUE = 0

class TicTacToe:
    LINES = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 4, 8], [2, 4, 6], [0, 3, 6], [1, 4, 7], [2, 5, 8]]

    def __init__(self, board=None, a_turn = True):
        board = board if board else [None for _ in range(9)]
        self.board = board

        self.a_turn = a_turn

    def get_player_to_play(self):
        return 'A' if self.a_turn else 'B'

    def winner(self):
        for line in TicTacToe.LINES:
            board_line = [self.board[i] for i in line]
            if board_line[0] is not None and board_line[0] == board_line[1] and board_line[1] == board_line[2]:
                return board_line[0]

        if None not in self.board:
            return 'tie'

    def add_new_mark_and_flip_turn(self, space):
        board = self.board.copy()
        board[space] = self.get_player_to_play()
        return TicTacToe(board, a_turn = not self.a_turn)

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
    def evaluate(self):
        return self.open_lines('A') - self.open_lines('B')

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

class ConnectFour:
    def __init__(self, board = None, a_turn = True):
        board = board if board else [[] for _ in range(7)]
        self.board = board

        self.a_turn = a_turn

    def get_player_to_play(self):
        return 'A' if self.a_turn else 'B'

    def get_piece(self, col_index, row_index):
        if col_index >= 0 and col_index < 7 and row_index < len(self.board[col_index]) and row_index >= 0:
            return self.board[col_index][row_index]
        else:
            return None

    # TODO-someday: Rewrite using the explicit 69 winning patterns from below
    def winner(self):
        def four_in_a_row(l):
            equal_to = None
            count = 0
            for x in l:
                if x == equal_to and x is not None:
                    count += 1
                    if count == 4:
                        return equal_to
                else:
                    count = 1
                    equal_to = x
            return None

        for column in self.board:
            winner = four_in_a_row(column)
            if winner:
                # print('col')
                return winner

        for row_index in range(6):
            row = [self.get_piece(col_index, row_index) for col_index in range(7)]
            winner = four_in_a_row(row)
            if winner:
                # print('row')
                return winner

        # Diagonals
        for row_index in range(-4, 7):
            row = [self.get_piece(col_index, row_index + col_index) for col_index in range(7)]
            winner = four_in_a_row(row)
            if winner:
                # print('diag up-left')
                return winner

        for row_index in range(10):
            row = [self.get_piece(col_index, row_index - col_index) for col_index in range(7)]
            winner = four_in_a_row(row)
            if winner:
                # print('diag up-right')
                return winner

        if all([None not in col and len(col) > 0 for col in self.board]):
            return 'tie'

    def four_combos(N):
        # partials[i] contains all partials with length i and numbers <= n
        combo_size = 4

        partials = [[] for _ in range(combo_size)]
        for n in range(N):
            for i in range(1, combo_size)[::-1]:
                partials[i].extend([l + [n] for l in partials[i - 1]])
                partials[0].append([n])
        return partials[-1]

        # for i in range(N):
        #     finals += [l + [i] for l in three_partials]
        #     three_partials += [l + [i] for l in two_partials]
        #     two_partials += [l + [i] for l in one_partials]
        #     one_partials.append([i])

        # return finals

    def place_possibly_hovering(self, col_index, row_index):
        # Check that the column is tall enough
        if row_index < len(self.board[col_index]):
            self.board[col_index][row_index] = 'A'
        else:
            # Add blank spots after the current end of the column
            spots_to_add = row_index - len(self.board[col_index])
            self.board[col_index].extend([None for _ in range(spots_to_add)])
            self.board[col_index].append('A')

    def simple_col_winner_test():
        state = ConnectFour()
        state.place_possibly_hovering(0, 0)
        state.place_possibly_hovering(0, 1)
        state.place_possibly_hovering(0, 2)
        state.place_possibly_hovering(0, 3)

        assert state.winner() == 'A'

    def simple_row_winner_test():
        state = ConnectFour()
        state.place_possibly_hovering(0, 0)
        state.place_possibly_hovering(1, 0)
        state.place_possibly_hovering(2, 0)
        state.place_possibly_hovering(3, 0)

        assert state.winner() == 'A'

    def simple_up_right_winner_test():
        state = ConnectFour()
        state.place_possibly_hovering(0, 0)
        state.place_possibly_hovering(1, 1)
        state.place_possibly_hovering(2, 2)
        state.place_possibly_hovering(3, 3)

        assert state.winner() == 'A'

    def second_up_right_winner_test():
        state = ConnectFour()
        state.place_possibly_hovering(6, 6)
        state.place_possibly_hovering(5, 5)
        state.place_possibly_hovering(4, 4)
        state.place_possibly_hovering(3, 3)

        assert state.winner() == 'A'

    def simple_up_left_winner_test():
        state = ConnectFour()
        state.place_possibly_hovering(3, 0)
        state.place_possibly_hovering(2, 1)
        state.place_possibly_hovering(1, 2)
        state.place_possibly_hovering(0, 3)

        assert state.winner() == 'A'

    def second_up_left_winner_test():
        state = ConnectFour()
        state.place_possibly_hovering(3, 6)
        state.place_possibly_hovering(4, 5)
        state.place_possibly_hovering(5, 4)
        state.place_possibly_hovering(6, 3)

        assert state.winner() == 'A'

    def test_num_winners():
        num_winners = 0
        winners = []
        for combo in ConnectFour.four_combos(42):
            state = ConnectFour()
            for i in combo:
                row_index = i // 7
                col_index = i % 7
                state.place_possibly_hovering(col_index, row_index)

            winner = state.winner()
            if winner == 'A':
                num_winners += 1
                winners.append(state.board)

        # 7 columns, 3 different winning jawns on each col
        # 6 rows, 4 " on each row
        # Diagonals going up and to the right can start anywhere that isn't within 3
        # of the top or right side. So they can start in one of 3 * 4 places
        # By symmetry, same thing for the diagonals going up and to the left
        # 21 + 24 + 12 + 12 = 69
        #print(num_winners)
        #print(winners[:10])
        assert num_winners == 69

    def add_new_mark_and_flip_turn(self, col_index):
        board = copy.deepcopy(self.board)
        if len(board[col_index]) < 6:
            board[col_index].append(self.get_player_to_play())
        else:
            assert False

        return ConnectFour(board, a_turn = not self.a_turn)

    def next_node(self):
        open_columns = [i for i in range(7) if len(self.board[i]) < 6]

        winner = self.winner()
        if winner is not None:
            return 'Terminal', winner
        elif self.a_turn:
            return 'A', {str(i) : i for i in open_columns}
        else:
            return 'B', {str(i) : i for i in open_columns}

    def resolve_choice(self, choice):
        return self.add_new_mark_and_flip_turn(choice)

    def evaluate(self):
        lasts = [col[-1] for col in self.board if len(col) > 0]
        lefts = [self.get_piece(col_index - 1, len(self.board[col_index])) for col_index in range(7)]
        rights = [self.get_piece(col_index + 1, len(self.board[col_index])) for col_index in range(7)]

        considered = lasts + lefts + rights

        return considered.count('A') - considered.count('B')

    def __repr__(self):
        def print_cell(col_num, row_num):
            x = self.get_piece(col_num, row_num)
            if x is None:
                return ' '
            elif x == 'A':
                return 'X'
            elif x == 'B':
                return 'O'
            else:
                assert False

        return '\n'.join(['|' + ''.join([print_cell(col_num, row_num) for col_num in range(7)]) + '|' for row_num in range(6)[::-1]]) + '\n' + '-' * 9 + '\n ' + ''.join([str(i) for i in range(7)]) + ' '

    def print_for_human_input(self):
        print(self)

class HumanPlayer:
    def __init__(self, playing_as):
        self.playing_as = playing_as

    def choose_move(self, choices, current_state, debug_mode=False):
        while True:
            current_state.print_for_human_input()

            user_input = input('\nChoice: ')

            if user_input.split()[0] == 'v' or user_input.split()[0] == 'view':
                choice_to_view = user_input.split()[1]
                if choice_to_view in choices:
                    print(current_state.resolve_choice(choices[choice_to_view]))
                    input('Press <enter> to continue')
                else:
                    print(f'Choice of {user_input} could not be parsed\n')

            else:
                if user_input in choices:
                    return current_state.resolve_choice(choices[user_input])
                else:
                    print(f'Choice of {user_input} could not be parsed\n')

def resolve_random(state_with_probability_list, debug_mode=False, depth_limit=0):
    if debug_mode:
        print('unimplemented')
        assert False
    return sum([prob * negamax(state, depth_limit=(depth_limit - 1)) for state in state_with_probability_list])

def evaluate_player_node(state_choices, invert, debug_mode=False, depth_limit=0):
    invert_mult = -1 if invert else 1
    max_value_so_far = invert_mult * negamax(state_choices[0], debug_mode, depth_limit=(depth_limit - 1))
    best_state = state_choices[0]

    for state in state_choices[1:]:
        value = invert_mult * negamax(state, debug_mode=debug_mode, depth_limit=(depth_limit - 1))
        if value > max_value_so_far:
            max_value_so_far = value
            best_state = state

    return { 'value' : invert_mult * max_value_so_far, 'state' : best_state }

# Returns A's value of the subgame
def negamax(state, debug_mode=False, depth_limit=0):
    if depth_limit < 0:
        assert False
    elif depth_limit == 0:
        return state.evaluate()

    node_type, node = state.next_node()

    if debug_mode:
        print('\nResolving state:')
        print(state)
        print('\n')

    if node_type == "Random":
        if debug_mode:
            input('Resolving random node. Press <enter> to continue')

        return resolve_random(state, debug_mode, depth_limit=depth_limit)

    elif node_type ==  "Terminal":
        if debug_mode:
            print(f'Winner is {node}. Press <enter> to continue')

        if node == 'A':
            return WIN_VALUE
        elif node == 'B':
            return LOSE_VALUE
        elif node == 'tie':
            return TIE_VALUE
        else:
            assert False

    elif node_type == 'A' or node_type == 'B':
        continue_in_debug_mode = None
        if debug_mode:
            while continue_in_debug_mode is None:
                user_input = input(f'{node_type} to play. [skip] or [drill]: ')
                if user_input == 's' or user_input == 'skip':
                    continue_in_debug_mode = False
                elif user_input == 'd' or user_input == 'drill':
                    continue_in_debug_mode = True

        state_choices = [state.resolve_choice(choice) for choice in node.values()]
        result = evaluate_player_node(state_choices, invert=(node_type == 'B'), debug_mode=(continue_in_debug_mode if debug_mode else False), depth_limit=depth_limit)

        if debug_mode and not continue_in_debug_mode:
            input(f'\nEvaluated this node as {(result["value"])}. Press enter to continue')

        return result['value']

    else:
        assert False

class AIPlayer:
    def __init__(self, playing_as):
        self.playing_as = playing_as

    def choose_move(self, choices, current_state, debug_mode=False):
        if debug_mode:
            print('Current state:')
            print(current_state)

        state_choices = [current_state.resolve_choice(choice) for choice in choices.values()]
        return evaluate_player_node(state_choices, invert=(self.playing_as == 'B'), debug_mode=debug_mode, depth_limit=5)['state']

def play_game(state, a_player, b_player):
    while True:
        node_type, node = state.next_node()

        if node_type == "Random":
            print('unimplemented')
            assert False
        elif node_type ==  "Terminal":
            print(f'Winner is {node}!')
            return
        elif node_type == 'A':
            state = a_player.choose_move(node, state, debug_mode = False)
        elif node_type == 'B':
            state = b_player.choose_move(node, state, debug_mode = False)
        else:
            assert False

# play_game(TicTacToe(), AIPlayer('A'), HumanPlayer('B'))
play_game(ConnectFour(), AIPlayer('A'), AIPlayer('B'))

## All pass
# ConnectFour.simple_col_winner_test()
# ConnectFour.simple_row_winner_test()
# ConnectFour.simple_up_right_winner_test()
# ConnectFour.second_up_right_winner_test()
# ConnectFour.simple_up_left_winner_test()
# ConnectFour.second_up_left_winner_test()
# ConnectFour.test_num_winners()
# assert len(ConnectFour.four_combos(42)) == 111930
