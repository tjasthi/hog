"""The Game of Hog."""

from dice import four_sided, six_sided, make_test_dice
from ucb import main, trace, log_current_line, interact

GOAL_SCORE = 100  # The goal of Hog is to score 100 points.


######################
# Phase 1: Simulator #
######################


def roll_dice(num_rolls, dice=six_sided):
    """Simulate rolling the DICE exactly NUM_ROLLS times. Return the sum of
    the outcomes unless any of the outcomes is 1. In that case, return 0.
    """
    # These assert statements ensure that num_rolls is a positive integer.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls > 0, 'Must roll at least once.'
    answer = 0
    count = num_rolls
    one = False
    while count > 0:  
        dice_result = dice() 
        if dice_result == 1:
            one = True
        answer = answer + dice_result
        count = count - 1
    if one == True:
        return 0
    else:
        return answer


def is_prime(x):
    prime = True

    if x == 1:
        prime = False
    elif x == 0:
        prime = False
    for i in range(2,x):
        if x % i == 0:
            prime = False
    return prime

def next_prime(x):
    next_prime_number = 0
    if is_prime(x) == True:
        x = x + 1
        while not is_prime(x):
            x = x + 1
        return x
    else:
        print("This number is not prime")

def take_turn(num_rolls, opponent_score, dice=six_sided):
    """Simulate a turn rolling NUM_ROLLS dice, which may be 0 (Free Bacon).

    num_rolls:       The number of dice rolls that will be made.
    opponent_score:  The total score of the opponent.
    dice:            A function of no args that returns an integer outcome.
    """
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls >= 0, 'Cannot roll a negative number of dice.'
    assert num_rolls <= 10, 'Cannot roll more than 10 dice.'
    assert opponent_score < 100, 'The game should be over.'
    total = 0
    opp_score_ones = opponent_score % 10
    opp_score_tens = opponent_score // 10
    if num_rolls == 0:
        total = max(opp_score_ones, opp_score_tens) + 1
    else:
        total = roll_dice(num_rolls, dice)
    if is_prime(total) == True:
        return next_prime(total)
    else:
        return total



def select_dice(score, opponent_score):
    """Select six-sided dice unless the sum of SCORE and OPPONENT_SCORE is a
    multiple of 7, in which case select four-sided dice (Hog wild).
    """
    if (score + opponent_score) % 7 == 0:
        return four_sided
    else:
        return six_sided


def is_swap(score0, score1):
    """Returns whether the last two digits of SCORE0 and SCORE1 are reversed
    versions of each other, such as 19 and 91.
    """
    
    score0_tens = score0 // 10 
    score0_ones = score0 % 10
    score1_tens = score1 // 10
    score1_ones = score1 % 10
    if score0_tens >= 10:
        score0_tens = score0_tens - 10
    if score1_tens >= 10:
        score1_tens = score1_tens - 10
    if score0_tens == score1_ones and score0_ones == score1_tens:
        return True
    else:
        return False


def other(player):
    """Return the other player, for a player PLAYER numbered 0 or 1.

    >>> other(0)
    1
    >>> other(1)
    0
    """
    return 1 - player


def play(strategy0, strategy1, score0=0, score1=0, goal=GOAL_SCORE):
    """Simulate a game and return the final scores of both players, with
    Player 0's score first, and Player 1's score second.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    strategy0:  The strategy function for Player 0, who plays first
    strategy1:  The strategy function for Player 1, who plays second
    score0   :  The starting score for Player 0
    score1   :  The starting score for Player 1
    """
    player = 0  # Which player is about to take a turn, 0 (first) or 1 (second)
    
    while score0 < goal and score1 < goal:
        if player == 0:
            num_rolls = strategy0(score0, score1)
            turn_result = take_turn(num_rolls, score1, select_dice(score0, score1))
            if turn_result == 0:
                score1 = score1 + num_rolls
            score0 = score0 + turn_result
            if is_swap(score0, score1):
                score0, score1 = score1, score0
            player = other(player)
        elif player == 1:
            num_rolls = strategy1(score1, score0)
            turn_result = take_turn(num_rolls, score0, select_dice(score0, score1))
            if turn_result == 0:
                score0 = score0 + (num_rolls)
            score1 = score1 + turn_result
            if is_swap(score0, score1):
                score0, score1 = score1, score0
            player = other(player)
    return score0, score1
#select_dice and is_swap is repeated but we believe taking it out of both statements is harmful


#######################
# Phase 2: Strategies #
#######################


def always_roll(n):
    """Return a strategy that always rolls N dice.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    >>> strategy = always_roll(5)
    >>> strategy(0, 0)
    5
    >>> strategy(99, 99)
    5
    """
    def strategy(score, opponent_score):
        return n

    return strategy


# Experiments

def make_averaged(fn, num_samples=1000):
    """Return a function that returns the average_value of FN when called.

    To implement this function, you will have to use *args syntax, a new Python
    feature introduced in this project.  See the project description.

    >>> dice = make_test_dice(3, 1, 5, 6)
    >>> averaged_dice = make_averaged(dice, 1000)
    >>> averaged_dice()
    3.75
    >>> make_averaged(roll_dice, 1000)(2, dice)
    5.5

    In this last example, two different turn scenarios are averaged.
    - In the first, the player rolls a 3 then a 1, receiving a score of 0.
    - In the other, the player rolls a 5 and 6, scoring 11.
    Thus, the average value is 5.5.
    Note that the last example uses roll_dice so the hogtimus prime rule does
    not apply.
    """
    def average(*args):
        count = 0
        total = 0
        while count < num_samples:
            total = total + fn(*args)
            count = count + 1
        return total / num_samples
    return average



def max_scoring_num_rolls(dice=six_sided, num_samples=1000):
    """Return the number of dice (1 to 10) that gives the highest average turn
    score by calling roll_dice with the provided DICE over NUM_SAMPLES times.
    Assume that the dice always return positive outcomes.

    >>> dice = make_test_dice(3)
    >>> max_scoring_num_rolls(dice)
    10
    """
    maximum_score = -.1
    best_dice = 0
    for i in range(1,11):
        average_score = make_averaged(roll_dice, num_samples)
        average = average_score(i,dice)
        if average > maximum_score:
            maximum_score = average
            best_dice = i
    return best_dice


def winner(strategy0, strategy1):
    """Return 0 if strategy0 wins against strategy1, and 1 otherwise."""
    score0, score1 = play(strategy0, strategy1)
    if score0 > score1:
        return 0
    else:
        return 1


def average_win_rate(strategy, baseline=always_roll(5)):
    """Return the average win rate of STRATEGY against BASELINE. Averages the
    winrate when starting the game as player 0 and as player 1.
    """
    win_rate_as_player_0 = 1 - make_averaged(winner)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner)(baseline, strategy)

    return (win_rate_as_player_0 + win_rate_as_player_1) / 2


def run_experiments():
    """Run a series of strategy experiments and report results."""
    if True:  # Change to False when done finding max_scoring_num_rolls
        six_sided_max = max_scoring_num_rolls(six_sided)
        print('Max scoring num rolls for six-sided dice:', six_sided_max)
        four_sided_max = max_scoring_num_rolls(four_sided)
        print('Max scoring num rolls for four-sided dice:', four_sided_max)

    if False:  # Change to True to test always_roll(8)
        print('always_roll(8) win rate:', average_win_rate(always_roll(8)))

    if False:  # Change to True to test bacon_strategy
        print('bacon_strategy win rate:', average_win_rate(bacon_strategy))

    if False:  # Change to True to test swap_strategy
        print('swap_strategy win rate:', average_win_rate(swap_strategy))

    "*** You may add additional experiments as you wish ***"


# Strategies

def bacon_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice if that gives at least MARGIN points,
    and rolls NUM_ROLLS otherwise.
    """
    opp_score_tens = opponent_score // 10
    opp_score_ones = opponent_score % 10
    max_bacon = max(opp_score_tens, opp_score_ones)
    
    if is_prime(max_bacon + 1) == True:
        if next_prime(max_bacon + 1) >= margin:
            return 0
    elif (max_bacon + 1) >= margin:
        return 0
    else:
        return num_rolls


def swap_strategy(score, opponent_score, num_rolls=5):
    """This strategy rolls 0 dice when it results in a beneficial swap and
    rolls NUM_ROLLS otherwise.
    """
    opp_score_tens = opponent_score // 10
    opp_score_ones = opponent_score % 10
    max_bacon = max(opp_score_tens, opp_score_ones)
    
    if is_prime(max_bacon + 1) == True:
        added_number = next_prime(max_bacon + 1)
    else:
        added_number = max_bacon + 1
    final_score = score + added_number
    if is_swap(final_score, opponent_score) == True:
        if final_score < opponent_score:
            return 0
        else:
            return num_rolls
    else:
        return num_rolls

def final_strategy(score, opponent_score):
    """Write a brief description of your final strategy.

    *** 
    First we define two functions, one that tries to give the other player four-sided die (so they are more likely to roll a 1,
    and one that checks if pigging out (rolling 10 dice to get a 1) makes swine swap happen (only if the swap is benieficial).
    First and foremost, if the score is >= 99, we return only 1 die, because at this point there is no need to roll more dice because rolling more dice gives a bigger chance of pigging out.
    Then, we put swap strategy as the most important function, as a beneficial swap usually gives the highest return to the player, while also disadvantaging the opponent.
    We then check if pigging out to swap works, as another way to force a swap.
    Then we implement bacon_strategy with margin 6 and num_rolls 4 because that combination yields the highest return.
    Afterward, if the dice are four-sided, we roll only 1 die, to minimize the chances of pigging out, while still getting points.
    Finally, we check if it is possible to force the opponent to roll four-sided die, as this increases the chance of them pigging out.
    If all these cases fail, then we just roll 4 dice.

    ***
    """
    piggy_rolls = 0
    num_rolls = 4
    margin = 6

    def four_side_the_opponent(score, opponent_score):
        opp_score_tens = opponent_score // 10
        opp_score_ones = opponent_score % 10
        max_bacon = max(opp_score_tens, opp_score_ones)

        if is_prime(max_bacon + 1) == True:
            added_number = next_prime(max_bacon + 1)
        else:
            added_number = max_bacon + 1
        final_score = score + added_number
        if (final_score + opponent_score) % 7 == 0:
            return 0
        else:
            return num_rolls

    def pigging_out_to_swap_10(score, opponent_score):
        if is_swap(score, (opponent_score + 10)) == True and ((opponent_score + 10) > score) == True:
            return True
    def pigging_out_to_swap_9(score, opponent_score):
        if is_swap(score, (opponent_score + 9)) == True and ((opponent_score + 9) > score) == True:
            return True
    def pigging_out_to_swap_8(score, opponent_score):
        if is_swap(score, (opponent_score + 8)) == True and ((opponent_score + 8) > score) == True:
            return True
    def pigging_out_to_swap_7(score, opponent_score):
        if is_swap(score, (opponent_score + 7)) == True and ((opponent_score + 7) > score) == True:
            return True
    def pigging_out_to_swap_6(score, opponent_score):
        if is_swap(score, (opponent_score + 6)) == True and ((opponent_score + 6) > score) == True:
            return True
    def pigging_out_to_swap_5(score, opponent_score):
        if is_swap(score, (opponent_score + 5)) == True and ((opponent_score + 5) > score) == True:
            return True
    if score >= 99:
        return 1
    elif swap_strategy(score, opponent_score, num_rolls) == 0:
        return 0
    elif pigging_out_to_swap_10(score, opponent_score) == True:
        return 10
    elif pigging_out_to_swap_9(score, opponent_score) == True:
        return 9
    elif pigging_out_to_swap_8(score, opponent_score) == True:
        return 8
    elif pigging_out_to_swap_7(score, opponent_score) == True:
        return 7
    elif pigging_out_to_swap_6(score, opponent_score) == True:
        return 6
    elif pigging_out_to_swap_5(score, opponent_score) == True:
        return 5
    elif bacon_strategy(score,opponent_score, margin, num_rolls) == 0:
        return 0
    elif (score + opponent_score) % 7 == 0:
        return 1
    elif four_side_the_opponent(score,opponent_score) == 0:
        return 0
    else:
        return num_rolls


##########################
# Command Line Interface #
##########################


# Note: Functions in this section do not need to be changed. They use features
#       of Python not yet covered in the course.


@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions.

    This function uses Python syntax/techniques not yet covered in this course.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Play Hog")
    parser.add_argument('--run_experiments', '-r', action='store_true',
                        help='Runs strategy experiments')

    args = parser.parse_args()

    if args.run_experiments:
        run_experiments()
