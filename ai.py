import csv

WIN_VALUE = 10000
LOSE_VALUE = -10000
TIE_VALUE = 0

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

def evaluate_player_node(current_state, choices, invert, alpha, beta, debug_mode=False, depth_limit=0, trans={}):
    # This is the max score when invert = False, min score when invert = True
    state_choices = [current_state.resolve_choice(choice) for choice in choices]
    state_choices.sort(key=lambda state : state.evaluate())

    if not invert:
        state_choices = state_choices[::-1]

    best_score_so_far = None
    best_pv = None

    current_hash = current_state.hash()
    if current_hash in trans:
        (lb, ub) = trans[current_state.hash()]
        if lb == ub and lb is not None:
            return { 'score' : lb, 'pv' : [] }
        alpha = max_opt(alpha, lb)
        beta = min_opt(beta, ub)

    if debug_mode:
        children_in_eval_order = []

    for state in state_choices:
        if debug_mode:
            children_in_eval_order.append(state.to_reversible_format())

        result = negamax(state, alpha, beta, debug_mode=debug_mode, depth_limit=(depth_limit - 1), trans=trans)

        if result is None:
            continue

        score = result['score']
        pv = result['pv']
        if invert:
            beta = min_opt(score, beta)
            if best_score_so_far is None or score < best_score_so_far:
                best_score_so_far = score
                best_pv = pv
        else:
            alpha = max_opt(alpha, score)
            if best_score_so_far is None or score > best_score_so_far:
                best_score_so_far = score
                best_pv = pv

        if alpha is not None and beta is not None and alpha >= beta:
            # Don't update bounds .. for now
            break
    else:
        # when we don't cutoff
        trans[current_state.hash()] = (best_score_so_far, best_score_so_far)

    if debug_mode:
        is_cutoff = len(children_in_eval_order) < len(state_choices)
        debug_mode.writerow([
            current_state.hash(),
            current_state.to_reversible_format(),
            best_score_so_far,
            alpha,
            beta,
            '|'.join(children_in_eval_order),
            is_cutoff
            ])

    if best_score_so_far is None:
        # This is the case where every possible play results in a cutoff
        # Not true now that we're not returning Nones?
        print('should be impossible?')
        return None
    else:
        return { 'score' : best_score_so_far, 'pv' : best_pv }

# Returns A's score of the subgame, or None if this part of the game tree will not be used
# alpha : best choice available to player A
# beta  : best choice available to player B
# alpha < beta normally, when it flips that game tree is doneso
# return type looks like { score }
def negamax(state, alpha, beta, debug_mode=False, depth_limit=0, trans={}):
    if depth_limit < 0:
        assert False
    elif depth_limit == 0:
        return { 'score' : state.evaluate(), 'pv' : [state] }

    node_type, node = state.next_node()

    if node_type == 'Random':
        assert False

    elif node_type == "Terminal":
        if node == 'A':
            ret = { 'score' : WIN_VALUE, 'pv' : [state] }
        elif node == 'B':
            ret = { 'score' : LOSE_VALUE, 'pv' : [state] }
        elif node == 'tie':
            ret = { 'score' : TIE_VALUE, 'pv' : [state] }
        else:
            assert False

        if debug_mode:
            debug_mode.writerow([
                state.hash(),
                state.to_reversible_format(),
                ret['score'],
                # alpha,
                # beta,
                # '|'.join(children_in_eval_order),
                # is_cutoff
                None, None, None, None
                ])

        return ret

    elif node_type == 'A' or node_type == 'B':

        result = evaluate_player_node(state, node.values(), (node_type == 'B'), alpha, beta, debug_mode=debug_mode, depth_limit=depth_limit, trans=trans)

        if result is None:
            return None
        else:
            result['pv'].append(state)
            return result

    else:
        assert False

class AIPlayer:
    def __init__(self, playing_as):
        self.playing_as = playing_as

    def choose_move(self, choices, current_state, debug_mode=False, depth_limit=6):
        if debug_mode:
            csvfile = open('out.csv', 'w', newline='')
            csv_writer = csv.writer(csvfile)
        else:
            csv_writer = None

        result = evaluate_player_node(current_state, choices.values(), (self.playing_as == 'B'), None, None, debug_mode=csv_writer, depth_limit=depth_limit)
        pv = result['pv']
        for state in pv[::-1]:
            print(state)
        return pv[-1]
