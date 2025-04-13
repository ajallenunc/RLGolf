import random
from typing import List, Tuple, Dict, Any, Optional
from .card import Card
from .deck import Deck
from .player import Player
from .constants import *

class GolfEnvironment: 
    """Handle Golf Environment"""
    
    def __init__(self, num_players: int = 2, num_decks: int = 2, num_jokers: int = 4):
        
        # Handle args 
        self.num_players = num_players 
        self.num_decks = num_decks
        self.num_jokers = num_jokers
        
        # --- Game setup --- #
        # Deck
        self.deck = Deck(self.num_decks, self.num_jokers)
        self.discard_pile: List[Card] = []
        self.drawn_card: Optional[Card] = None
        
        # Players
        self.players: List[Player] = [Player() for _ in range(self.num_players)]
        self.current_player: int = 0
        self.turn_count: int = 0
        self.final_turn_player_idx: Optional[int] = None
        
        # Round keeping 
        self.initial_flips_count: List[int] = [0,0]
        self.round_over: int = 0 
        self.game_over: bool = False 
        self.scores: List[int] = [0] * self.num_players 
        self.current_phase: int = 0
        
        # Action map 
        self._action_map: Dict[int, Tuple[str, Optional[int]]] = self._create_action_map()
        self.action_space_size = len(self._action_map)
    
    def _deal_initial_hands(self): 
        """Deal 9 cards to each player""" 
        # Shuffle deck 
        self.deck.shuffle()
        for i in range(GRID_SIZE): 
            for p_idx in range(self.num_players): 
                card = self.deck.deal()
                self.players[p_idx].set_card(i,card,face_up = True)
                
    def _start_discard_pile(self): 
        """Start the discard pile"""
        top_card = self.deck.deal()
        self.discard_pile.append(top_card) 
    
    def _reshuffle_discard_pile(self): 
        """ Reshuffle the discard pile if stockpile runs out (unlikely I think)"""
        if len(self.discard_pile) > 1: 
            # Keep the top card in discard pile 
            top_card = self.discard_pile.pop() 
            cards_to_reshuffle = self.discard_pile
            self.discard_pile = [top_card] 
            
            # Add cards to stock pile and reshuffle 
            self.deck.add_cards(cards_to_reshuffle)
            self.deck.shuffle() 
            print("--- Reshuffled discard pile into deck ---")
            
    def _reveal_all_cards(self, player_id): 
        """Turns all face-down cards up at the end of the round"""
        player = self.players[player_id]
        # Flip all remaining face-down cards up
        for i in range(GRID_SIZE): 
            card = player.get_card(i)
            if not player.is_face_up(i): 
                player.flip_card_up(i)
                
    
    def _check_round_end_and_advance_player(self): 
        """Check if player ended round, managed final turn logic, advances to next player if round not over"""
        current_player_id = self.current_player
        opponent_id = 1 - current_player
    
        player_all_face_up  = self.players[current_player_id].all_cards_face_up()
        
        if player_all_face_up:
            if self.final_turn_player_idx is None: 
                # Player triggered final turn for opponent 
                print(f"--- Player {current_player_id} has all cards face up! Player {opponent_id} gets final turn. ---")
                self.final_turn_player_idx =  opponent_id 
                self.current_player = opponent_id
                self.turn_count = self.turn_count + 1 
                self.current_phase = PHASE_START_TURN
            else: 
                # Current player was opponent taking final turn 
                print(f"--- Player {current_player_id}'s (Opponent) final turn complete. Round over. ---")
                self.round_over = True
                
                # Reveal all remaining cards 
                self._read_all_cards(current_player_id)
                self._read_all_cards(opponent_id)

        elif self.final_turn_player_idx == current_player_id: 
            # Current player is playing their final turn 
            print(f"--- Player {acting_player_id}'s final turn complete. Round over. ---")
            self.round_over = True
            self._read_all_cards(current_player_id)
            self._read_all_cards(opponent_id)
            
        else: 
            # Normal turn switch 
            self.current_player = opponent_id
            self.turn_count = self.turn_count + 1
            self.current_phase = PHASE_START_TURN

    
    def _create_action_map(self) -> Dict[int, Tuple[str, Optional[int]]]: 
        """Create mapping from action ID (int) to action (type, index)"""
        # Action Mapping 
        # ---------------------------
        # 0-8: Flip initial cards
        # 9: Draw from stock pile
        # 10: Draw from discard pile
        # 11-19: Replace card in grid
        # 20: Discard drawn card
        # 21-29: Flip card in grid 
        
        # Setup 
        mapping: Dict[int, Tuple[str, Optional[int]]] = {}
        action_id = 0
        
        # --- Action Mapping --- #
        
        for i in range(GRID_SIZE): 
            mapping[action_id] = ("Initial_Flip",i)
            action_id = action_id + 1
        
        # Draw from piles 
        mapping[action_id] = ("DRAW_STOCK", None)
        action_id = action_id + 1 
        mapping[action_id] = ("DRAW_DISCARD",None)
        action_id = action_id + 1
        
        # Replace card in grid 
        for i in range(GRID_SIZE): 
            mapping[action_id] = ("REPLACE",i)
            action_id = action_id + 1
            
        # Discard drawn card 
        mapping[action_id] = ("DISCARD_DRAWN", None) 
        action_id = action_id + 1
        
        # Flip card in grid
        for i in range(GRID_SIZE): 
            mapping[action_id] = ("FLIP", i)
            action_id = action_id + 1
            
        return mapping 
    
    def _get_action_from_id(self, action_id: int) -> Tuple[str, Optional[int]]: 
        """Retrieves action from action id"""
        # Action Mapping 
        # ---------------------------
        # 0-8: Flip initial cards
        # 9: Draw from stock pile
        # 10: Draw from discard pile
        # 11-19: Replace card in grid
        # 20: Discard drawn card
        # 21-29: Flip card in grid   
        if 0 <= action_id <= GRID_SIZE - 1: return("Initial_Flip",action_id)
        if action_id == 9: return ("DRAW_STOCK", None)
        if action_id == 10: return ("DRAW_DISCARD", None)
        if 11 <= action_id <= GRID_SIZE + 10: return("REPLACE",action_id-(GRID_SIZE + 2))
        if action_id == 20: return("DISCARD_DRAWN", None)
        if 21 <= action_id <= 29: return("FLIP",action_id - (2*GRID_SIZE+3))
        raise ValueError(f"Action ID {action_id} out of defined range.")

        
    def get_legal_actions(self, player_id: int) -> List[int] 
        """Returns a list of legal actions for the player""" 
        # Action Mapping 
        # ---------------------------
        # 0-8: Flip initial cards
        # 9: Draw from stock pile
        # 10: Draw from discard pile
        # 11-19: Replace card in grid
        # 20: Discard drawn card
        # 21-29: Flip card in grid   
      
        legal_action_ids = []
        player = self.players[player_id]
        
        # Initial flip phase 
        if self.current_phase == PHASE_INITIAL_FLIP: 
            if self.initial_flips_count[player_id] < 3: 
                for i in range(GRID_SIZE):
                    if player.is_face_up(i) == False: 
                        legal_actions.append(i)
                        
        # Player draws from stockpile or discard pile
        elif self.current_phase == PHASE_START_TURN: 
            if not self.deck.is_empty() or len(self.discard_pile) > 1: 
                legal_action_ids.append(9)
            if len(self.discard_pile) >= 1: 
                legal_action_ids.append(10)
        
        # Player drew from stock pile 
        elif self.current_phase == PHASE_DRAW_STOCK_DECISION:
            # Player can discard drawn card
            legal_action_ids.append(20) 
            # Player can replace card in grid
            for i in range(GRID_SIZE): 
                legal_action_ids.append(11 + i)
        
        # Player drew from discard pile, must replace card in grid 
        elif self.current_phase == PHASE_DRAW_DISCARD_DECISION: 
            for i in range(GRID_SIZE): 
                legal_action_ids.append(11 + i)
                
        # Player discarded drawn card from stock pile, must flip phase down card in grid 
        elif self.current_phase == PHASE_MUST_FLIP_CARD: 
            face_down_idx = player.get_face_down_cards()
            for i in face_down_idx: 
                legal_action_ids.append(21 + i)
        
        
        def get_observation(self, player_id: int) -> Dict[str, Any]: 
            """Generates observation for player"""
            # Get players 
            player = self.players[player_id]
            opponent_id = 1 - player_id 
            opponent = self.players[opponent_id] 
            
            # Own grid 
            own_grid_vis = [] # List index, rank, and suit 
            own_grid_invis = [] # List index
            for i in range(GRID_SIZE): 
                card = player.get_card(i)
                if player.is_face_up(i): 
                    own_grid_vis.append({'index': i, 'rank': card.rank, 'suit', card.suit})
                else: 
                    own_grid_invis.append(i)
            
            # Opponent grid 
            opponent_grid_vis = [] 
            opponent_grid_invis = [] 
            for i in range(GRID_SIZE): 
                card = opponent.get_card(i)
                if opponent.is_face_up(i): 
                    opponent_grid_vis.append({'index': i, 'rank': card.rank, 'suit', card.suit}) 
                else: 
                    opponend_grid_invis.append(i)
            
            # Top card in dispile deck 
            top_discard = self.discard_pile[-1]
            top_discard_info = {'rank': top_discard.rank, 'suit': self.top_discard.suit}
            
            # Drawn card 
            drawn_card_info = {'rank': self.drawn_card.rank, 'suit': self.drawn_card.suit}
            
            # Gather observation information 
            observation = {
                "player_id": player_id,
                "current_player": self.current_player,
                "turn_phase": self.current_phase,
                "initial_flips_done": self.initial_flips_count[player_id],
                "own_hand": {
                    "visible_cards": own_grid_vis,
                    "hidden_indices": own_grid_invis,
                },
                "opponent_hand": {
                     "visible_cards": opponent_grid_vis,
                     "hideen_indices": opponent_grid_invis
                },
                "discard_top": top_discard_info,
                "deck_size": len(self.deck),
                "drawn_card": drawn_card_info,
                "scores": self.scores, 
                "turn_count": self.turn_count,
                "is_final_turn": self.final_turn_player_idx == player_id # Is this player taking final turn?
            }

            return observation 