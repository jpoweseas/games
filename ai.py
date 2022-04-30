import csv

# current_state_hash=id,<state sexp>,score,alpha_after?,beta_after?,children_in_eval_order

def max_opt(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return max(a, b)

def min_opt(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return min(a, b)

def resolve_random(state_with_probability_list, debug_mode=False, depth_limit=0):
    return sum([prob * negamax(state, depth_limit=(depth_limit - 1)) for state in state_with_probability_list])

def evaluate_player_node(current_state, choices, invert, alpha, beta, history=None, debug_mode=False, depth_limit=0, trans=None):
    if trans is None:
        trans = {}

    if history is None:
        history = []

    if debug_mode:
        init_alpha = alpha
        init_beta = beta

    state_choices = [current_state.resolve_choice(choice) for choice in choices]
    state_choices.sort(key=lambda state : state.evaluate())

    if not invert:
        state_choices = state_choices[::-1]

    best_move = None

    # lb, ub represent our bounds on the ACTUAL utility of the move
    # (lb, ub) = trans[current_state.hash()]
    current_hash = current_state.hash()
    lb = None
    ub = None
    for sym_hash in current_state.symmetric_hashes():
        if sym_hash in trans:
            (sym_lb, sym_ub) = trans[sym_hash]
            lb = max_opt(lb, sym_lb)
            ub = max_opt(ub, sym_ub)
    is_lookup = lb == ub and lb is not None
    alpha = max_opt(alpha, lb)
    beta = min_opt(beta, ub)

    if debug_mode:
        init_lb, init_ub = lb, ub
        children_in_eval_order = []

    best_possible_score = None
    best_possible_score_is_bounded = True

    for state in state_choices:
        if alpha is not None and beta is not None and alpha >= beta:
            break

        if debug_mode:
            children_in_eval_order.append(str(state.hash()))

        result = negamax(state, alpha, beta, history=(history[:] + [str(current_hash)]), debug_mode=debug_mode, depth_limit=(depth_limit - 1), trans=trans)
        child_lb = result['lb']
        child_ub = result['ub']

        # A updates the lower bound every time he finds a better move
        # A must assume everything is as bad as possible, i.e. lower bounds
        if invert:
            # TODO: move this inside if statement?
            beta = min_opt(child_ub, beta)
            # best_possible_score = min_opt(best_possible_score, child_lb)
            best_possible_score = None if not best_possible_score_is_bounded or child_lb is None else min_opt(best_possible_score, child_lb)
            if ub is None or (child_ub is not None and child_ub < ub):
                ub = child_ub
                best_move = state
        else:
            alpha = max_opt(alpha, child_lb)
            best_possible_score = None if not best_possible_score_is_bounded or child_ub is None else max_opt(best_possible_score, child_ub)
            if lb is None or (child_lb is not None and child_lb > lb):
                lb = child_lb
                best_move = state
    else:
        # when we don't cutoff
        if invert:
            lb = max_opt(best_possible_score, lb)
        else:
            ub = min_opt(best_possible_score, ub)
        pass

    # Don't put reflections back in the table
    if not is_lookup:
        trans[current_hash] = (lb, ub)

    if debug_mode:
        is_cutoff = len(children_in_eval_order) < len(state_choices)
        debug_mode.writerow([
            current_state.hash(),
            '|'.join(history),
            current_state.to_reversible_format(),
            f'{lb}/{ub}',
            init_alpha,
            init_beta,
            '|'.join(children_in_eval_order),
            is_cutoff,
            init_lb,
            init_ub
        ])

    return { 'lb' : lb, 'ub' : ub, 'best_move' : best_move }

# Returns A's score of the subgame, or None if this part of the game tree will not be used
# alpha : best choice available to player A
# beta  : best choice available to player B
# alpha < beta normally, when it flips that game tree is doneso
# return type looks like { score }
def negamax(state, alpha, beta, history=None, debug_mode=False, depth_limit=0, trans=None):
    if trans is None:
        trans = {}

    node_type, node = state.next_node()

    if depth_limit < 0:
        assert False

    elif node_type == "Terminal" or depth_limit == 0:
        score = state.evaluate()
        if debug_mode:
            debug_mode.writerow([
                state.hash(),
                '|'.join(history),
                state.to_reversible_format(),
                score,
                alpha,
                beta,
                [],
                False
                ])

        return { 'lb' : score, 'ub' : score }

    elif node_type == 'A' or node_type == 'B':
        result = evaluate_player_node(state, node.values(), (node_type == 'B'), alpha, beta, history=history, debug_mode=debug_mode, depth_limit=depth_limit, trans=trans)

        if result is None:
            print('impossible!')
            assert False
        else:
            return result

    elif node_type == 'Random':
        assert False

    else:
        assert False

# TODO: This class doesn't make sense
class AIPlayer:
    def __init__(self, playing_as):
        self.playing_as = playing_as

    def choose_move(self, choices, current_state, debug_mode=False, depth_limit=6):
        # node_type, choices = state.next_node()

        # if node_type not in ['A', 'B']:
        #     assert False

        if debug_mode:
            csvfile = open('out.csv', 'w', newline='')
            csv_writer = csv.writer(csvfile)
        else:
            csv_writer = None

        result = evaluate_player_node(current_state, choices.values(), (self.playing_as == 'B'), None, None, debug_mode=csv_writer, depth_limit=depth_limit)
        return result['best_move']
