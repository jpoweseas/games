import copy, csv

def read_winners(filename='connect_four_winners.csv'):
    with open(filename) as f:
        return [[(int(i) // 7, int(i) % 7) for i in line] for line in csv.reader(f)]

WIN_VALUE = 10000
LOSE_VALUE = -10000
TIE_VALUE = 0

class ConnectFour:
    WINNERS = read_winners()
    INVERSE_WINNERS = [[i for (i, line) in enumerate(WINNERS) if x in line] for x in range(42)]

    def __init__(self, board = None, a_turn = True, memory=None):
        if not board:
            board = [[] for _ in range(7)]
            # memory = { 'num_as' : num_as, 'num_bs', num_bs, 'winner' : None }
        elif not memory:
            print('Cannot pass in board and not memory')
            assert False

        self.board = board
        self.a_turn = a_turn

    # ACCESSORS

    def get_player_to_play(self):
        return 'A' if self.a_turn else 'B'

    def get_piece(self, col_index, row_index):
        if col_index >= 0 and col_index < 7 \
           and row_index < len(self.board[col_index]) and row_index >= 0:
            return self.board[col_index][row_index]
        else:
            return None

    def place_possibly_hovering(self, col_index, row_index):
        # Check that the column is tall enough
        if row_index < len(self.board[col_index]):
            self.board[col_index][row_index] = 'A'
        else:
            # Add blank spots after the current end of the column
            spots_to_add = row_index - len(self.board[col_index])
            self.board[col_index].extend([None for _ in range(spots_to_add)])
            self.board[col_index].append('A')

    def open_columns(self):
        return [i for i in range(7) if len(self.board[i]) < 6]

    # EVALUATION

    def winner(self):
        for l in ConnectFour.WINNERS:
            first_piece = self.get_piece(l[0][1], l[0][0])
            if first_piece is not None \
               and first_piece == self.get_piece(l[1][1], l[1][0]) \
               and first_piece == self.get_piece(l[2][1], l[2][0]) \
               and first_piece == self.get_piece(l[3][1], l[3][0]):
                return first_piece

    def old_winner(self):
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

        if all([len(col) == 6 for col in self.board]):
            return 'tie'

    def old_evaluate(self):
        lasts = [col[-1] for col in self.board if len(col) > 0]
        lefts = [self.get_piece(col_index - 1, len(self.board[col_index])) for col_index in range(7)]
        rights = [self.get_piece(col_index + 1, len(self.board[col_index])) for col_index in range(7)]

        considered = lasts + lefts + rights

        return considered.count('A') - considered.count('B')

    def evaluate(self):
        score = 0
        for winner in ConnectFour.WINNERS:
            line = [self.get_piece(row_index, col_index) for row_index, col_index in winner]
            if 'A' not in line:
                score -= 1
            if 'B' not in line:
                score += 1

        return score

    # GAMEPLAY

    def add_new_mark_and_flip_turn(self, col_index):
        board = copy.deepcopy(self.board)
        if len(board[col_index]) < 6:
            board[col_index].append(self.get_player_to_play())
        else:
            assert False

        new_state = ConnectFour(board, a_turn = not self.a_turn)
        new_state.evaluate = self.evaluate
        return new_state

    def next_node(self):
        open_columns = self.open_columns()

        winner = self.winner()
        if winner is not None:
            return 'Terminal', winner
        elif self.a_turn:
            return 'A', { str(i) : i for i in open_columns }
        else:
            return 'B', { str(i) : i for i in open_columns }

    def resolve_choice(self, choice):
        return self.add_new_mark_and_flip_turn(choice)

    # REPRESENTATION

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
    state.place_possibly_hovering(6, 5)
    state.place_possibly_hovering(5, 4)
    state.place_possibly_hovering(4, 3)
    state.place_possibly_hovering(3, 2)

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
    state.place_possibly_hovering(3, 5)
    state.place_possibly_hovering(4, 4)
    state.place_possibly_hovering(5, 3)
    state.place_possibly_hovering(6, 2)

    assert state.winner() == 'A'

def test_num_winners():
    num_winners = 0
    winners = []
    winner_states = []
    for combo in four_combos(42):
        state = ConnectFour()
        for i in combo:
            row_index = i // 7
            col_index = i % 7
            state.place_possibly_hovering(col_index, row_index)

        winner = state.winner()
        if winner == 'A':
            num_winners += 1
            winners.append(combo)
            winner_states.append(state)

    # 7 columns, 3 different winning jawns on each col
    # 6 rows, 4 " on each row
    # Diagonals going up and to the right can start anywhere that isn't within 3
    # of the top or right side. So they can start in one of 3 * 4 places
    # By symmetry, same thing for the diagonals going up and to the left
    # 21 + 24 + 12 + 12 = 69
    #print(num_winners)
    #print(winners[:10])
    #assert num_winners == 69

    # for winner in winners:
    #     print(','.join([str(i) for i in winner]))

    # i = 0
    # for state in winner_states:
    #     i += 1
    #     print(i)
    #     print(state)

if __name__ == '__main__':
    assert len(four_combos(42)) == 111930
    test_num_winners()
    simple_col_winner_test()
    simple_row_winner_test()
    simple_up_right_winner_test()
    second_up_right_winner_test()
    simple_up_left_winner_test()
    second_up_left_winner_test()
    pass
