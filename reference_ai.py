WIN_VALUE = 10000
LOSE_VALUE = -10000
TIE_VALUE = 0

def resolve_random(state_with_probability_list, debug_mode=False, depth_limit=0, use_pruning=True):
    if debug_mode:
        print('unimplemented')
        assert False
    return sum([prob * negamax(state, depth_limit=(depth_limit - 1)) for state in state_with_probability_list], use_pruning=use_pruning)

def evaluate_player_node(state_choices, invert, debug_mode=False, depth_limit=0):
    invert_mult = -1 if invert else 1
    max_value_so_far = invert_mult * negamax(state_choices[0], debug_mode, depth_limit=(depth_limit - 1), use_pruning=True)
    best_state = state_choices[0]

    for state in state_choices[1:]:
        value = invert_mult * negamax(state, debug_mode=debug_mode, depth_limit=(depth_limit - 1), use_pruning=True)
        if value > max_value_so_far:
            max_value_so_far = value
            best_state = state

    return { 'value' : invert_mult * max_value_so_far, 'state' : best_state }

# Returns A's value of the subgame
def negamax(state, debug_mode=False, depth_limit=0, use_pruning=True):
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

        return resolve_random(state, debug_mode, depth_limit=depth_limit, use_pruning=use_pruning)

    elif node_type == "Terminal":
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

class SimpleAIPlayer:
    def __init__(self, playing_as, evaluate=None):
        self.playing_as = playing_as
        self.evaluate = evaluate

    def choose_move(self, choices, current_state, debug_mode=False, depth_limit=6):
        if debug_mode:
            print('AI moving:')
            print(current_state)
            print('')

        state_choices = [current_state.resolve_choice(choice) for choice in choices.values()]
        if self.evaluate:
            for state in state_choices:
                state.evaluate = self.evaluate

        choice = evaluate_player_node(state_choices, invert=(self.playing_as == 'B'), debug_mode=debug_mode, depth_limit=depth_limit)['state']
        return choice
