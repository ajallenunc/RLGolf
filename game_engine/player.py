from .card import Card
from .constants import *

class Player: 
    """Players 3x3 grid of cards and their visibility"""
    
    def __init__(self): 
        # 3x3 Grid as flat list
        # Top Row:    0 1 2
        # Middle Row: 3 4 5
        # Bottom Row: 6 7 8
        self.grid: List[Optional[Card]] = [None] * GRID_SIZE 
        self.face_up: List[bool] = [False] * GRID_SIZE
    
    def set_card(self, index: int, card: Card, face_up: bool): 
        """Places a card on grid"""
        self.grid[index] = card
        self.face_up[index] = face_up 
    
    def get_card(self, index):
        """Retrieve card from grid"""
        return self.grid[index] 
    
    def is_face_up(self, index):
        return self.face_up[index]
    
    def flip_card_up(self, index): 
        """Turns a card face-up"""
        self.face_up[index] = True
    
    def get_face_up_cards(self):
        """ Returns list of all face-up cards"""
        return [(i, card) for i, (card, up) in enumerate(zip(self.grid, self.face_up)) if up and card is not None]
   
    def get_face_down_cards(self):
        """ Returns list of all face-down cards"""
        return [i for i, (card, up) in enumerate(zip(self.grid, self.face_up)) if not up and card is not None]

    def all_cards_face_up(self) -> bool: 
        """ Check if all cards for player are face up """
        for i in range(GRID_SIZE): 
            if not self.face_up[i]: 
                return False 
        return True 
    
    def calculate_score(self): 
        """Calculates score for grid"""
        total_score = 0 
        matched_idx = set()

        # Check columns (0,3,6), (1,4,7), (2,5,8)
        for col_start in range(GRID_DIM): 
            # Get cards at each column set
            idx = [col_start, col_start + GRID_DIM, col_start + 2 * GRID_DIM]
            cards = [self.grid[i] for i in idx]
            # Check match
            if cards[0].rank == cards[1].rank == cards[2].rank: 
                matched_idx.update(idx)


        # Check rows (0,1,2), (3,4,5), (6,7,8)
        for row_start in range(GRID_DIM):
            # Get  cards at each row sset
            idx = [row_start, row_start + 1, row_start + 2]
            cards = [self.grid[i] for i in idx]

            # Check match
            if cards[0].rank == cards[1].rank == cards[2].rank: 
                matched_idx.update(idx)


        # Sum rank values of non-matched cards 
        for i in range(GRID_SIZE): 
            if i not in matched_idx: 
                card = self.grid[i]
                total_score = total_score + card.get_value()

        return total_score 
   
    def __str__(self):
        """Text representation of the grid."""
        lines = []
        for r in range(GRID_DIM):
            line = []
            for c in range(GRID_DIM):
                idx = r * GRID_DIM + c
                card = self.grid[idx]
                if card is None:
                    line.append("[ ]")
                elif self.face_up[idx]:
                    line.append(f"{str(card):>3}") 
                else:
                    line.append("[?]") # Face down
            lines.append(" ".join(line))
        return "\n".join(lines)
