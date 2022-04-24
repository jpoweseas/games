import csv

WIN_VALUE = 10000
LOSE_VALUE = -10000
TIE_VALUE = 0

def resolve_random(state_with_probability_list, debug_mode=False, depth_limit=0, use_pruning=True):
    return sum([prob * negamax(state, depth_limit=(depth_limit - 1)) for state in state_with_probability_list], use_pruning=use_pruning)

def evaluate_player_node(current_state, state_choices, invert, debug_mode=False, depth_limit=0):
    invert_mult = -1 if invert else 1

    if debug_mode:
        children_in_eval_order = []

    max_value_so_far = invert_mult * negamax(state_choices[0], debug_mode, depth_limit=(depth_limit - 1), use_pruning=True)
    best_state = state_choices[0]

    if debug_mode:
        children_in_eval_order = []

    for state in state_choices[1:]:
        if debug_mode:
            children_in_eval_order.append(str(state.hash()))

        value = invert_mult * negamax(state, debug_mode=debug_mode, depth_limit=(depth_limit - 1), use_pruning=True)
        if value > max_value_so_far:
            max_value_so_far = value
            best_state = state

    if debug_mode:
        debug_mode.writerow([
            current_state.hash(),
            current_state.to_reversible_format(),
            invert_mult * max_value_so_far,
            None, #alpha
            None, #beta
            '|'.join(children_in_eval_order),
            None #is_cutoff
            ])

    return { 'value' : invert_mult * max_value_so_far, 'state' : best_state }

# Returns A's value of the subgame
def negamax(state, debug_mode=False, depth_limit=0, use_pruning=True):
    if depth_limit < 0:
        assert False
    elif depth_limit == 0:
        return state.evaluate()

    node_type, node = state.next_node()

    if node_type == "Random":
        return resolve_random(state, debug_mode, depth_limit=depth_limit, use_pruning=use_pruning)

    elif node_type == "Terminal":
        if node == 'A':
            ret = WIN_VALUE
        elif node == 'B':
            ret = LOSE_VALUE
        elif node == 'tie':
            ret = TIE_VALUE
        else:
            assert False

        if debug_mode:
            debug_mode.writerow([
                state.hash(),
                state.to_reversible_format(),
                ret,
                # alpha,
                # beta,
                # '|'.join(children_in_eval_order),
                # is_cutoff
                None, None, None, None
                ])

        return ret

    elif node_type == 'A' or node_type == 'B':

        state_choices = [state.resolve_choice(choice) for choice in node.values()]
        result = evaluate_player_node(state, state_choices, invert=(node_type == 'B'), debug_mode=debug_mode, depth_limit=depth_limit)

        return result['value']

    else:
        assert False

class SimpleAIPlayer:
    def __init__(self, playing_as, evaluate=None):
        self.playing_as = playing_as
        self.evaluate = evaluate

    def choose_move(self, choices, current_state, debug_mode=False, depth_limit=6):
        if debug_mode:
            csvfile = open('out.csv', 'w', newline='')
            csv_writer = csv.writer(csvfile)
        else:
            csv_writer = None

        state_choices = [current_state.resolve_choice(choice) for choice in choices.values()]
        if self.evaluate:
            for state in state_choices:
                state.evaluate = self.evaluate

        choice = evaluate_player_node(current_state, state_choices, invert=(self.playing_as == 'B'), debug_mode=csv_writer, depth_limit=depth_limit)['state']
        return choice
