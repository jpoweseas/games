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

def evaluate_player_node(current_state, choices, invert, alpha, beta, parent_hash=None, debug_mode=False, depth_limit=0, trans=None):
    if trans is None:
        trans = {}

    init_alpha = alpha
    init_beta = beta

    state_choices = [current_state.resolve_choice(choice) for choice in choices]
    state_choices.sort(key=lambda state : state.evaluate())

    if not invert:
        state_choices = state_choices[::-1]

    best_move = None

    # lb, ub represent our bounds on the ACTUAL utility of the move
    current_hash = current_state.hash()
    if current_hash in trans:
        (lb, ub) = trans[current_state.hash()]
        # if lb == ub and lb is not None:
        #     print(f'gotcha {current_hash}-{parent_hash}')
        alpha = max_opt(alpha, lb)
        beta = min_opt(beta, ub)
        best_score_so_far = ub if invert else lb
    else:
        lb, ub = None, None
        best_score_so_far = None

    if debug_mode:
        children_in_eval_order = []

    for state in state_choices:
        if alpha is not None and beta is not None and alpha >= beta:
            if invert:
                ub = best_score_so_far
            else:
                lb = best_score_so_far

            trans[current_state.hash()] = (lb, ub)
            break

        if debug_mode:
            children_in_eval_order.append(str(state.hash()))

        score = negamax(state, alpha, beta, parent_hash=current_hash, debug_mode=debug_mode, depth_limit=(depth_limit - 1), trans=trans)

        if score is None:
            continue

        if invert:
            beta = min_opt(score, beta)
            if best_score_so_far is None or score < best_score_so_far:
                best_score_so_far = score
                best_move = state
        else:
            alpha = max_opt(alpha, score)
            if best_score_so_far is None or score > best_score_so_far:
                best_score_so_far = score
                best_move = state
    else:
        # when we don't cutoff
        trans[current_state.hash()] = (best_score_so_far, best_score_so_far)
        pass

    if debug_mode:
        is_cutoff = len(children_in_eval_order) < len(state_choices)
        debug_mode.writerow([
            current_state.hash(),
            parent_hash,
            current_state.to_reversible_format(),
            best_score_so_far,
            init_alpha,
            init_beta,
            '|'.join(children_in_eval_order),
            is_cutoff
            ])

    if best_score_so_far is None:
        # This is the case where every possible play results in a cutoff
        # Not true now that we're not returning Nones?
        print('should be impossible?', current_state.hash())
        return None
    else:
        return { 'score' : best_score_so_far, 'best_move' : best_move }

# Returns A's score of the subgame, or None if this part of the game tree will not be used
# alpha : best choice available to player A
# beta  : best choice available to player B
# alpha < beta normally, when it flips that game tree is doneso
# return type looks like { score }
def negamax(state, alpha, beta, parent_hash=None, debug_mode=False, depth_limit=0, trans=None):
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
                parent_hash,
                state.to_reversible_format(),
                score,
                alpha,
                beta,
                [],
                False
                ])

        return score

    elif node_type == 'A' or node_type == 'B':
        result = evaluate_player_node(state, node.values(), (node_type == 'B'), alpha, beta, parent_hash=parent_hash, debug_mode=debug_mode, depth_limit=depth_limit, trans=trans)

        if result is None:
            return None
        else:
            return result['score']

    if node_type == 'Random':
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
