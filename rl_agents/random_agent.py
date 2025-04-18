import random 
from typing import List, Dict, Any 

class RandomAgent: 
    """Agent that randomly chooses a legal action"""

    def act(self, legal_actions: List[int]) -> int: 

        # Debugging
        if not legal_actions: 
            raise ValueError("No legal actions available for RandomAgent to choose???)
        
        choose_action = random.choice(legal_actions)
        return choose_action