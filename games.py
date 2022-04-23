import copy
from tictactoe import TicTacToe
from connect_four import ConnectFour
from tree_game import TreeGame
from reference_ai import SimpleAIPlayer
from ai import AIPlayer

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

def play_game(state, a_player, b_player):
    while True:
        node_type, node = state.next_node()

        if node_type == "Random":
            print('unimplemented')
            assert False
        elif node_type ==  "Terminal":
            print(f'Winner is {node}!')
            print(state)
            return
        elif node_type == 'A':
            state = a_player.choose_move(node, state, debug_mode = False)
        elif node_type == 'B':
            state = b_player.choose_move(node, state, debug_mode = False)
        else:
            assert False

# play_game(TicTacToe(), AIPlayer('A'), AIPlayer('B'))
#play_game(ConnectFour(), AIPlayer('A'), AIPlayer('B'))

if __name__ == '__main__':
    play_game(TreeGame(seed=1), AIPlayer('A'), AIPlayer('B'))
