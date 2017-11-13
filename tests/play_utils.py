import random

TRACE_SOL = 'tests/play.sol'
TEST_SEED = 1337
NUM_TESTS = 1000

def make_random_strat():
    """Makes a random pure strategy."""
    seed = random.randrange(0, 2 ** 31)

    def random_strat(score, opponent_score):
        # Save the state of the random generator, so strategy calls don't
        # impact dice rolls.
        state = random.getstate()
        random.seed(hash((score, opponent_score, seed)))
        roll = random.randrange(0, 11)
        random.setstate(state)
        return roll
    return random_strat


# TODO: Not being used at the moment. Remove?
def make_random_strat_old():
    """Makes a "random" pure strategy.

    Note: this is slightly suboptimal in the aspect that the returned
    strategies will always roll 0 on the first turn. In the future, it might be
    better to replace this function with the previous one.
    """
    seed = random.randint(1, 65535)

    def random_strat(score, opponent_score):
        return pow(score * opponent_score, seed, 11)
    return random_strat


class GameState(object):
    def __init__(self, score, opponent_score, who, num_rolls):
        if who == 0:
            self.score0, self.score1 = score, opponent_score
        else:
            self.score0, self.score1 = opponent_score, score
        self.who = who
        self.num_rolls = num_rolls
        self.rolls = []
        self.dice_sides = 6

    def is_over(self):
        """Returns True iff this GameState should be over."""
        return len(self.rolls) >= self.num_rolls

    def successor(self, other):
        """Returns True if another GameState is a plausible successor of this
        GameState. Used for preventing multiple calls to a strategy function
        from messing up the tracer (to a reasonable degree).
        """
        return self.who != other.who and self.is_over() and \
                (self.score0 != other.score0 or self.score1 != other.score1)

    def is_correct(self, sol):
        return hash(self) == sol

    @property
    def turn_summary(self):
        if self.num_rolls == 0:
            return 'Player {0} rolls 0 dice:'.format(self.who)
        elif self.num_rolls == 1:
            return 'Player {0} rolls {1} {2}-sided die:'.format(
                    self.who,
                    self.num_rolls,
                    'six' if self.dice_sides == 6 else 'four')
        else:
            return 'Player {0} rolls {1} {2}-sided dice:'.format(
                    self.who,
                    self.num_rolls,
                    'six' if self.dice_sides == 6 else 'four')

    @property
    def turn_rolls(self):
        return str(self.rolls)[1:-1]

    def __hash__(self):
        return hash((self.score0, self.score1, self.who, self.num_rolls, self.dice_sides))


def make_traced(s0, s1, six_sided, four_sided):
    """Given the strategy functions of player 0 and player 1, and a list of
    dice functions that the """
    trace = []  # List of GameStates

    def make_traced_strategy(strat, player):
        def traced_strategy(score, opponent_score):
            num_rolls = strat(score, opponent_score)
            state = GameState(score, opponent_score, player, num_rolls)

            if not trace:
                trace.append(state)
            elif trace[-1].successor(state):
                trace.append(state)
            return num_rolls
        return traced_strategy

    def make_traced_dice(dice, dice_sides):
        def traced_dice():
            roll = dice()
            if trace:
                trace[-1].dice_sides = dice_sides
                trace[-1].rolls.append(roll)
            return roll
        return traced_dice

    def get_trace():
        return trace

    return make_traced_strategy(s0, 0), \
        make_traced_strategy(s1, 1), \
        make_traced_dice(six_sided, 6), \
        make_traced_dice(four_sided, 4), \
        get_trace


def play_traced(hog, strat0, strat1):
    four_sided, six_sided = hog.four_sided, hog.six_sided
    strat0, strat1, traced_six_sided, traced_four_sided, get_trace = \
        make_traced(strat0, strat1, six_sided, four_sided)

    hog.four_sided = traced_four_sided
    hog.six_sided = traced_six_sided
    score0, score1 = hog.play(strat0, strat1)
    trace = get_trace()
    trace.append(GameState(score0, score1, 0, 0))

    hog.four_sided = four_sided
    hog.six_sided = six_sided
    return trace


def check_play_function(hog):
    """Checks the `play` function of a student's HOG module by running multiple
    seeded games, and comparing the results.
    """
    random.seed(TEST_SEED)
    sol_traces = load_traces_from_file(TRACE_SOL)
    for i in range(NUM_TESTS):
        strat0, strat1 = make_random_strat(), make_random_strat()
        trace = play_traced(hog, strat0, strat1)
        incorrect = compare_trace(trace, sol_traces[i])
        if incorrect != -1:
            print('Incorrect result after playing {0} game(s):'.format(i + 1))
            print_trace(trace)
            print('Implementation diverged from solution at turn',
                '{0} (error_id: {1})'.format(incorrect,
                    hash((trace[incorrect], incorrect, i))))
            break


def make_solution_traces(hog):
    random.seed(TEST_SEED)
    sol_traces = []
    for i in range(NUM_TESTS):
        strat0, strat1 = make_random_strat(), make_random_strat()
        trace = play_traced(hog, strat0, strat1, hog.six_sided, hog.four_sided)
        sol_traces.append([hash(state) for state in trace])
    return sol_traces


def compare_trace(trace, sol):
    """Compares TRACE with the SOLUTION trace, and returns the turn number
    where the two traces differ, or -1 if the traces are the same.
    """
    i = 0
    while i < min(len(trace), len(sol)):
        state, sol_state = trace[i], sol[i]
        if not state.is_correct(sol_state):
            return i
        i += 1
    if len(trace) != len(sol):
        return len(trace)
    return -1


def print_trace(trace):
    prev_state = trace[0]
    i = 0
    print('{0:<10}{1:5}{2:5}    {3}'.format(
        'Turn {0}:'.format(i),
        prev_state.score0,
        prev_state.score1,
        ''))
    print('-'*58)
    for _ in range(len(trace) - 1):
        i += 1
        next_state = trace[i]
        s0_change = next_state.score0 - prev_state.score0
        s1_change = next_state.score1 - prev_state.score1
        print('{0:>15}{1:>5}    {2}'.format(
            '' if s0_change == 0 else '{0:+}'.format(s0_change),
            '' if s1_change == 0 else '{0:+}'.format(s1_change),
            prev_state.turn_summary))
        print('{0:<10}{1:5}{2:5}        {3}'.format(
            'Turn {0}:'.format(i),
            prev_state.score0,
            prev_state.score1,
            prev_state.turn_rolls))
        print('-'*58)
        prev_state = next_state
    print('{0:<10}{1:5}{2:5}'.format(
        'Result:',
        prev_state.score0,
        prev_state.score1))


def load_traces_from_file(path):
    with open(path) as f:
        return eval(f.read())

def write_traces_to_file(path, traces):
    with open(path, 'w') as f:
        f.write(str(traces))
