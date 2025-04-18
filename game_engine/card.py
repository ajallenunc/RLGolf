from .constants import *
class Card: 
    """ Represents a single playing card """ 
    def __init__(self, rank: str, suit: str): 
        self.rank = rank
        self.suit = suit
        self.is_visible = False

    def get_value(self): 
        """ Calculates point value of card """ 
        if self.rank == JOKER: 
            return -2
        if self.rank == KING: 
            return 0
        if self.rank == ACE: 
            return 1 
        if self.rank in [TEN, JACK, QUEEN]: 
            return 10
        if self.rank in [NINE,EIGHT,SEVEN,SIX,FIVE,FOUR,THREE,TWO]: 
            return int(self.rank)

    def __str__(self) -> str:
        if self.rank == JOKER:
            return "Joker"
        rank_display = self.rank
        return f"{rank_display}{self.suit}"

