from .constants import *
from .card import Card
import random 
from typing import List

class Deck: 
    """ Deck of cards used in the game """ 

    def __init__(self,num_decks: int = 2, num_jokers: int = 4): 
        self.cards: List[Card] = []
        self.num_decks = num_decks 
        self.num_jokers = num_jokers
        self._build()

    def _build(self):
        """ Build the deck """ 
        for _ in range(self.num_decks): 
            for suit in SUITS:
                for rank in RANKS:
                    self.cards.append(Card(rank,suit))

        for _ in range(self.num_jokers):
            self.cards.append(Card(JOKER,JOKER_SUIT))


    def shuffle(self): 
        """ Shuffle the deck """ 
        random.shuffle(self.cards)
        