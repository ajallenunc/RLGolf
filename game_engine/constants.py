# Card Ranks
ACE = 'A'
TWO = '2'
THREE = '3'
FOUR = '4'
FIVE = '5'
SIX = '6'
SEVEN = '7'
EIGHT = '8'
NINE = '9'
TEN = 'T'
JACK = 'J'
QUEEN = 'Q'
KING = 'K'
JOKER = 'X' 

RANKS = [ACE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING]
ALL_RANKS = RANKS + [JOKER]

# Card Suits
HEARTS = 'H'
DIAMONDS = 'D'
CLUBS = 'C'
SPADES = 'S'
JOKER_SUIT = 'J' 

SUITS = [HEARTS, DIAMONDS, CLUBS, SPADES]
ALL_SUITS = SUITS + [JOKER_SUIT] 

# Grid Size
GRID_SIZE = 9
GRID_DIM = 3 # 3x3 grid

# Turn phases 
PHASE_INITIAL_FLIP = 0 # Initial 3 flips 
PHASE_START_TURN = 1 # Player chooses to either draw from stock pile or discard pile
PHASE_DRAW_STOCK_DECISION = 2 # Player drew from stock, either REPLACE card in Grid or DISCARD and FLIP card in grid
PHASE_DRAW_DISCARD_DECISION = 3 # Player drew from discard pile, must REPLACE card in Grid 
PHASE_MUST_FLIP_CARD = 4 # Player chose to discard drawn card, must now flip 
PHASE_GAME_OVER = 5 # Round over 
