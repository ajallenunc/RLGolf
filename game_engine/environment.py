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
        self.round_over: bool = False
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
                self.players[p_idx].set_card(i,card,face_up = False)
                
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
        opponent_id = 1 - current_player_id
    
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
                self._reveal_all_cards(current_player_id)
                self._reveal_all_cards(opponent_id)

        elif self.final_turn_player_idx == current_player_id: 
            # Current player is playing their final turn 
            print(f"--- Player {current_player_id}'s final turn complete. Round over. ---")
            self.round_over = True
            self._reveal_all_cards(current_player_id)
            self._reveal_all_cards(opponent_id)
            
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

        
    def get_legal_actions(self, player_id: int) -> List[int]: 
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
                        legal_action_ids.append(i)
                        
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

        return legal_action_ids
        
        
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
                own_grid_vis.append({'index': i, 'rank': card.rank, 'suit': card.suit})
            else: 
                own_grid_invis.append(i)
        
        # Opponent grid 
        opponent_grid_vis = [] 
        opponent_grid_invis = [] 
        for i in range(GRID_SIZE): 
            card = opponent.get_card(i)
            if opponent.is_face_up(i): 
                opponent_grid_vis.append({'index': i, 'rank': card.rank, 'suit': card.suit}) 
            else: 
                opponent_grid_vis.append(i)
        
        # Top card in dispile deck           
        
        if self.discard_pile:  
            top_discard = self.discard_pile[-1]
            top_discard_info = {'rank': top_discard.rank, 'suit': top_discard.suit}
        else:
            top_discard_info = None
            top_discard = None
        
        # Drawn card 
        if self.drawn_card:
           drawn_card_info = {'rank': self.drawn_card.rank, 'suit': self.drawn_card.suit}
        else:
            drawn_card_info = None
        
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
            "deck_size": len(self.deck.cards),
            "drawn_card": drawn_card_info,
            "scores": self.scores, 
            "turn_count": self.turn_count,
            "is_final_turn": self.final_turn_player_idx == player_id # Is this player taking final turn?
        }

        return observation 


    def reset(self) -> Tuple[Dict[str, Any], Dict[str, Any]]: 
        """ Reset the environment for a new round """ 
        print("--- Resetting Environment ---")

        # Deck 
        self.deck = Deck(self.num_decks, self.num_jokers) 
        self.discard_pile = [] 
        self.drawn_card = None
    
        # Players
        self.players = [Player() for _ in range(self.num_players)]
        self.current_player = 0 
        self.turn_count = 0
        self.final_turn_player_idx = None 
    
        # Round keeping 
        self.initial_flips_count = [0]*self.num_players
        self.round_over = False
        self.game_over = False 
        self.scores = [0]*self.num_players
    
        # Deal and start the discard pile
        self._deal_initial_hands()
        self._start_discard_pile()
    
        # Start phase
        self.current_phasse = PHASE_INITIAL_FLIP
    
        # Return initial obss
        obs0 = self.get_observation(0)
        obs1 = self.get_observation(1)
    
        return obs0,obs1


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

    def step(self, action_id: int) -> Tuple[Dict[str, Any], Dict[str, Any], int, bool, Dict[str, Any]]:
        """ Execute action for current player""" 

        # Get player
        player_id = self.current_player
        player = self.players[player_id] 
        opponent_id = 1 - player_id
    
        # Get legal actions for player
        legal_acts = self.get_legal_actions(player_id)
        action_type, action_index = self._get_action_from_id(action_id)
        print(f"Step: P{player_id}, Phase:{self.current_phase}, Action:{action_type}, Idx:{action_index}") # Debug
    
        # Setup
        reward = 0
        info = {} 
    
        # --- Process action based on phase --- #
    
        # Player initially flips each card 
        if self.current_phase == PHASE_INITIAL_FLIP:
            # Flip card
            player.flip_card_up(action_index)
            self.initial_flips_count[player_id]  = self.initial_flips_count[player_id] + 1 
    
            # Player needs to flip 3 cards, so loop back if less than 3 cards flipped
            if self.initial_flips_count[player_id] == 3: 
                if player_id == 0: 
                    self.current_player = 1
                else: # Current player still needs to flip more 
                    self.current_player = 0
                    self.current_phase = PHASE_START_TURN 
    
        # Player chooses to draw from discard pile or stock 
        elif self.current_phase == PHASE_START_TURN:
            if action_type == "DRAW_STOCK": 
                self.drawn_card = self.deck.deal()
                self.current_phase = PHASE_DRAW_STOCK_DECISION
            elif action_type == "DRAW_DISCARD": 
                self.drawn_card = self.discard_pile.pop()
                self.current_phase = PHASE_DRAW_DISCARD_DECISION
    
        # If player draws from stock, they choose to replace card in grid or discard drawn card
        elif self.current_phase == PHASE_DRAW_STOCK_DECISION: 
            if action_type == "REPLACE": 
                # Player chooses to replace card in grid, take replaced card to discard pile
                replaced_card = player.get_card(action_index) 
                player.set_card(action_index, self.drawn_card, face_up = True)
                self.discard_pile.append(replaced_card)
                self.drawn_card = None
                # Advance round
                self._check_round_end_and_advance_player() 
            elif action_type == "DISCARD_DRAWN": 
                self.discard_pile.append(self.drawn_card)
                self.drawn_card = None
                self.current_phase = PHASE_MUST_FLIP_CARD       
    
        # If player draws from discard pile, they choose to replace card in grid or they must flip a card in the grid
        elif self.current_phase == PHASE_DRAW_DISCARD_DECISION: 
            if action_type == "REPLACE": 
                replaced_card = player.get_card(action_index)
                player.set_card(action_index, self.drawn_card, face_up = True)
                self.discard_pile.append(replaced_card)
                self.drawn_card = None
                
                # Advance round
                self._check_round_end_and_advance_player()
            else: 
                raise ValueError(f"Invalid action type {action_type} during PHASE_DRAW_DISCARD_DECISION")
    
        # Player must flip card in the grid 
        elif self.current_phase == PHASE_MUST_FLIP_CARD: 
            if action_type == "FLIP": 
                player.flip_card_up(action_index) 
                # Advance round
                self._check_round_end_and_advance_player()
            else: 
                raise ValueError(f"Invalid action type {action_type} during PHASE_MUST_FLIP_CARD")
    
    
        # --- After action processing and scoring --- #
    
        done = self.round_over or self.game_over 
    
        if done: 
            self._reveal_all_cards(0)
            self._reveal_all_cards(1)
    
            self.scores[0] = self.players[0].calculate_score()
            self.scores[1] = self.players[1].calculate_score() 
        
            # Determine winner 
            winner = -1 # Tie? 
            if self.scores[0] < self.scores[1]: winner = 0
            elif self.scores[1] < self.scores[0]: winner = 1
        
            info['round_winner'] = winner 
            info['final_scores'] = self.scores.copy() 
        
            # Calculate award
            current_player_score = self.scores[player_id]
            opponent_score = self.scores[opponent_id]
            reward = opponent_score - current_player_score
        
            # Final state
            self.game_over = True
            self.current_phase = PHASE_GAME_OVER
    
        # Updated observations
        obs0 = self.get_observation(0) 
        obs1 = self.get_observation(1) 
    
        return obs0, obs1, reward, done, info 
    
    def render(self, mode='human'):
        """Prints the current game state to the console."""
        if mode == 'human':
            print("\n" + "="*30)
            # Map phase number to name for readability
            phase_map = {
                PHASE_INITIAL_FLIP: "Initial Flip",
                PHASE_START_TURN: "Start Turn",
                PHASE_DRAW_STOCK_DECISION: "Decide Stock Draw",
                PHASE_DRAW_DISCARD_DECISION: "Decide Discard Draw",
                PHASE_MUST_FLIP_CARD: "Must Flip Card",
                PHASE_GAME_OVER: "Game Over"
            }
            phase_name = phase_map.get(self.current_phase, f"Unknown Phase ({self.current_phase})")

            print(f"Turn: {self.turn_count} | Player: {self.current_player} | Phase: {phase_name}")
            print(f"Deck Size: {len(self.deck.cards)}")
            top_discard = self.discard_pile[-1] if self.discard_pile else "Empty"
            print(f"Discard Top: {top_discard}")
            if self.drawn_card: print(f"Player {self.current_player} holding drawn card: {self.drawn_card}")

            # Print Player Hands (requires Player class __str__)
            for p_idx, player_obj in enumerate(self.players):
                flips = self.initial_flips_count[p_idx] if self.current_phase == PHASE_INITIAL_FLIP else 3
                print(f"\n--- Player {p_idx} Hand (Initial Flips: {flips}/3) ---")
                print(player_obj) # Relies on Player.__str__

                # Show scores only at the end
                if self.game_over or self.round_over:
                     # Ensure scores are calculated if rendering end state
                     if not self.scores[p_idx]: self.scores[p_idx] = player_obj.calculate_score()
                     print(f"Score: {self.scores[p_idx]}")


            # Print final results or legal actions
            if self.game_over or self.round_over:
                 print("="*30)
                 print(f"ROUND OVER. Final Scores: Player 0 = {self.scores[0]}, Player 1 = {self.scores[1]}")
                 winner = -1
                 if self.scores[0] < self.scores[1]: winner = 0
                 elif self.scores[1] < self.scores[0]: winner = 1
                 print(f"Winner: Player {winner}" if winner != -1 else "Tie")
                 print("="*30)
            else:
                 print("-"*30)
                 legal_acts = self.get_legal_actions(self.current_player)
                 print(f"Player {self.current_player} Legal Action IDs: {legal_acts}")
                 # Map actions to readable format for display
                 action_details = []
                 for aid in legal_acts:
                     try:
                         atype, aindex = self._get_action_from_id(aid)
                         action_details.append(f"{atype}{f'[{aindex}]' if aindex is not None else ''} ({aid})")
                     except ValueError:
                         action_details.append(f"Invalid({aid})")
                 print(f"Legal Actions: {', '.join(action_details)}")
                 if self.current_phase == PHASE_INITIAL_FLIP:
                     print(f"(Choose card index {self.initial_flips_count[self.current_player]+1}/3 to flip)")

        else:
            # For non-human modes, maybe return observations
            return self.get_observation(0), self.get_observation(1)



    
