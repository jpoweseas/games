from ai import AIPlayer
from reference_ai import SimpleAIPlayer
from connect_four import ConnectFour
from tictactoe import TicTacToe

import time

def bench(ai, depth_limit, ai_str):
    state = TicTacToe()
    node_type, node = state.next_node()

    assert (node_type == 'A')

    start = time.time()
    ai.choose_move(node, state, debug_mode=True, depth_limit=depth_limit)
    stop = time.time()

    delta = stop - start
    print(f'{ai_str}: {delta:.2f}s to search depth_limit = {depth_limit}')

if __name__ == '__main__':
    depth_limit = 10

    bench(AIPlayer(playing_as='A'), depth_limit, 'better')
    # bench(SimpleAIPlayer(playing_as='A'), depth_limit, 'reference')
