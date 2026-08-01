from typing import Protocol, List, Optional, Any, Dict
import pandas as pd

class DecisionEngine(Protocol):
    """
    Protocol defining the strategy for a decision analysis engine.
    Every algorithm (TOPSIS, PROMETHEE, Decision Theory, etc.) must implement this interface.
    """
    
    def analyze(
        self, 
        data: pd.DataFrame | Dict[str, Any], 
        weights: List[float], 
        max_bools: List[bool], 
        **kwargs: Any
    ) -> pd.Series | Dict[str, Any]:
        """
        Execute the decision analysis algorithm.
        
        Args:
            data: The decision matrix (crisp or fuzzy).
            weights: List of weights corresponding to each factor.
            max_bools: List of booleans indicating if a factor is to be maximized (True) or minimized (False).
            **kwargs: Additional parameters specific to the engine (e.g., preference types for PROMETHEE).
            
        Returns:
            A pandas Series containing the scores/rankings, or a Dictionary with detailed results.
        """
        ...
